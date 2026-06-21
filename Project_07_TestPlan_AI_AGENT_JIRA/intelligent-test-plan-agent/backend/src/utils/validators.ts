export function validateJiraId(ticketId: string): boolean {
  const pattern = /^[A-Z][A-Z0-9]*-\d+$/;
  return pattern.test(ticketId.toUpperCase());
}

export function validateUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

export function validateTemperature(temp: number): boolean {
  return temp >= 0 && temp <= 1;
}

export function sanitizeJiraId(ticketId: string): string {
  return ticketId.toUpperCase().trim();
}
