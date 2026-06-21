import Groq from 'groq-sdk';
import { SecureStorage } from '../secure-storage';
import { getDatabase } from '../../database/db';
import { LLMError } from '../../utils/errors';

export interface LLMConfig {
  apiKey: string;
  model: string;
  temperature: number;
}

export interface GenerationRequest {
  ticketData: any;
  templateText: string;
  systemPrompt: string;
}

export class GroqProvider {
  private client: Groq | null = null;
  private config: LLMConfig | null = null;

  async initialize(): Promise<void> {
    const db = getDatabase();
    const settings = db.prepare('SELECT * FROM settings WHERE id = 1').get() as any;
    
    const apiKey = await SecureStorage.getPassword(SecureStorage.ACCOUNTS.GROQ_KEY);
    
    if (!apiKey) {
      throw new LLMError('Groq API key not found. Please configure settings first.');
    }

    this.config = {
      apiKey,
      model: settings?.groq_model || 'openai/gpt-oss-120b',
      temperature: settings?.groq_temperature ?? 0.7,
    };

    this.client = new Groq({ apiKey: this.config.apiKey });
  }

  async testConnection(): Promise<{ success: boolean; message: string; models?: string[] }> {
    try {
      if (!this.client) {
        await this.initialize();
      }

      const models = [
        'openai/gpt-oss-120b',
        'openai/gpt-oss-20b',
        'llama-3.3-70b-versatile',
        'llama-3.1-70b-versatile',
        'llama-3.1-8b-instant', 
        'llama3-70b-8192',
        'llama3-8b-8192',
        'mixtral-8x7b-32768',
        'gemma2-9b-it'
      ];
      
      return {
        success: true,
        message: 'Groq API connection successful',
        models,
      };
    } catch (error: any) {
      console.error('Groq connection test failed:', error);
      return {
        success: false,
        message: error.message || 'Failed to connect to Groq API',
      };
    }
  }

  async generateTestPlan(request: GenerationRequest): Promise<string> {
    if (!this.client) {
      await this.initialize();
    }

    const { ticketData, templateText, systemPrompt } = request;
    const userPrompt = this.buildPrompt(ticketData, templateText);

    try {
      const completion = await this.client!.chat.completions.create({
        model: this.config!.model,
        temperature: this.config!.temperature,
        max_tokens: 4096,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
      });

      const content = completion.choices[0]?.message?.content;
      
      if (!content) {
        throw new LLMError('Empty response from Groq API');
      }

      return content;
    } catch (error: any) {
      console.error('Groq generation failed:', error);
      
      if (error.status === 401) {
        throw new LLMError('Invalid Groq API key', 401);
      }
      if (error.status === 429) {
        throw new LLMError('Rate limit exceeded. Please try again later.', 429);
      }
      
      throw new LLMError(error.message || 'Failed to generate test plan');
    }
  }

  async *streamTestPlan(request: GenerationRequest): AsyncGenerator<string> {
    if (!this.client) {
      await this.initialize();
    }

    const { ticketData, templateText, systemPrompt } = request;
    const userPrompt = this.buildPrompt(ticketData, templateText);

    try {
      const stream = await this.client!.chat.completions.create({
        model: this.config!.model,
        temperature: this.config!.temperature,
        max_tokens: 4096,
        stream: true,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
      });

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          yield content;
        }
      }
    } catch (error: any) {
      console.error('Groq streaming failed:', error);
      throw new LLMError(error.message || 'Failed to stream test plan');
    }
  }

  private buildPrompt(ticketData: any, templateText: string): string {
    return `Generate a comprehensive test plan for the following JIRA ticket, following the template structure provided.

## JIRA Ticket Information

**Ticket ID:** ${ticketData.key}
**Summary:** ${ticketData.summary}
**Priority:** ${ticketData.priority}
**Status:** ${ticketData.status}

**Description:**
${ticketData.description}

**Acceptance Criteria:**
${ticketData.acceptanceCriteria?.length > 0 
  ? ticketData.acceptanceCriteria.map((ac: string, i: number) => `${i + 1}. ${ac}`).join('\n')
  : 'No explicit acceptance criteria provided.'}

**Labels:** ${ticketData.labels?.join(', ') || 'None'}

## Template Structure to Follow

${templateText}

## Instructions

1. Maintain the template structure and headings
2. Map ticket details to appropriate sections
3. Create specific, actionable test cases based on acceptance criteria
4. Include edge cases and boundary conditions
5. Consider the priority level in test coverage
6. Write in professional QA language

Generate the complete test plan now:`;
  }
}
