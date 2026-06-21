import { Router } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { join } from 'path';
import { writeFileSync, readFileSync } from 'fs';
import { JiraClient } from '../services/jira-client';
import { GroqProvider } from '../services/llm-providers/groq-provider';
import { OllamaProvider } from '../services/llm-providers/ollama-provider';
import { runQuery, getQuery, allQuery } from '../database/db';
import { ValidationError } from '../utils/errors';
import { validateJiraId, sanitizeJiraId } from '../utils/validators';

const router = Router();

const SYSTEM_PROMPT = `You are an expert QA Engineer with years of experience in software testing. Your task is to generate comprehensive, professional test plans based on JIRA tickets and provided templates.

Guidelines:
1. Follow the template structure exactly, using the same headings and organization
2. Create specific, actionable test cases with clear steps and expected results
3. Map acceptance criteria directly to test scenarios
4. Include positive tests, negative tests, and edge cases
5. Consider the priority level when determining test depth
6. Use professional QA terminology and clear, concise language
7. Ensure each test case is traceable to a requirement
8. Include appropriate test data suggestions where relevant

Output format: Markdown`;

// Generate test plan
router.post('/generate', async (req, res, next) => {
  try {
    const { ticketId, templateId, provider: preferredProvider } = req.body;

    if (!ticketId) {
      throw new ValidationError('Missing required field: ticketId');
    }

    const sanitizedId = sanitizeJiraId(ticketId);
    if (!validateJiraId(sanitizedId)) {
      throw new ValidationError(`Invalid JIRA ticket ID: ${ticketId}`);
    }

    const startTime = Date.now();

    // Get settings
    const settings = await getQuery<any>('SELECT * FROM settings WHERE id = 1');
    const provider = preferredProvider || settings?.llm_provider || 'groq';

    // Fetch ticket
    const jira = new JiraClient();
    const ticket = await jira.fetchTicket(sanitizedId);

    // Get template
    const templateIdToUse = templateId || 'default-testplan';
    const template = await getQuery<any>('SELECT * FROM templates WHERE id = ?', [templateIdToUse]);

    if (!template) {
      throw new ValidationError('Template not found');
    }

    // Generate based on provider
    let content: string;
    let modelUsed: string;

    if (provider === 'groq') {
      const groq = new GroqProvider();
      content = await groq.generateTestPlan({
        ticketData: ticket,
        templateText: template.extracted_text,
        systemPrompt: SYSTEM_PROMPT,
      });
      modelUsed = settings?.groq_model || 'openai/gpt-oss-120b';
    } else {
      const ollama = new OllamaProvider();
      content = await ollama.generateTestPlan({
        ticketData: ticket,
        templateText: template.extracted_text,
        systemPrompt: SYSTEM_PROMPT,
      });
      modelUsed = settings?.ollama_model || 'llama3.1';
    }

    const generationTime = Date.now() - startTime;
    const wordCount = content.split(/\s+/).length;

    // Save to history
    const historyId = uuidv4();
    const contentPath = join(__dirname, '../../../data', `${historyId}.md`);
    writeFileSync(contentPath, content);

    await runQuery(`
      INSERT INTO generation_history 
      (id, ticket_id, ticket_summary, template_id, template_name, provider, model, 
       preview, full_content_path, word_count, generation_time_ms)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      historyId,
      ticket.key,
      ticket.summary,
      template.id,
      template.name,
      provider,
      modelUsed,
      content.substring(0, 500) + '...',
      contentPath,
      wordCount,
      generationTime
    ]);

    res.json({
      success: true,
      testPlan: {
        id: historyId,
        ticketId: ticket.key,
        ticketSummary: ticket.summary,
        templateName: template.name,
        provider,
        model: modelUsed,
        content,
        wordCount,
        generationTimeMs: generationTime,
      },
    });
  } catch (error) {
    next(error);
  }
});

// Stream generate test plan
router.get('/stream', async (req, res, next) => {
  try {
    const { ticketId, templateId, provider: preferredProvider } = req.query as any;

    if (!ticketId) {
      throw new ValidationError('Missing required field: ticketId');
    }

    const sanitizedId = sanitizeJiraId(ticketId);
    if (!validateJiraId(sanitizedId)) {
      throw new ValidationError(`Invalid JIRA ticket ID: ${ticketId}`);
    }

    const settings = await getQuery<any>('SELECT * FROM settings WHERE id = 1');
    const provider = preferredProvider || settings?.llm_provider || 'groq';

    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Fetch ticket and template
    const jira = new JiraClient();
    const ticket = await jira.fetchTicket(sanitizedId);

    const templateIdToUse = templateId || 'default-testplan';
    const template = await getQuery<any>('SELECT * FROM templates WHERE id = ?', [templateIdToUse]);

    if (!template) {
      throw new ValidationError('Template not found');
    }

    // Stream based on provider
    let generator: AsyncGenerator<string>;

    if (provider === 'groq') {
      const groq = new GroqProvider();
      generator = groq.streamTestPlan({
        ticketData: ticket,
        templateText: template.extracted_text,
        systemPrompt: SYSTEM_PROMPT,
      });
    } else {
      const ollama = new OllamaProvider();
      generator = ollama.streamTestPlan({
        ticketData: ticket,
        templateText: template.extracted_text,
        systemPrompt: SYSTEM_PROMPT,
      });
    }

    // Send chunks
    for await (const chunk of generator) {
      res.write(`data: ${JSON.stringify({ chunk })}\n\n`);
    }

    res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
    res.end();
  } catch (error) {
    next(error);
  }
});

// Get generation history
router.get('/history', async (req, res, next) => {
  try {
    const history = await allQuery<{
      id: string;
      ticket_id: string;
      ticket_summary: string;
      template_name: string;
      provider: string;
      model: string;
      generated_at: string;
      preview: string;
      word_count: number;
    }>(`
      SELECT 
        id, ticket_id as ticket_id, ticket_summary as ticket_summary,
        template_name as template_name, provider, model,
        generated_at as generated_at, preview, word_count as word_count
      FROM generation_history
      ORDER BY generated_at DESC
      LIMIT 50
    `);

    res.json({ 
      history: history.map(h => ({
        ...h,
        ticketId: h.ticket_id,
        ticketSummary: h.ticket_summary,
        templateName: h.template_name,
        generatedAt: h.generated_at,
        wordCount: h.word_count
      }))
    });
  } catch (error) {
    next(error);
  }
});

// Get single generation
router.get('/history/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    const history = await getQuery<{
      id: string;
      ticket_id: string;
      ticket_summary: string;
      template_name: string;
      provider: string;
      model: string;
      generated_at: string;
      full_content_path: string;
      word_count: number;
      generation_time_ms: number;
    }>(`
      SELECT 
        id, ticket_id as ticket_id, ticket_summary as ticket_summary,
        template_name as template_name, provider, model,
        generated_at as generated_at, full_content_path as full_content_path,
        word_count as word_count, generation_time_ms as generation_time_ms
      FROM generation_history
      WHERE id = ?
    `, [id]);

    if (!history) {
      throw new ValidationError('History entry not found');
    }

    const content = readFileSync(history.full_content_path, 'utf-8');

    res.json({
      history: {
        id: history.id,
        ticketId: history.ticket_id,
        ticketSummary: history.ticket_summary,
        templateName: history.template_name,
        provider: history.provider,
        model: history.model,
        generatedAt: history.generated_at,
        wordCount: history.word_count,
        generationTimeMs: history.generation_time_ms,
        content,
      },
    });
  } catch (error) {
    next(error);
  }
});

export default router;
