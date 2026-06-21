import express from 'express';
import cors from 'cors';
import { convertSeleniumToPlaywright } from './navigation/converter_engine.js';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

app.post('/api/convert', async (req, res) => {
    const { sourceCode } = req.body;

    if (!sourceCode) {
        return res.status(400).json({ error: 'Source code is required' });
    }

    try {
        console.log("📥 Received conversion request...");
        const result = await convertSeleniumToPlaywright(sourceCode, 'converted_test.spec.ts');
        console.log("📤 Sending conversion response...");
        res.json({ convertedCode: result.convertedCode, outputPath: result.outputPath });
    } catch (error: any) {
        console.error("❌ Conversion failed:", error.message);
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 API Server running on http://localhost:${PORT}`);
});
