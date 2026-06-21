import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const OLLAMA_ENDPOINT = process.env.LLM_ENDPOINT || 'http://localhost:11434/api/generate';
const MODEL = process.env.LLM_MODEL || 'codellama';

export async function promptLLM(prompt: string, systemMessage?: string): Promise<string> {
    try {
        const response = await axios.post(OLLAMA_ENDPOINT, {
            model: MODEL,
            prompt: prompt,
            system: systemMessage,
            stream: false,
            options: {
                temperature: 0.1, // Low temperature for deterministic mapping
            }
        });

        return response.data.response;
    } catch (error: any) {
        console.error('LLM Request Error:', error.message);
        throw new Error(`Failed to communicate with Ollama: ${error.message}`);
    }
}
