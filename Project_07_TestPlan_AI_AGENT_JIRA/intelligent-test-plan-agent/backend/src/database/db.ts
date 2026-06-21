import sqlite3 from 'sqlite3';
import { readFileSync } from 'fs';
import { join } from 'path';
import { promisify } from 'util';

const DB_PATH = process.env.DATABASE_PATH || join(__dirname, '../../../data/app.db');

let db: sqlite3.Database | null = null;

export function getDatabase(): sqlite3.Database {
  if (!db) {
    db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        console.error('Error opening database:', err);
      } else {
        console.log('Database connected');
        initializeSchema();
      }
    });
  }
  return db;
}

function initializeSchema() {
  if (!db) return;
  
  const schemaPath = join(__dirname, 'schema.sql');
  const schema = readFileSync(schemaPath, 'utf-8');
  
  // Split schema by semicolons and execute each statement
  const statements = schema.split(';').filter(s => s.trim().length > 0);
  
  for (const statement of statements) {
    db!.run(statement + ';', (err) => {
      if (err) {
        // Ignore errors for existing tables
        console.log('Schema statement executed (may be duplicate)');
      }
    });
  }
  
  console.log('Database initialized successfully');
}

export function closeDatabase() {
  if (db) {
    db.close((err) => {
      if (err) {
        console.error('Error closing database:', err);
      }
    });
    db = null;
  }
}

// Helper to run queries with promises
export function runQuery(sql: string, params: any[] = []): Promise<sqlite3.RunResult> {
  const database = getDatabase();
  return new Promise((resolve, reject) => {
    database.run(sql, params, function(err) {
      if (err) reject(err);
      else resolve(this);
    });
  });
}

export function getQuery<T>(sql: string, params: any[] = []): Promise<T | undefined> {
  const database = getDatabase();
  return new Promise((resolve, reject) => {
    database.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row as T);
    });
  });
}

export function allQuery<T>(sql: string, params: any[] = []): Promise<T[]> {
  const database = getDatabase();
  return new Promise((resolve, reject) => {
    database.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows as T[]);
    });
  });
}
