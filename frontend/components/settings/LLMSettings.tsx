/**
 * LLM Settings Component
 * Configure Language Model providers, models, and parameters
 */

import React, { useState } from 'react';
import { useSettingsStore } from '@/lib/settings-store';
import { LLM_MODELS, LLMProvider } from '@/types/settings';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function LLMSettings() {
  const { settings, updateLLMConfig, validationErrors } = useSettingsStore();
  const { llm } = settings;
  const [showApiKey, setShowApiKey] = useState(false);

  const getFieldError = (field: string) => {
    return validationErrors.find((err) => err.field === field);
  };

  const handleProviderChange = (provider: LLMProvider) => {
    // Update provider and reset to default model for that provider
    const defaultModel = LLM_MODELS[provider][0];
    updateLLMConfig({
      provider,
      defaultModel,
      level1Model: defaultModel,
      level2Model: defaultModel,
      level3Model: defaultModel,
      level4Model: defaultModel,
    });
  };

  const handleNumberChange = (field: keyof typeof llm, value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      updateLLMConfig({ [field]: numValue });
    }
  };

  const maskApiKey = (key?: string) => {
    if (!key) return '';
    if (key.length <= 8) return '••••••••';
    return key.substring(0, 4) + '••••••••' + key.substring(key.length - 4);
  };

  const temperatureError = getFieldError('llm.temperature');
  const maxTokensError = getFieldError('llm.maxTokens');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">LLM Configuration</h2>
        <p className="text-muted-foreground">
          Configure language model providers, models, and generation parameters
        </p>
      </div>

      {/* Provider Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Provider Configuration</CardTitle>
          <CardDescription>
            Select your preferred LLM provider and authentication
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Provider */}
          <div className="space-y-2">
            <Label htmlFor="provider">LLM Provider</Label>
            <Select value={llm.provider} onValueChange={handleProviderChange}>
              <SelectTrigger id="provider">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openai">OpenAI</SelectItem>
                <SelectItem value="anthropic">Anthropic</SelectItem>
                <SelectItem value="together">Together AI</SelectItem>
                <SelectItem value="ollama">Ollama (Local)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Choose the LLM provider for all model interactions
            </p>
          </div>

          {/* API Key */}
          {llm.provider !== 'ollama' && (
            <div className="space-y-2">
              <Label htmlFor="apiKey">API Key</Label>
              <div className="flex gap-2">
                <Input
                  id="apiKey"
                  type={showApiKey ? 'text' : 'password'}
                  value={showApiKey ? llm.apiKey || '' : maskApiKey(llm.apiKey)}
                  onChange={(e) => updateLLMConfig({ apiKey: e.target.value })}
                  placeholder="Enter your API key"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => setShowApiKey(!showApiKey)}
                >
                  {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                Your API key is stored locally and never sent to our servers
              </p>
            </div>
          )}

          {/* Ollama Endpoint */}
          {llm.provider === 'ollama' && (
            <div className="space-y-2">
              <Label htmlFor="apiEndpoint">Ollama Endpoint</Label>
              <Input
                id="apiEndpoint"
                type="url"
                value={llm.apiEndpoint || 'http://localhost:11434'}
                onChange={(e) => updateLLMConfig({ apiEndpoint: e.target.value })}
                placeholder="http://localhost:11434"
              />
              <p className="text-sm text-muted-foreground">
                URL of your local Ollama instance
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Model Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Model Selection</CardTitle>
          <CardDescription>
            Choose specific models for different pipeline levels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Default Model */}
          <div className="space-y-2">
            <Label htmlFor="defaultModel">Default Model</Label>
            <Select
              value={llm.defaultModel}
              onValueChange={(value) => updateLLMConfig({ defaultModel: value })}
            >
              <SelectTrigger id="defaultModel">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LLM_MODELS[llm.provider].map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Fallback model used when level-specific models are not set
            </p>
          </div>

          {/* Level 1 Model */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="level1Model">Level 1 - Paradigm Selection</Label>
              <Badge variant="outline" className="text-xs">Optional</Badge>
            </div>
            <Select
              value={llm.level1Model || llm.defaultModel}
              onValueChange={(value) => updateLLMConfig({ level1Model: value })}
            >
              <SelectTrigger id="level1Model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LLM_MODELS[llm.provider].map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Level 2 Model */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="level2Model">Level 2 - Technique Selection</Label>
              <Badge variant="outline" className="text-xs">Optional</Badge>
            </div>
            <Select
              value={llm.level2Model || llm.defaultModel}
              onValueChange={(value) => updateLLMConfig({ level2Model: value })}
            >
              <SelectTrigger id="level2Model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LLM_MODELS[llm.provider].map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Level 3 Model */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="level3Model">Level 3 - Decomposition</Label>
              <Badge variant="outline" className="text-xs">Optional</Badge>
            </div>
            <Select
              value={llm.level3Model || llm.defaultModel}
              onValueChange={(value) => updateLLMConfig({ level3Model: value })}
            >
              <SelectTrigger id="level3Model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LLM_MODELS[llm.provider].map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Level 4 Model */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="level4Model">Level 4 - Execution</Label>
              <Badge variant="default" className="text-xs">Recommended</Badge>
            </div>
            <Select
              value={llm.level4Model || llm.defaultModel}
              onValueChange={(value) => updateLLMConfig({ level4Model: value })}
            >
              <SelectTrigger id="level4Model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LLM_MODELS[llm.provider].map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Generation Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Generation Parameters</CardTitle>
          <CardDescription>
            Fine-tune model output characteristics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Temperature */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="temperature">Temperature</Label>
              <span className="text-sm text-muted-foreground">{llm.temperature}</span>
            </div>
            <Input
              id="temperature"
              type="number"
              min="0"
              max="2"
              step="0.1"
              value={llm.temperature}
              onChange={(e) => handleNumberChange('temperature', e.target.value)}
              className={temperatureError ? 'border-red-500' : ''}
            />
            {temperatureError && (
              <p className="text-sm text-red-500">{temperatureError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Controls randomness: 0 is deterministic, 2 is very creative (0.0-2.0)
            </p>
          </div>

          {/* Max Tokens */}
          <div className="space-y-2">
            <Label htmlFor="maxTokens">Max Tokens</Label>
            <Input
              id="maxTokens"
              type="number"
              min="1"
              max="32000"
              value={llm.maxTokens}
              onChange={(e) => handleNumberChange('maxTokens', e.target.value)}
              className={maxTokensError ? 'border-red-500' : ''}
            />
            {maxTokensError && (
              <p className="text-sm text-red-500">{maxTokensError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Maximum length of generated responses (1-32000)
            </p>
          </div>

          {/* Top P */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="topP">Top P (Nucleus Sampling)</Label>
              <span className="text-sm text-muted-foreground">{llm.topP || 1.0}</span>
            </div>
            <Input
              id="topP"
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={llm.topP || 1.0}
              onChange={(e) => handleNumberChange('topP', e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Cumulative probability cutoff (0.0-1.0)
            </p>
          </div>

          {/* Frequency Penalty */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="frequencyPenalty">Frequency Penalty</Label>
              <span className="text-sm text-muted-foreground">{llm.frequencyPenalty || 0}</span>
            </div>
            <Input
              id="frequencyPenalty"
              type="number"
              min="-2"
              max="2"
              step="0.1"
              value={llm.frequencyPenalty || 0}
              onChange={(e) => handleNumberChange('frequencyPenalty', e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Penalize repeated tokens (-2.0 to 2.0)
            </p>
          </div>

          {/* Presence Penalty */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="presencePenalty">Presence Penalty</Label>
              <span className="text-sm text-muted-foreground">{llm.presencePenalty || 0}</span>
            </div>
            <Input
              id="presencePenalty"
              type="number"
              min="-2"
              max="2"
              step="0.1"
              value={llm.presencePenalty || 0}
              onChange={(e) => handleNumberChange('presencePenalty', e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Penalize new topics (-2.0 to 2.0)
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
