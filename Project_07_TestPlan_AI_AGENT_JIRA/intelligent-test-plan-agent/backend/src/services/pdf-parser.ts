import pdfParse from 'pdf-parse';
import { readFileSync } from 'fs';
import { TemplateError } from '../utils/errors';

export interface ParsedPDF {
  text: string;
  pageCount: number;
  info: any;
}

export class PDFParser {
  async parseFile(filePath: string): Promise<ParsedPDF> {
    try {
      const dataBuffer = readFileSync(filePath);
      const result = await pdfParse(dataBuffer);

      return {
        text: result.text,
        pageCount: result.numpages,
        info: result.info,
      };
    } catch (error: any) {
      console.error('PDF parsing failed:', error);
      throw new TemplateError(`Failed to parse PDF: ${error.message}`);
    }
  }

  async parseBuffer(buffer: Buffer): Promise<ParsedPDF> {
    try {
      const result = await pdfParse(buffer);

      return {
        text: result.text,
        pageCount: result.numpages,
        info: result.info,
      };
    } catch (error: any) {
      console.error('PDF parsing failed:', error);
      throw new TemplateError(`Failed to parse PDF: ${error.message}`);
    }
  }

  // Extract structured sections from template text
  extractSections(text: string): string[] {
    const sections: string[] = [];
    
    // Match markdown headers
    const headerPattern = /^#{1,3}\s+(.+)$/gm;
    let match;
    
    while ((match = headerPattern.exec(text)) !== null) {
      sections.push(match[1].trim());
    }
    
    return sections;
  }
}
