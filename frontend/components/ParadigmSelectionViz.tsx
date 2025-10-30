"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/**
 * Data structure for paradigm selection output from Level 1 of the decomposition pipeline
 */
export interface ParadigmScore {
  paradigm: string;
  score: number;
  reasoning: string;
  selected: boolean;
}

export interface ParadigmSelectionData {
  selectedParadigms: string[];
  paradigmScores: Record<string, number>;
  paradigmReasoning: Record<string, string>;
}

interface ParadigmSelectionVizProps {
  data: ParadigmSelectionData;
  className?: string;
}

/**
 * The 8 decomposition paradigms with their descriptions
 */
const PARADIGMS = [
  { id: "structural", name: "Structural", description: "Graph/component decomposition" },
  { id: "functional", name: "Functional", description: "Operation/task decomposition" },
  { id: "temporal", name: "Temporal", description: "Time/stage decomposition" },
  { id: "spatial", name: "Spatial", description: "Region/location decomposition" },
  { id: "hierarchical", name: "Hierarchical", description: "Layer/level decomposition" },
  { id: "computational", name: "Computational", description: "Resource/workload decomposition" },
  { id: "data", name: "Data", description: "Partition/schema decomposition" },
  { id: "dependency", name: "Dependency", description: "Order/sequence decomposition" },
];

/**
 * Get color classes based on score threshold
 */
function getScoreColorClass(score: number, selected: boolean): string {
  if (selected || score > 0.6) {
    return "bg-green-500";
  } else if (score >= 0.3) {
    return "bg-yellow-500";
  }
  return "bg-gray-300";
}

/**
 * Get text color based on score
 */
function getScoreTextColor(score: number, selected: boolean): string {
  if (selected || score > 0.6) {
    return "text-green-700";
  } else if (score >= 0.3) {
    return "text-yellow-700";
  }
  return "text-gray-500";
}

/**
 * ParadigmSelectionViz Component
 *
 * Visualizes the paradigm selection output from Level 1 of the LangGraph decomposition pipeline.
 * Shows all 8 paradigms with their scores, selected status, and reasoning.
 *
 * @param data - The paradigm selection data containing scores, selections, and reasoning
 * @param className - Optional additional CSS classes
 */
export function ParadigmSelectionViz({ data, className }: ParadigmSelectionVizProps) {
  const [expandedParadigm, setExpandedParadigm] = React.useState<string | null>(null);

  // Transform data into ParadigmScore array
  const paradigmScores: ParadigmScore[] = PARADIGMS.map((paradigm) => ({
    paradigm: paradigm.id,
    score: data.paradigmScores[paradigm.id] || 0,
    reasoning: data.paradigmReasoning[paradigm.id] || "No reasoning provided",
    selected: data.selectedParadigms.includes(paradigm.id),
  }));

  const toggleReasoning = (paradigmId: string) => {
    setExpandedParadigm(expandedParadigm === paradigmId ? null : paradigmId);
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          Selected Decomposition Paradigms
        </CardTitle>
        <CardDescription>
          Level 1 output showing paradigm applicability scores and selections
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {paradigmScores.map((item) => {
          const paradigmInfo = PARADIGMS.find((p) => p.id === item.paradigm);
          const isExpanded = expandedParadigm === item.paradigm;

          return (
            <div
              key={item.paradigm}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              {/* Paradigm Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-lg">
                      {paradigmInfo?.name || item.paradigm}
                    </h4>
                    {item.selected && (
                      <Badge variant="success" className="ml-2">
                        Selected
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {paradigmInfo?.description}
                  </p>
                </div>
              </div>

              {/* Score Bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">Applicability Score</span>
                  <span
                    className={cn(
                      "text-sm font-bold",
                      getScoreTextColor(item.score, item.selected)
                    )}
                  >
                    {(item.score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className={cn(
                      "h-full transition-all duration-500 ease-out rounded-full",
                      getScoreColorClass(item.score, item.selected)
                    )}
                    style={{ width: `${item.score * 100}%` }}
                    role="progressbar"
                    aria-valuenow={item.score * 100}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`${paradigmInfo?.name} score: ${(item.score * 100).toFixed(0)}%`}
                  />
                </div>
              </div>

              {/* Reasoning Section */}
              <div>
                <button
                  onClick={() => toggleReasoning(item.paradigm)}
                  className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-2 py-1"
                  aria-expanded={isExpanded}
                  aria-controls={`reasoning-${item.paradigm}`}
                >
                  <span className={cn(
                    "transition-transform duration-200",
                    isExpanded ? "rotate-90" : ""
                  )}>
                    ▶
                  </span>
                  {isExpanded ? "Hide" : "Show"} Reasoning
                </button>

                {isExpanded && (
                  <div
                    id={`reasoning-${item.paradigm}`}
                    className="mt-2 p-3 bg-gray-50 rounded-md border border-gray-200 text-sm"
                  >
                    {item.reasoning}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Summary */}
        <div className="mt-6 pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Selected Paradigms:</span>
            <span className="font-bold text-green-700">
              {data.selectedParadigms.length} of {PARADIGMS.length}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {data.selectedParadigms.map((paradigmId) => {
              const paradigmInfo = PARADIGMS.find((p) => p.id === paradigmId);
              return (
                <Badge key={paradigmId} variant="success">
                  {paradigmInfo?.name || paradigmId}
                </Badge>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
