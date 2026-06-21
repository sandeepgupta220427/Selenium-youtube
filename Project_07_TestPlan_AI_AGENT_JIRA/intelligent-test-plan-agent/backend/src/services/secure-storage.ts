import keytar from 'keytar';

const SERVICE_NAME = 'test-plan-agent';

export class SecureStorage {
  static async setPassword(account: string, password: string): Promise<void> {
    await keytar.setPassword(SERVICE_NAME, account, password);
  }

  static async getPassword(account: string): Promise<string | null> {
    return await keytar.getPassword(SERVICE_NAME, account);
  }

  static async deletePassword(account: string): Promise<boolean> {
    return await keytar.deletePassword(SERVICE_NAME, account);
  }

  // Account names for different credentials
  static readonly ACCOUNTS = {
    JIRA_TOKEN: 'jira-api-token',
    GROQ_KEY: 'groq-api-key',
  } as const;
}
