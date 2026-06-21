import { useState, useEffect } from 'react';
import { 
  Save, CheckCircle, XCircle, Loader2, Server, Brain, 
  FileText, Upload, Trash2, AlertCircle 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { settingsApi, templatesApi } from '@/services/api';

export default function Settings() {
  const { toast } = useToast();
  
  // JIRA State
  const [jiraUrl, setJiraUrl] = useState('');
  const [jiraUsername, setJiraUsername] = useState('');
  const [jiraToken, setJiraToken] = useState('');
  const [jiraStatus, setJiraStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');

  // LLM State
  const [useLocalLLM, setUseLocalLLM] = useState(false);
  const [groqKey, setGroqKey] = useState('');
  const [groqModel, setGroqModel] = useState('openai/gpt-oss-120b');
  const [temperature, setTemperature] = useState(0.7);
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('llama3.1');
  const [ollamaModels, setOllamaModels] = useState<string[]>([]);
  const [groqStatus, setGroqStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [ollamaStatus, setOllamaStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');

  // Templates State
  const [templates, setTemplates] = useState<Array<{ id: string; name: string; isDefault: boolean }>>([]);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState('');

  useEffect(() => {
    loadSettings();
    loadTemplates();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await settingsApi.get();
      if (data.jira) {
        setJiraUrl(data.jira.baseUrl || '');
        setJiraUsername(data.jira.username || '');
      }
      if (data.llm) {
        setUseLocalLLM(data.llm.provider === 'ollama');
        setGroqModel(data.llm.groq?.model || 'llama3-70b-8192');
        setTemperature(data.llm.groq?.temperature ?? 0.7);
        setOllamaUrl(data.llm.ollama?.baseUrl || 'http://localhost:11434');
        setOllamaModel(data.llm.ollama?.model || 'llama3.1');
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const data = await templatesApi.list();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleSaveJira = async () => {
    try {
      await settingsApi.saveJira({
        baseUrl: jiraUrl,
        username: jiraUsername,
        apiToken: jiraToken,
      });
      toast({ title: 'Success', description: 'JIRA settings saved' });
      setJiraToken(''); // Clear token from UI
    } catch (error: any) {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleTestJira = async () => {
    setJiraStatus('testing');
    try {
      const result = await settingsApi.testJira();
      if (result.success) {
        setJiraStatus('success');
        toast({ title: 'Connected', description: result.message });
      } else {
        setJiraStatus('error');
        toast({ title: 'Connection Failed', description: result.message, variant: 'destructive' });
      }
    } catch (error: any) {
      setJiraStatus('error');
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleSaveLLM = async () => {
    try {
      await settingsApi.saveLLM({
        provider: useLocalLLM ? 'ollama' : 'groq',
        groq: {
          apiKey: groqKey,
          model: groqModel,
          temperature,
        },
        ollama: {
          baseUrl: ollamaUrl,
          model: ollamaModel,
        },
      });
      toast({ title: 'Success', description: 'LLM settings saved' });
      setGroqKey(''); // Clear key from UI
    } catch (error: any) {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleTestGroq = async () => {
    setGroqStatus('testing');
    try {
      const result = await settingsApi.testGroq();
      if (result.success) {
        setGroqStatus('success');
        toast({ title: 'Connected', description: result.message });
      } else {
        setGroqStatus('error');
        toast({ title: 'Connection Failed', description: result.message, variant: 'destructive' });
      }
    } catch (error: any) {
      setGroqStatus('error');
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleTestOllama = async () => {
    setOllamaStatus('testing');
    try {
      const result = await settingsApi.testOllama();
      if (result.success) {
        setOllamaStatus('success');
        setOllamaModels(result.models || []);
        toast({ title: 'Connected', description: result.message });
      } else {
        setOllamaStatus('error');
        toast({ title: 'Connection Failed', description: result.message, variant: 'destructive' });
      }
    } catch (error: any) {
      setOllamaStatus('error');
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleUploadTemplate = async () => {
    if (!uploadFile || !uploadName) {
      toast({ title: 'Error', description: 'Please select a file and enter a name', variant: 'destructive' });
      return;
    }

    try {
      await templatesApi.upload(uploadFile, uploadName);
      toast({ title: 'Success', description: 'Template uploaded' });
      setUploadFile(null);
      setUploadName('');
      loadTemplates();
    } catch (error: any) {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    try {
      await templatesApi.delete(id);
      toast({ title: 'Success', description: 'Template deleted' });
      loadTemplates();
    } catch (error: any) {
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'testing': return <Loader2 className="h-4 w-4 animate-spin" />;
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 mt-1">Configure integrations and templates</p>
      </div>

      <Tabs defaultValue="jira" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
          <TabsTrigger value="jira"><Server className="h-4 w-4 mr-2" /> JIRA</TabsTrigger>
          <TabsTrigger value="llm"><Brain className="h-4 w-4 mr-2" /> LLM</TabsTrigger>
          <TabsTrigger value="templates"><FileText className="h-4 w-4 mr-2" /> Templates</TabsTrigger>
        </TabsList>

        {/* JIRA Settings */}
        <TabsContent value="jira">
          <Card>
            <CardHeader>
              <CardTitle>JIRA Configuration</CardTitle>
              <CardDescription>Connect to your JIRA instance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="jira-url">Base URL</Label>
                <Input
                  id="jira-url"
                  placeholder="https://your-domain.atlassian.net"
                  value={jiraUrl}
                  onChange={(e) => setJiraUrl(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="jira-username">Username / Email</Label>
                <Input
                  id="jira-username"
                  placeholder="user@example.com"
                  value={jiraUsername}
                  onChange={(e) => setJiraUsername(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="jira-token">API Token {jiraStatus === 'success' && <Badge variant="outline" className="ml-2 text-green-600">Configured</Badge>}</Label>
                <Input
                  id="jira-token"
                  type="password"
                  placeholder="Enter API token (only if changing)"
                  value={jiraToken}
                  onChange={(e) => setJiraToken(e.target.value)}
                />
                <p className="text-sm text-slate-500">Get your API token from <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Atlassian Account Settings</a></p>
              </div>
              <div className="flex gap-3 pt-4">
                <Button onClick={handleSaveJira} className="flex-1">
                  <Save className="h-4 w-4 mr-2" /> Save JIRA Settings
                </Button>
                <Button variant="outline" onClick={handleTestJira} disabled={jiraStatus === 'testing'}>
                  {getStatusIcon(jiraStatus)}
                  <span className="ml-2">Test Connection</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* LLM Settings */}
        <TabsContent value="llm">
          <Card>
            <CardHeader>
              <CardTitle>LLM Provider</CardTitle>
              <CardDescription>Choose between cloud (Groq) or local (Ollama) LLM</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div>
                  <p className="font-medium">Use Local LLM (Ollama)</p>
                  <p className="text-sm text-slate-500">Run models locally for privacy</p>
                </div>
                <Switch checked={useLocalLLM} onCheckedChange={setUseLocalLLM} />
              </div>

              {!useLocalLLM ? (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Groq API Key {groqStatus === 'success' && <Badge variant="outline" className="ml-2 text-green-600">Configured</Badge>}</Label>
                    <Input
                      type="password"
                      placeholder="Enter API key (only if changing)"
                      value={groqKey}
                      onChange={(e) => setGroqKey(e.target.value)}
                    />
                    <p className="text-sm text-slate-500">Get your key from <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Groq Console</a></p>
                  </div>
                  <div className="space-y-2">
                    <Label>Model</Label>
                    <select
                      className="w-full h-10 px-3 rounded-md border border-input bg-background"
                      value={groqModel}
                      onChange={(e) => setGroqModel(e.target.value)}
                    >
                      <optgroup label="OpenAI GPT-OSS (Recommended)">
                        <option value="openai/gpt-oss-120b">🌟 GPT-OSS 120B (MoE - Most Powerful)</option>
                        <option value="openai/gpt-oss-20b">GPT-OSS 20B (MoE - Faster)</option>
                      </optgroup>
                      <optgroup label="Llama 3.3 (Meta)">
                        <option value="llama-3.3-70b-versatile">Llama 3.3 70B Versatile</option>
                      </optgroup>
                      <optgroup label="Llama 3.1 (Meta)">
                        <option value="llama-3.1-70b-versatile">Llama 3.1 70B Versatile</option>
                        <option value="llama-3.1-8b-instant">Llama 3.1 8B Instant (Fastest)</option>
                      </optgroup>
                      <optgroup label="Llama 3 (Meta)">
                        <option value="llama3-70b-8192">Llama 3 70B</option>
                        <option value="llama3-8b-8192">Llama 3 8B</option>
                      </optgroup>
                      <optgroup label="Other Models">
                        <option value="mixtral-8x7b-32768">Mixtral 8x7B</option>
                        <option value="gemma2-9b-it">Gemma 2 9B</option>
                      </optgroup>
                    </select>
                    <p className="text-xs text-slate-500">
                      💡 <strong>Model Info:</strong> Includes OpenAI's GPT-OSS (open-weight), Llama, Mixtral, and Gemma models.
                      GPT-OSS 120B is OpenAI's flagship MoE model with 120B parameters.
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label>Temperature: {temperature}</Label>
                    <Slider
                      value={[temperature]}
                      onValueChange={(v) => setTemperature(v[0])}
                      min={0}
                      max={1}
                      step={0.1}
                    />
                  </div>
                  <div className="flex gap-3 pt-4">
                    <Button onClick={handleSaveLLM} className="flex-1">
                      <Save className="h-4 w-4 mr-2" /> Save LLM Settings
                    </Button>
                    <Button variant="outline" onClick={handleTestGroq} disabled={groqStatus === 'testing'}>
                      {getStatusIcon(groqStatus)}
                      <span className="ml-2">Test Groq</span>
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Ollama Base URL</Label>
                    <Input
                      placeholder="http://localhost:11434"
                      value={ollamaUrl}
                      onChange={(e) => setOllamaUrl(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Model</Label>
                    <Input
                      placeholder="llama3.1"
                      value={ollamaModel}
                      onChange={(e) => setOllamaModel(e.target.value)}
                    />
                    {ollamaModels.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {ollamaModels.map((m) => (
                          <Badge 
                            key={m} 
                            variant={ollamaModel === m ? 'default' : 'outline'}
                            className="cursor-pointer"
                            onClick={() => setOllamaModel(m)}
                          >
                            {m}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-3 pt-4">
                    <Button onClick={handleSaveLLM} className="flex-1">
                      <Save className="h-4 w-4 mr-2" /> Save LLM Settings
                    </Button>
                    <Button variant="outline" onClick={handleTestOllama} disabled={ollamaStatus === 'testing'}>
                      {getStatusIcon(ollamaStatus)}
                      <span className="ml-2">Test Ollama</span>
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates */}
        <TabsContent value="templates">
          <Card>
            <CardHeader>
              <CardTitle>Template Management</CardTitle>
              <CardDescription>Upload and manage test plan templates</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center">
                <Upload className="h-8 w-8 mx-auto text-slate-400 mb-2" />
                <p className="text-sm font-medium">Upload PDF Template</p>
                <p className="text-xs text-slate-500 mb-4">Max 5MB, text-based PDFs only</p>
                <Input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="mb-3"
                />
                <Input
                  placeholder="Template name"
                  value={uploadName}
                  onChange={(e) => setUploadName(e.target.value)}
                  className="mb-3"
                />
                <Button onClick={handleUploadTemplate} disabled={!uploadFile || !uploadName}>
                  Upload Template
                </Button>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium">Available Templates</h4>
                {templates.map((t) => (
                  <div key={t.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-slate-400" />
                      <span>{t.name}</span>
                      {t.isDefault && <Badge variant="secondary">Default</Badge>}
                    </div>
                    {!t.isDefault && (
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => handleDeleteTemplate(t.id)}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
