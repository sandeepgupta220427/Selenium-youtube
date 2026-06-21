import { Router } from 'express';
import { getDatabase, getQuery, runQuery } from '../database/db';
import { SecureStorage } from '../services/secure-storage';
import { JiraClient } from '../services/jira-client';
import { GroqProvider } from '../services/llm-providers/groq-provider';
import { OllamaProvider } from '../services/llm-providers/ollama-provider';
import { validateUrl } from '../utils/validators';
import { ValidationError } from '../utils/errors';

const router = Router();

// Get settings
router.get('/', async (req, res, next) => {
  try {
    const settings = await getQuery<any>('SELECT * FROM settings WHERE id = 1');

    // Don't send sensitive data
    res.json({
      jira: {
        baseUrl: settings?.jira_base_url || '',
        username: settings?.jira_username || '',
      },
      llm: {
        provider: settings?.llm_provider || 'groq',
        groq: {
          model: settings?.groq_model || 'openai/gpt-oss-120b',
          temperature: settings?.groq_temperature ?? 0.7,
        },
        ollama: {
          baseUrl: settings?.ollama_base_url || 'http://localhost:11434',
          model: settings?.ollama_model || 'llama3.1',
        },
      },
    });
  } catch (error) {
    next(error);
  }
});

// Save JIRA settings
router.post('/jira', async (req, res, next) => {
  try {
    const { baseUrl, username, apiToken } = req.body;

    if (!baseUrl || !username || !apiToken) {
      throw new ValidationError('Missing required fields: baseUrl, username, apiToken');
    }

    if (!validateUrl(baseUrl)) {
      throw new ValidationError('Invalid JIRA base URL. Must be a valid HTTPS URL.');
    }

    await runQuery(
      'UPDATE settings SET jira_base_url = ?, jira_username = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1',
      [baseUrl, username]
    );

    // Store API token securely
    await SecureStorage.setPassword(SecureStorage.ACCOUNTS.JIRA_TOKEN, apiToken);

    res.json({ success: true, message: 'JIRA settings saved' });
  } catch (error) {
    next(error);
  }
});

// Save LLM settings
router.post('/llm', async (req, res, next) => {
  try {
    const { provider, groq, ollama } = req.body;

    if (!provider || !['groq', 'ollama'].includes(provider)) {
      throw new ValidationError('Invalid provider. Must be "groq" or "ollama"');
    }

    if (provider === 'groq') {
      if (groq?.apiKey) {
        await SecureStorage.setPassword(SecureStorage.ACCOUNTS.GROQ_KEY, groq.apiKey);
      }
      
      await runQuery(
        'UPDATE settings SET llm_provider = ?, groq_model = ?, groq_temperature = ? WHERE id = 1',
        [provider, groq?.model || 'openai/gpt-oss-120b', groq?.temperature ?? 0.7]
      );
    } else {
      await runQuery(
        'UPDATE settings SET llm_provider = ?, ollama_base_url = ?, ollama_model = ? WHERE id = 1',
        [provider, ollama?.baseUrl || 'http://localhost:11434', ollama?.model || 'llama3.1']
      );
    }

    res.json({ success: true, message: 'LLM settings saved' });
  } catch (error) {
    next(error);
  }
});

// Test JIRA connection
router.get('/jira/test', async (req, res, next) => {
  try {
    const jira = new JiraClient();
    const result = await jira.testConnection();
    res.json(result);
  } catch (error) {
    next(error);
  }
});

// Test Groq connection
router.get('/llm/groq/test', async (req, res, next) => {
  try {
    const groq = new GroqProvider();
    const result = await groq.testConnection();
    res.json(result);
  } catch (error) {
    next(error);
  }
});

// Test Ollama connection
router.get('/llm/ollama/test', async (req, res, next) => {
  try {
    const ollama = new OllamaProvider();
    const result = await ollama.testConnection();
    res.json(result);
  } catch (error) {
    next(error);
  }
});

// Get available Ollama models
router.get('/llm/ollama/models', async (req, res, next) => {
  try {
    const ollama = new OllamaProvider();
    const result = await ollama.testConnection();
    res.json({ models: result.models || [] });
  } catch (error) {
    next(error);
  }
});

export default router;
