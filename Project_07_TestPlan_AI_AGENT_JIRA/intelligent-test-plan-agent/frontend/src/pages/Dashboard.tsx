import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Search, Loader2, FileText, Download, Copy, History, 
  Sparkles, CheckCircle, AlertCircle, Clock 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { jiraApi, templatesApi, testPlanApi } from '@/services/api';

interface Ticket {
  key: string;
  summary: string;
  description: string;
  priority: string;
  status: string;
  assignee: { email: string; displayName: string } | null;
  labels: string[];
  acceptanceCriteria: string[];
}

interface Template {
  id: string;
  name: string;
}

export default function Dashboard() {
  const { toast } = useToast();
  const [ticketId, setTicketId] = useState('');
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState('default-testplan');
  const [recentTickets, setRecentTickets] = useState<Array<{ ticketId: string; ticketSummary: string }>>([]);
  
  const [isFetching, setIsFetching] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [testPlan, setTestPlan] = useState<string | null>(null);
  const [generationStats, setGenerationStats] = useState<any>(null);

  useEffect(() => {
    loadTemplates();
    loadRecentTickets();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await templatesApi.list();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const loadRecentTickets = async () => {
    try {
      const data = await jiraApi.getRecent();
      setRecentTickets(data.tickets || []);
    } catch (error) {
      console.error('Failed to load recent tickets:', error);
    }
  };

  const handleFetchTicket = async () => {
    if (!ticketId.trim()) {
      toast({ title: 'Error', description: 'Please enter a ticket ID', variant: 'destructive' });
      return;
    }

    setIsFetching(true);
    setTicket(null);
    setTestPlan(null);

    try {
      const data = await jiraApi.fetchTicket(ticketId);
      setTicket(data.ticket);
      toast({ title: 'Success', description: `Fetched ${data.ticket.key}` });
      loadRecentTickets();
    } catch (error: any) {
      toast({ 
        title: 'Error', 
        description: error.message || 'Failed to fetch ticket', 
        variant: 'destructive' 
      });
    } finally {
      setIsFetching(false);
    }
  };

  const handleGenerate = async () => {
    if (!ticket) {
      toast({ title: 'Error', description: 'Please fetch a ticket first', variant: 'destructive' });
      return;
    }

    setIsGenerating(true);
    setTestPlan(null);

    try {
      const data = await testPlanApi.generate({
        ticketId: ticket.key,
        templateId: selectedTemplate,
      });
      setTestPlan(data.testPlan.content);
      setGenerationStats({
        wordCount: data.testPlan.wordCount,
        generationTime: data.testPlan.generationTimeMs,
        provider: data.testPlan.provider,
        model: data.testPlan.model,
      });
      toast({ title: 'Success', description: 'Test plan generated!' });
    } catch (error: any) {
      toast({ 
        title: 'Error', 
        description: error.message || 'Failed to generate test plan', 
        variant: 'destructive' 
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    if (testPlan) {
      navigator.clipboard.writeText(testPlan);
      toast({ title: 'Copied', description: 'Test plan copied to clipboard' });
    }
  };

  const handleDownload = () => {
    if (testPlan) {
      const blob = new Blob([testPlan], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${ticket?.key || 'test-plan'}.md`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'highest':
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low':
      case 'lowest': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Generate Test Plan</h1>
        <p className="text-slate-500 mt-1">Enter a JIRA ticket ID to generate a comprehensive test plan</p>
      </div>

      {/* Step 1: Ticket Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold">1</span>
            Ticket Input
          </CardTitle>
          <CardDescription>Enter the JIRA ticket ID you want to generate a test plan for</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              placeholder="e.g., VWO-123"
              value={ticketId}
              onChange={(e) => setTicketId(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleFetchTicket()}
              className="flex-1"
            />
            <Button onClick={handleFetchTicket} disabled={isFetching}>
              {isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              <span className="ml-2">Fetch Ticket</span>
            </Button>
          </div>

          {recentTickets.length > 0 && (
            <div className="flex items-center gap-2 text-sm">
              <History className="h-4 w-4 text-slate-400" />
              <span className="text-slate-500">Recent:</span>
              {recentTickets.slice(0, 5).map((t) => (
                <button
                  key={t.ticketId}
                  onClick={() => { setTicketId(t.ticketId); }}
                  className="text-blue-600 hover:underline"
                >
                  {t.ticketId}
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Step 2: Ticket Display */}
      {ticket && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold">2</span>
              Ticket Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-semibold">{ticket.key}: {ticket.summary}</h3>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant={getPriorityColor(ticket.priority) as any}>{ticket.priority}</Badge>
                  <Badge variant="outline">{ticket.status}</Badge>
                  {ticket.labels.map((label) => (
                    <Badge key={label} variant="secondary" className="text-xs">{label}</Badge>
                  ))}
                </div>
              </div>
              {ticket.assignee && (
                <div className="text-right text-sm text-slate-500">
                  <p>Assignee</p>
                  <p className="font-medium text-slate-700">{ticket.assignee.displayName}</p>
                </div>
              )}
            </div>

            <div className="bg-slate-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Description</h4>
              <p className="text-sm text-slate-600 whitespace-pre-wrap">{ticket.description}</p>
            </div>

            {ticket.acceptanceCriteria.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2">Acceptance Criteria</h4>
                <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                  {ticket.acceptanceCriteria.map((ac, i) => (
                    <li key={i}>{ac}</li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 3: Generation Controls */}
      {ticket && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="bg-blue-100 text-blue-600 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold">3</span>
              Generation Options
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Template</label>
                <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((t) => (
                      <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="pt-6">
                <Button 
                  onClick={handleGenerate} 
                  disabled={isGenerating}
                  size="lg"
                  className="bg-gradient-to-r from-blue-600 to-indigo-600"
                >
                  {isGenerating ? (
                    <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Generating...</>
                  ) : (
                    <><Sparkles className="h-4 w-4 mr-2" /> Generate Test Plan</>
                  )}
                </Button>
              </div>
            </div>

            {isGenerating && (
              <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg">
                <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                <div>
                  <p className="font-medium text-blue-900">Generating test plan...</p>
                  <p className="text-sm text-blue-700">This may take 10-30 seconds depending on the LLM provider</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 4: Output */}
      {testPlan && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <span className="bg-green-100 text-green-600 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold">4</span>
                Generated Test Plan
              </CardTitle>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleCopy}>
                  <Copy className="h-4 w-4 mr-2" /> Copy
                </Button>
                <Button variant="outline" size="sm" onClick={handleDownload}>
                  <Download className="h-4 w-4 mr-2" /> Download
                </Button>
              </div>
            </div>
            {generationStats && (
              <div className="flex items-center gap-4 text-sm text-slate-500 mt-2">
                <span className="flex items-center gap-1">
                  <FileText className="h-4 w-4" />
                  {generationStats.wordCount} words
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {(generationStats.generationTime / 1000).toFixed(1)}s
                </span>
                <span className="flex items-center gap-1">
                  <CheckCircle className="h-4 w-4" />
                  {generationStats.provider} ({generationStats.model})
                </span>
              </div>
            )}
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="preview">
              <TabsList>
                <TabsTrigger value="preview">Preview</TabsTrigger>
                <TabsTrigger value="raw">Raw Markdown</TabsTrigger>
              </TabsList>
              <TabsContent value="preview">
                <div className="prose prose-slate max-w-none bg-white p-6 rounded-lg border">
                  <ReactMarkdown>{testPlan}</ReactMarkdown>
                </div>
              </TabsContent>
              <TabsContent value="raw">
                <pre className="bg-slate-900 text-slate-100 p-6 rounded-lg overflow-auto max-h-[600px] text-sm">
                  {testPlan}
                </pre>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
