import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, FileText, ArrowLeft, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { testPlanApi } from '@/services/api';

interface HistoryItem {
  id: string;
  ticketId: string;
  ticketSummary: string;
  templateName: string;
  provider: string;
  model: string;
  generatedAt: string;
  preview: string;
  wordCount: number;
}

export default function History() {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<any>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await testPlanApi.getHistory();
      setHistory(data.history || []);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleView = async (id: string) => {
    try {
      const data = await testPlanApi.getHistoryItem(id);
      setSelectedItem(data.history);
    } catch (error: any) {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleDownload = (item: any) => {
    const blob = new Blob([item.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${item.ticketId}-testplan.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  if (selectedItem) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => setSelectedItem(null)}>
            <ArrowLeft className="h-4 w-4 mr-2" /> Back to History
          </Button>
          <h1 className="text-2xl font-bold">{selectedItem.ticketId}</h1>
          <Badge variant="outline">{selectedItem.provider}</Badge>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{selectedItem.ticketSummary}</CardTitle>
                <p className="text-sm text-slate-500 mt-1">
                  Generated on {formatDate(selectedItem.generatedAt)} using {selectedItem.model}
                </p>
              </div>
              <Button onClick={() => handleDownload(selectedItem)}>
                <Download className="h-4 w-4 mr-2" /> Download
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <pre className="bg-slate-900 text-slate-100 p-6 rounded-lg overflow-auto max-h-[600px] text-sm whitespace-pre-wrap">
              {selectedItem.content}
            </pre>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Generation History</h1>
        <p className="text-slate-500 mt-1">View previously generated test plans</p>
      </div>

      {history.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Clock className="h-12 w-12 mx-auto text-slate-300 mb-4" />
            <p className="text-slate-500">No test plans generated yet</p>
            <Button className="mt-4" onClick={() => navigate('/')}>Generate Your First Test Plan</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <Card 
              key={item.id} 
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => handleView(item.id)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="h-5 w-5 text-blue-500" />
                      <span className="font-semibold text-lg">{item.ticketId}</span>
                      <Badge variant="outline">{item.provider}</Badge>
                      <Badge variant="secondary">{item.wordCount} words</Badge>
                    </div>
                    <p className="text-slate-700 font-medium">{item.ticketSummary}</p>
                    <p className="text-sm text-slate-500 mt-1">Template: {item.templateName}</p>
                    <p className="text-xs text-slate-400 mt-2">{formatDate(item.generatedAt)}</p>
                  </div>
                  <Button variant="ghost" size="sm">
                    View
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
