'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { extractCharacteristics, ProblemCharacteristics } from '@/lib/extractCharacteristics';

interface ProblemInputDisplayProps {
  onSubmit?: (problemText: string, characteristics: ProblemCharacteristics) => void;
  initialProblem?: string;
}

export default function ProblemInputDisplay({
  onSubmit,
  initialProblem = '',
}: ProblemInputDisplayProps) {
  const [problemText, setProblemText] = useState(initialProblem);
  const [characteristics, setCharacteristics] = useState<ProblemCharacteristics | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  // Auto-extract characteristics with debounce
  useEffect(() => {
    if (problemText.trim().length < 10) {
      setCharacteristics(null);
      return;
    }

    setIsAnalyzing(true);
    const timer = setTimeout(() => {
      const extracted = extractCharacteristics(problemText);
      setCharacteristics(extracted);
      setIsAnalyzing(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [problemText]);

  const handleSubmit = () => {
    if (problemText.trim() && characteristics) {
      onSubmit?.(problemText, characteristics);
    }
  };

  const handleClear = () => {
    setProblemText('');
    setCharacteristics(null);
  };

  const characterCount = problemText.length;
  const wordCount = problemText.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-4">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Problem Description</CardTitle>
          <CardDescription>
            Describe the problem you want to decompose. Be as detailed as possible to get better
            characteristics extraction.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="problem-input">Problem Description</Label>
            <Textarea
              id="problem-input"
              placeholder="Enter your problem description here...

Example: Build a real-time collaborative text editor with conflict resolution, supporting multiple users editing the same document simultaneously. The system should handle operational transformations, maintain version history, and provide cursor tracking."
              value={problemText}
              onChange={(e) => setProblemText(e.target.value)}
              className="min-h-[200px] font-mono text-sm"
              aria-label="Problem description input"
            />
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>
                {wordCount} {wordCount === 1 ? 'word' : 'words'} • {characterCount}{' '}
                {characterCount === 1 ? 'character' : 'characters'}
              </span>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPreview(!showPreview)}
                  disabled={!problemText.trim()}
                >
                  {showPreview ? 'Hide' : 'Show'} Preview
                </Button>
                <Button variant="ghost" size="sm" onClick={handleClear} disabled={!problemText}>
                  Clear
                </Button>
              </div>
            </div>
          </div>

          {showPreview && problemText.trim() && (
            <div className="border rounded-md p-4 bg-muted/50">
              <h4 className="text-sm font-semibold mb-2">Preview</h4>
              <div className="prose prose-sm max-w-none">
                {problemText.split('\n').map((line, i) => (
                  <p key={i} className="mb-2">
                    {line || '\u00A0'}
                  </p>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <Button
              onClick={handleSubmit}
              disabled={!problemText.trim() || !characteristics || isAnalyzing}
              className="flex-1"
            >
              {isAnalyzing ? 'Analyzing...' : 'Start Pipeline'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Characteristics Section */}
      {characteristics && (
        <Card>
          <CardHeader>
            <CardTitle>Extracted Characteristics</CardTitle>
            <CardDescription>
              Automatically detected problem attributes. These will be used for paradigm and
              technique selection.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Size */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold">Size Estimate</h4>
                <ConfidenceBadge confidence={characteristics.size.confidence} />
              </div>
              <div className="flex gap-2 items-center">
                <Badge variant="secondary" className="text-base capitalize">
                  {characteristics.size.estimated}
                </Badge>
                {characteristics.size.linesOfCode && (
                  <span className="text-sm text-muted-foreground">
                    ≈ {characteristics.size.linesOfCode.toLocaleString()} LOC
                  </span>
                )}
              </div>
            </div>

            {/* Complexity */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold">Complexity</h4>
                <ConfidenceBadge confidence={characteristics.complexity.confidence} />
              </div>
              <div className="space-y-2">
                <Badge
                  variant="secondary"
                  className={`text-base capitalize ${getComplexityColor(
                    characteristics.complexity.level
                  )}`}
                >
                  {characteristics.complexity.level}
                </Badge>
                {characteristics.complexity.factors.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {characteristics.complexity.factors.map((factor) => (
                      <Badge key={factor} variant="outline" className="text-xs capitalize">
                        {factor.replace(/([A-Z])/g, ' $1').trim()}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Structure */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold">Detected Structure</h4>
                <ConfidenceBadge confidence={characteristics.structure.confidence} />
              </div>
              <div className="flex flex-wrap gap-1">
                {characteristics.structure.types.map((type) => (
                  <Badge key={type} variant="secondary" className="capitalize">
                    {type}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Resources */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold">Resource Requirements</h4>
                <ConfidenceBadge confidence={characteristics.resources.confidence} />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div className="flex flex-col">
                  <span className="text-xs text-muted-foreground">Compute</span>
                  <Badge variant="outline" className="capitalize mt-1">
                    {characteristics.resources.compute}
                  </Badge>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-muted-foreground">Memory</span>
                  <Badge variant="outline" className="capitalize mt-1">
                    {characteristics.resources.memory}
                  </Badge>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-muted-foreground">Real-time</span>
                  <Badge
                    variant="outline"
                    className={`mt-1 ${characteristics.resources.realTime ? 'bg-green-100' : ''}`}
                  >
                    {characteristics.resources.realTime ? 'Yes' : 'No'}
                  </Badge>
                </div>
                <div className="flex flex-col">
                  <span className="text-xs text-muted-foreground">Distributed</span>
                  <Badge
                    variant="outline"
                    className={`mt-1 ${
                      characteristics.resources.distributed ? 'bg-green-100' : ''
                    }`}
                  >
                    {characteristics.resources.distributed ? 'Yes' : 'No'}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Domains */}
            {characteristics.domains.detected.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold">Domain Hints</h4>
                  <ConfidenceBadge confidence={characteristics.domains.confidence} />
                </div>
                <div className="flex flex-wrap gap-1">
                  {characteristics.domains.detected.map((domain) => (
                    <Badge key={domain} variant="secondary" className="capitalize">
                      {domain}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Constraints */}
            {(characteristics.constraints.timing.length > 0 ||
              characteristics.constraints.dependencies.length > 0 ||
              characteristics.constraints.technical.length > 0) && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold">Detected Constraints</h4>
                  <ConfidenceBadge confidence={characteristics.constraints.confidence} />
                </div>
                <div className="space-y-2 text-sm">
                  {characteristics.constraints.timing.length > 0 && (
                    <div>
                      <span className="text-muted-foreground">Timing:</span>{' '}
                      <span>{characteristics.constraints.timing.join(', ')}</span>
                    </div>
                  )}
                  {characteristics.constraints.dependencies.length > 0 && (
                    <div>
                      <span className="text-muted-foreground">Dependencies:</span>{' '}
                      <span>{characteristics.constraints.dependencies.join(', ')}</span>
                    </div>
                  )}
                  {characteristics.constraints.technical.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {characteristics.constraints.technical.slice(0, 5).map((tech, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {tech}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Help Text */}
      {!problemText && (
        <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <h4 className="font-semibold mb-2">Tips for better extraction:</h4>
            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              <li>Describe the problem in detail (what, why, how)</li>
              <li>Mention key technologies, frameworks, or tools</li>
              <li>Include requirements (performance, scalability, security)</li>
              <li>Specify constraints (timing, resources, dependencies)</li>
              <li>Describe the expected outcome or deliverable</li>
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Helper component for confidence badges
function ConfidenceBadge({ confidence }: { confidence: number }) {
  const percentage = Math.round(confidence * 100);
  const variant = confidence >= 0.7 ? 'default' : confidence >= 0.5 ? 'secondary' : 'outline';

  return (
    <Badge variant={variant} className="text-xs">
      {percentage}% confidence
    </Badge>
  );
}

// Helper function for complexity colors
function getComplexityColor(level: string): string {
  switch (level) {
    case 'low':
      return 'bg-green-100 text-green-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'high':
      return 'bg-orange-100 text-orange-800';
    case 'very high':
      return 'bg-red-100 text-red-800';
    default:
      return '';
  }
}
