import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

async function verifyConnectivity() {
    const baseEndpoint = 'http://localhost:11434';
    const tagsEndpoint = `${baseEndpoint}/api/tags`;
    console.log(`Checking connectivity to: ${tagsEndpoint}`);

    try {
        const response = await axios.get(tagsEndpoint);
        if (response.status === 200) {
            console.log('✅ Success: Local LLM is responding.');
            console.log('Available models:', JSON.stringify(response.data.models?.map((m: any) => m.name) || 'N/A'));
        } else {
            console.error(`❌ Error: LLM responded with status ${response.status}`);
        }
    } catch (error: any) {
        console.error('❌ Error: Could not connect to local LLM. Make sure Ollama or your LLM server is running.');
        console.error(error.message);
    }
}

verifyConnectivity();
