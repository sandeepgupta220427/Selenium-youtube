import { Version3Client } from 'jira.js';
import { SecureStorage } from './secure-storage';
import { runQuery, getQuery, allQuery } from '../database/db';
import { JiraError } from '../utils/errors';

export interface JiraConfig {
  baseUrl: string;
  username: string;
  apiToken: string;
}

export interface TicketData {
  key: string;
  summary: string;
  description: string;
  priority: string;
  status: string;
  assignee: {
    email: string;
    displayName: string;
  } | null;
  labels: string[];
  acceptanceCriteria: string[];
  attachments: Array<{
    filename: string;
    contentType: string;
    size: number;
  }>;
  createdAt: string;
  updatedAt: string;
}

export class JiraClient {
  private client: Version3Client | null = null;
  private config: JiraConfig | null = null;

  async initialize(): Promise<void> {
    const settings = await getQuery<any>('SELECT * FROM settings WHERE id = 1');
    
    if (!settings?.jira_base_url || !settings?.jira_username) {
      throw new JiraError('JIRA configuration not found. Please configure settings first.');
    }

    const apiToken = await SecureStorage.getPassword(SecureStorage.ACCOUNTS.JIRA_TOKEN);
    
    if (!apiToken) {
      throw new JiraError('JIRA API token not found. Please configure settings first.');
    }

    this.config = {
      baseUrl: settings.jira_base_url,
      username: settings.jira_username,
      apiToken,
    };

    this.client = new Version3Client({
      host: this.config.baseUrl,
      authentication: {
        basic: {
          email: this.config.username,
          apiToken: this.config.apiToken,
        },
      },
    });
  }

  async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      if (!this.client) {
        await this.initialize();
      }

      const myself = await this.client!.myself.getCurrentUser();
      
      return {
        success: true,
        message: `Connected as ${myself.displayName} (${myself.emailAddress})`,
      };
    } catch (error: any) {
      console.error('JIRA connection test failed:', error);
      return {
        success: false,
        message: error.message || 'Failed to connect to JIRA',
      };
    }
  }

  async fetchTicket(ticketId: string): Promise<TicketData> {
    if (!this.client) {
      await this.initialize();
    }

    try {
      const issue = await this.client!.issues.getIssue({
        issueIdOrKey: ticketId,
        expand: 'renderedFields',
      });

      // Parse acceptance criteria from description
      const acceptanceCriteria = this.extractAcceptanceCriteria(
        issue.fields.description || ''
      );

      const ticketData: TicketData = {
        key: issue.key,
        summary: issue.fields.summary || '',
        description: this.formatDescription(issue.fields.description),
        priority: issue.fields.priority?.name || 'Unknown',
        status: issue.fields.status?.name || 'Unknown',
        assignee: issue.fields.assignee ? {
          email: issue.fields.assignee.emailAddress || '',
          displayName: issue.fields.assignee.displayName || '',
        } : null,
        labels: issue.fields.labels || [],
        acceptanceCriteria,
        attachments: (issue.fields.attachment || []).map(att => ({
          filename: att.filename || '',
          contentType: att.mimeType || '',
          size: att.size || 0,
        })),
        createdAt: issue.fields.created || '',
        updatedAt: issue.fields.updated || '',
      };

      // Save to recent tickets
      this.saveToRecentTickets(ticketData);

      return ticketData;
    } catch (error: any) {
      console.error('Failed to fetch ticket:', error);
      
      if (error.response?.status === 404) {
        throw new JiraError(`Ticket ${ticketId} not found`, 404);
      }
      if (error.response?.status === 401) {
        throw new JiraError('Authentication failed. Check your JIRA credentials.', 401);
      }
      
      throw new JiraError(error.message || 'Failed to fetch ticket from JIRA');
    }
  }

  private extractAcceptanceCriteria(description: any): string[] {
    if (!description) return [];
    
    const text = typeof description === 'string' 
      ? description 
      : JSON.stringify(description);
    
    // Look for common acceptance criteria patterns
    const patterns = [
      /acceptance criteria:?\s*([\s\S]*?)(?=\n\n|\n##|$)/i,
      /given[\s\S]*?when[\s\S]*?then/gi,
    ];
    
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        // Split by bullet points or numbers
        const criteria = match[1] || match[0];
        return criteria
          .split(/\n\s*[-•*]\s*|\n\s*\d+\.\s*/)
          .map(s => s.trim())
          .filter(s => s.length > 0 && s.length < 500);
      }
    }
    
    return [];
  }

  private formatDescription(description: any): string {
    if (!description) return '';
    
    // Handle Atlassian Document Format (ADF)
    if (typeof description === 'object') {
      return this.extractTextFromADF(description);
    }
    
    return String(description);
  }

  private extractTextFromADF(doc: any): string {
    if (!doc) return '';
    
    if (typeof doc === 'string') return doc;
    
    if (doc.type === 'text') {
      return doc.text || '';
    }
    
    if (doc.content && Array.isArray(doc.content)) {
      return doc.content.map((child: any) => this.extractTextFromADF(child)).join(' ');
    }
    
    return '';
  }

  private async saveToRecentTickets(ticket: TicketData): Promise<void> {
    try {
      await runQuery(`
        INSERT OR REPLACE INTO recent_tickets (ticket_id, ticket_summary, ticket_data, fetched_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
      `, [
        ticket.key,
        ticket.summary,
        JSON.stringify(ticket)
      ]);
      
      // Keep only last 10 tickets
      await runQuery(`
        DELETE FROM recent_tickets 
        WHERE ticket_id NOT IN (
          SELECT ticket_id FROM recent_tickets 
          ORDER BY fetched_at DESC 
          LIMIT 10
        )
      `);
    } catch (error) {
      console.error('Failed to save recent ticket:', error);
    }
  }

  async getRecentTickets(): Promise<Array<{ ticketId: string; ticketSummary: string; fetchedAt: string }>> {
    const rows = await allQuery<{
      ticket_id: string;
      ticket_summary: string;
      fetched_at: string;
    }>(`
      SELECT ticket_id, ticket_summary, fetched_at 
      FROM recent_tickets 
      ORDER BY fetched_at DESC 
      LIMIT 5
    `);
    
    return rows.map(row => ({
      ticketId: row.ticket_id,
      ticketSummary: row.ticket_summary,
      fetchedAt: row.fetched_at,
    }));
  }
}
