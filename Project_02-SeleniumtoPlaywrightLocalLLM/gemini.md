# 📜 Project Constitution (gemini.md)

## 🏗️ Architectural Invariants
1. **Deterministic Logic**: Conversions should be predictable and repeatable.
2. **3-Layer Separation**: 
   - `architecture/` (SOPs)
   - `navigation/` (Logic)
   - `tools/` (Execution)
3. **Safety**: Never overwrite original Selenium files; output to new Playwright files or `.tmp/`.

## 🛠️ Behavioral Rules
1. **No Guessing**: If a Selenium pattern is ambiguous, flag it for user review rather than making a wrong conversion.
2. **Library Standard**: Default to Playwright `@playwright/test` library standards.
3. **Language Support**: Support both Javascript and Typescript.

## 📊 Data Schemas

### ConversionRequest
```json
{
  "sourceCode": "string",
  "sourceLanguage": "java",
  "targetLanguage": "javascript | typescript",
  "framework": "testng",
  "options": {
    "strictMapping": true
  }
}
```

### ConversionResponse
```json
{
  "convertedCode": "string",
  "outputPath": "string",
  "mappingDetails": [
    {
      "sourceLine": "number",
      "targetLine": "number",
      "description": "string"
    }
  ],
  "errors": []
}
```
