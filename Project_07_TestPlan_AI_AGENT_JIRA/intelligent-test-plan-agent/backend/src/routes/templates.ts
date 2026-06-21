import { Router } from 'express';
import multer from 'multer';
import { v4 as uuidv4 } from 'uuid';
import { join } from 'path';
import { runQuery, getQuery, allQuery } from '../database/db';
import { PDFParser } from '../services/pdf-parser';
import { ValidationError, TemplateError } from '../utils/errors';
import { mkdirSync, existsSync } from 'fs';

const router = Router();

// Ensure templates directory exists
const templatesDir = join(__dirname, '../../../templates');
if (!existsSync(templatesDir)) {
  mkdirSync(templatesDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, templatesDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}-${file.originalname}`;
    cb(null, uniqueName);
  },
});

const upload = multer({
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new ValidationError('Only PDF files are allowed'));
    }
  },
});

// List templates
router.get('/', async (req, res, next) => {
  try {
    const templates = await allQuery<{
      id: string;
      name: string;
      file_name: string;
      uploaded_at: string;
      is_default: number;
    }>(`
      SELECT id, name, file_name as file_name, uploaded_at as uploaded_at, is_default as is_default
      FROM templates
      ORDER BY is_default DESC, uploaded_at DESC
    `);

    res.json({ 
      templates: templates.map(t => ({
        ...t,
        isDefault: !!t.is_default
      }))
    });
  } catch (error) {
    next(error);
  }
});

// Get single template
router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    
    const template = await getQuery<{
      id: string;
      name: string;
      file_name: string;
      extracted_text: string;
      uploaded_at: string;
      is_default: number;
    }>(`
      SELECT id, name, file_name as file_name, extracted_text as extracted_text, 
             uploaded_at as uploaded_at, is_default as is_default
      FROM templates
      WHERE id = ?
    `, [id]);

    if (!template) {
      throw new TemplateError('Template not found');
    }

    res.json({ 
      template: {
        ...template,
        extractedText: template.extracted_text,
        isDefault: !!template.is_default
      }
    });
  } catch (error) {
    next(error);
  }
});

// Upload template
router.post('/upload', upload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) {
      throw new ValidationError('No file uploaded');
    }

    const { name } = req.body;
    const templateName = name || req.file.originalname.replace('.pdf', '');

    // Parse PDF
    const pdfParser = new PDFParser();
    const parsed = await pdfParser.parseFile(req.file.path);

    if (!parsed.text || parsed.text.trim().length === 0) {
      throw new TemplateError('Could not extract text from PDF. The file may be scanned or corrupted.');
    }

    // Save to database
    const id = uuidv4();

    await runQuery(
      'INSERT INTO templates (id, name, file_name, file_path, extracted_text, is_default) VALUES (?, ?, ?, ?, ?, 0)',
      [id, templateName, req.file.originalname, req.file.path, parsed.text]
    );

    res.json({
      success: true,
      template: {
        id,
        name: templateName,
        fileName: req.file.originalname,
        extractedText: parsed.text,
      },
    });
  } catch (error) {
    next(error);
  }
});

// Delete template
router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;

    // Don't allow deleting default template
    const template = await getQuery<{ is_default: number }>('SELECT is_default FROM templates WHERE id = ?', [id]);
    
    if (!template) {
      throw new TemplateError('Template not found');
    }

    if (template.is_default) {
      throw new TemplateError('Cannot delete the default template');
    }

    await runQuery('DELETE FROM templates WHERE id = ?', [id]);

    res.json({ success: true, message: 'Template deleted' });
  } catch (error) {
    next(error);
  }
});

export default router;
