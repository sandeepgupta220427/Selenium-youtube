export class AppError extends Error {
  constructor(
    message: string,
    public statusCode: number = 500,
    public code: string = 'INTERNAL_ERROR'
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 400, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
  }
}

export class JiraError extends AppError {
  constructor(message: string, statusCode: number = 500) {
    super(message, statusCode, 'JIRA_ERROR');
    this.name = 'JiraError';
  }
}

export class LLMError extends AppError {
  constructor(message: string, statusCode: number = 500) {
    super(message, statusCode, 'LLM_ERROR');
    this.name = 'LLMError';
  }
}

export class TemplateError extends AppError {
  constructor(message: string) {
    super(message, 400, 'TEMPLATE_ERROR');
    this.name = 'TemplateError';
  }
}
