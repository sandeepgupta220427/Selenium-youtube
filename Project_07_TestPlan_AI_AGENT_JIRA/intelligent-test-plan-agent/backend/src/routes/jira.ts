import { Router } from 'express';
import { JiraClient } from '../services/jira-client';
import { validateJiraId, sanitizeJiraId } from '../utils/validators';
import { ValidationError } from '../utils/errors';

const router = Router();

// Fetch ticket
router.post('/fetch', async (req, res, next) => {
  try {
    const { ticketId } = req.body;

    if (!ticketId) {
      throw new ValidationError('Missing required field: ticketId');
    }

    const sanitizedId = sanitizeJiraId(ticketId);

    if (!validateJiraId(sanitizedId)) {
      throw new ValidationError(`Invalid JIRA ticket ID format: ${ticketId}. Expected format: PROJECT-123`);
    }

    const jira = new JiraClient();
    const ticket = await jira.fetchTicket(sanitizedId);

    res.json({
      success: true,
      ticket,
    });
  } catch (error) {
    next(error);
  }
});

// Get recent tickets
router.get('/recent', async (req, res, next) => {
  try {
    const jira = new JiraClient();
    const tickets = await jira.getRecentTickets();
    res.json({ tickets });
  } catch (error) {
    next(error);
  }
});

export default router;
