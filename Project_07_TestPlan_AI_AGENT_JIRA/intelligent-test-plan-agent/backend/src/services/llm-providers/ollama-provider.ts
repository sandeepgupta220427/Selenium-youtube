import ollama from 'ollama';
import { getDatabase } from '../../database/db';
import { LLMError } from '../../utils/errors';

export interface OllamaConfig {
  baseUrl: string;
  model: string;
}

export interface GenerationRequest {
  ticketData: any;
  templateText: string;
  systemPrompt: string;
}

export class OllamaProvider {
  private config: OllamaConfig | null = null;

  async initialize(): Promise<void> {
    const db = getDatabase();
    const settings = db.prepare('SELECT * FROM settings WHERE id = 1').get() as any;

    this.config = {
      baseUrl: settings?.ollama_base_url || 'http://localhost:11434',
      model: settings?.ollama_model || 'llama3.1',
    };

    process.env.OLLAMA_HOST = this.config.baseUrl;
  }

  async testConnection(): Promise<{ success: boolean; message: string; models?: string[] }> {
    try {
      if (!this.config) {
        await this.initialize();
      }

      const response = await fetch(`${this.config!.baseUrl}/api/tags`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const models = data.models?.map((m: any) => m.name) || [];

      return {
        success: true,
        message: `Ollama connection successful. Found ${models.length} models.`,
        models,
      };
    } catch (error: any) {
      console.error('Ollama connection test failed:', error);
      return {
        success: false,
        message: error.message || 'Failed to connect to Ollama. Make sure Ollama is running.',
      };
    }
  }

  async generateTestPlan(request: GenerationRequest): Promise<string> {
    if (!this.config) {
      await this.initialize();
    }

    const { ticketData, templateText, systemPrompt } = request;
    const userPrompt = this.buildPrompt(ticketData, templateText);

    try {
      const response = await ollama.generate({
        model: this.config!.model,
        system: systemPrompt,
        prompt: userPrompt,
        options: {
          temperature: 0.7,
          num_predict: 4096,
        },
      });

      return response.response;
    } catch (error: any) {
      console.error('Ollama generation failed:', error);
      
      if (error.message?.includes('connection refused')) {
        throw new LLMError('Cannot connect to Ollama. Make sure it is running on the configured port.', 503);
      }
      if (error.message?.includes('not found')) {
        throw new LLMError(`Model "${this.config!.model}" not found. Run: ollama pull ${this.config!.model}`, 404);
      }
      
      throw new LLMError(error.message || 'Failed to generate test plan with Ollama');
    }
  }

  async *streamTestPlan(request: GenerationRequest): AsyncGenerator<string> {
    if (!this.config) {
      await this.initialize();
    }

    const { ticketData, templateText, systemPrompt } = request;
    const userPrompt = this.buildPrompt(ticketData, templateText);

    try {
      const stream = await ollama.generate({
        model: this.config!.model,
        system: systemPrompt,
        prompt: userPrompt,
        options: {
          temperature: 0.7,
          num_predict: 4096,
        },
        stream: true,
      });

      for await (const chunk of stream) {
        if (chunk.response) {
          yield chunk.response;
        }
      }
    } catch (error: any) {
      console.error('Ollama streaming failed:', error);
      throw new LLMError(error.message || 'Failed to stream test plan from Ollama');
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
