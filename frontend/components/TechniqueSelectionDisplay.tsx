"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { CheckCircle2, XCircle, ChevronDown, ChevronRight, BookOpen } from "lucide-react";

/**
 * Data structure for technique information from the catalog
 */
export interface Technique {
  name: string;
  paradigm: string;
  formalDefinition: string;
  prerequisites: string[];
  prerequisitesStatus: Record<string, boolean>;
  complexity: string;
  applicabilityScore: number;
  references: string[];
  implementationStrategy: string;
  reasoning: string;
}

/**
 * Data structure for technique selection output from Level 2
 */
export interface TechniqueSelectionData {
  selectedTechniques: Record<string, Technique>; // paradigm -> technique
  techniqueScores?: Record<string, number>;
  techniqueJustification?: Record<string, string>;
  alternativeTechniques?: Record<string, Technique[]>; // paradigm -> alternatives
}

interface TechniqueSelectionDisplayProps {
  data: TechniqueSelectionData;
  className?: string;
}

/**
 * The 8 decomposition paradigms with their color schemes
 */
const PARADIGM_INFO: Record<string, { name: string; color: string; bgColor: string }> = {
  structural: { name: "Structural", color: "text-blue-700", bgColor: "bg-blue-50 border-blue-200" },
  functional: { name: "Functional", color: "text-purple-700", bgColor: "bg-purple-50 border-purple-200" },
  temporal: { name: "Temporal", color: "text-orange-700", bgColor: "bg-orange-50 border-orange-200" },
  spatial: { name: "Spatial", color: "text-green-700", bgColor: "bg-green-50 border-green-200" },
  hierarchical: { name: "Hierarchical", color: "text-indigo-700", bgColor: "bg-indigo-50 border-indigo-200" },
  computational: { name: "Computational", color: "text-red-700", bgColor: "bg-red-50 border-red-200" },
  data: { name: "Data", color: "text-teal-700", bgColor: "bg-teal-50 border-teal-200" },
  dependency: { name: "Dependency", color: "text-pink-700", bgColor: "bg-pink-50 border-pink-200" },
};

/**
 * Get score color class based on applicability score
 */
function getScoreColorClass(score: number): string {
  if (score >= 0.8) return "bg-green-500";
  if (score >= 0.6) return "bg-blue-500";
  if (score >= 0.4) return "bg-yellow-500";
  return "bg-orange-500";
}

/**
 * Get score text color based on applicability score
 */
function getScoreTextColor(score: number): string {
  if (score >= 0.8) return "text-green-700";
  if (score >= 0.6) return "text-blue-700";
  if (score >= 0.4) return "text-yellow-700";
  return "text-orange-700";
}

/**
 * PrerequisiteItem Component
 * Displays a single prerequisite with its validation status
 */
function PrerequisiteItem({ prerequisite, status }: { prerequisite: string; status: boolean }) {
  return (
    <div className="flex items-start gap-2">
      {status ? (
        <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
      ) : (
        <XCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
      )}
      <span className={cn("text-sm", status ? "text-gray-700" : "text-red-700")}>
        {prerequisite}
      </span>
    </div>
  );
}

/**
 * TechniqueCard Component
 * Displays detailed information about a selected technique
 */
function TechniqueCard({ technique }: { technique: Technique }) {
  const [showJustification, setShowJustification] = React.useState(false);
  const paradigmInfo = PARADIGM_INFO[technique.paradigm] || {
    name: technique.paradigm,
    color: "text-gray-700",
    bgColor: "bg-gray-50 border-gray-200",
  };

  const allPrerequisitesMet = Object.values(technique.prerequisitesStatus).every((status) => status);

  return (
    <div className={cn("border-2 rounded-lg p-5", paradigmInfo.bgColor)}>
      {/* Paradigm Label */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className={cn("text-lg font-semibold", paradigmInfo.color)}>
            {paradigmInfo.name} Decomposition
          </h3>
          <Badge variant={allPrerequisitesMet ? "success" : "destructive"}>
            {allPrerequisitesMet ? "Prerequisites Met" : "Prerequisites Not Met"}
          </Badge>
        </div>
      </div>

      {/* Technique Name and Score */}
      <div className="mb-4 bg-white rounded-lg p-4 border">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h4 className="text-xl font-bold text-gray-900 mb-1">{technique.name}</h4>
            <p className="text-sm text-gray-600">Algorithmic Technique from Catalog</p>
          </div>
          <div className="text-right">
            <div className={cn("text-2xl font-bold", getScoreTextColor(technique.applicabilityScore))}>
              {(technique.applicabilityScore * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500">Applicability</div>
          </div>
        </div>

        {/* Score Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className={cn(
              "h-full transition-all duration-500 ease-out rounded-full",
              getScoreColorClass(technique.applicabilityScore)
            )}
            style={{ width: `${technique.applicabilityScore * 100}%` }}
            role="progressbar"
            aria-valuenow={technique.applicabilityScore * 100}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${technique.name} applicability score: ${(technique.applicabilityScore * 100).toFixed(0)}%`}
          />
        </div>
      </div>

      {/* Formal Definition */}
      <div className="mb-4 bg-white rounded-lg p-4 border">
        <h5 className="text-sm font-semibold text-gray-700 mb-2">Formal Definition</h5>
        <pre className="text-sm bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto font-mono text-gray-800">
          {technique.formalDefinition}
        </pre>
      </div>

      {/* Prerequisites */}
      <div className="mb-4 bg-white rounded-lg p-4 border">
        <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          Prerequisites Validation
          {allPrerequisitesMet && (
            <Badge variant="success" className="ml-2">
              ✓ All Met
            </Badge>
          )}
        </h5>
        <div className="space-y-2">
          {technique.prerequisites.map((prereq, index) => (
            <PrerequisiteItem
              key={index}
              prerequisite={prereq}
              status={technique.prerequisitesStatus[prereq] ?? false}
            />
          ))}
        </div>
      </div>

      {/* Complexity and Implementation Strategy */}
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <div className="bg-white rounded-lg p-4 border">
          <h5 className="text-sm font-semibold text-gray-700 mb-2">Complexity</h5>
          <p className="text-sm text-gray-800 font-mono">{technique.complexity}</p>
        </div>
        <div className="bg-white rounded-lg p-4 border">
          <h5 className="text-sm font-semibold text-gray-700 mb-2">Implementation Strategy</h5>
          <p className="text-sm text-gray-700">{technique.implementationStrategy}</p>
        </div>
      </div>

      {/* Literature References */}
      <div className="mb-4 bg-white rounded-lg p-4 border">
        <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <BookOpen className="w-4 h-4" />
          Literature References
        </h5>
        <ul className="space-y-2">
          {technique.references.map((reference, index) => (
            <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
              <span className="text-gray-400">•</span>
              <span>{reference}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Formal Justification */}
      <div className="bg-white rounded-lg border">
        <button
          onClick={() => setShowJustification(!showJustification)}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
          aria-expanded={showJustification}
          aria-controls={`justification-${technique.paradigm}`}
        >
          <span className="text-sm font-semibold text-gray-700">Formal Justification</span>
          {showJustification ? (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-500" />
          )}
        </button>

        {showJustification && (
          <div
            id={`justification-${technique.paradigm}`}
            className="px-4 pb-4 text-sm text-gray-700 leading-relaxed border-t"
          >
            <div className="pt-4 space-y-2">
              {technique.reasoning}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * AlternativeTechniquesSection Component
 * Displays alternative techniques that were considered but not selected
 */
function AlternativeTechniquesSection({
  paradigm,
  alternatives,
}: {
  paradigm: string;
  alternatives: Technique[];
}) {
  const [showAlternatives, setShowAlternatives] = React.useState(false);
  const paradigmInfo = PARADIGM_INFO[paradigm] || { name: paradigm };

  return (
    <div className="mt-4 border rounded-lg">
      <button
        onClick={() => setShowAlternatives(!showAlternatives)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        aria-expanded={showAlternatives}
        aria-controls={`alternatives-${paradigm}`}
      >
        <span className="text-sm font-semibold text-gray-700">
          Alternative Techniques Considered ({alternatives.length})
        </span>
        {showAlternatives ? (
          <ChevronDown className="w-5 h-5 text-gray-500" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-500" />
        )}
      </button>

      {showAlternatives && (
        <div
          id={`alternatives-${paradigm}`}
          className="px-4 pb-4 space-y-3 border-t bg-gray-50"
        >
          {alternatives.map((alt, index) => (
            <div key={index} className="bg-white rounded-lg p-4 border border-gray-200 mt-3">
              <div className="flex items-start justify-between mb-2">
                <h5 className="font-semibold text-gray-900">{alt.name}</h5>
                <span className={cn("text-sm font-bold", getScoreTextColor(alt.applicabilityScore))}>
                  {(alt.applicabilityScore * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{alt.reasoning}</p>
              <div className="text-xs text-gray-500">
                <span className="font-semibold">Complexity:</span> {alt.complexity}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * TechniqueSelectionDisplay Component
 *
 * Visualizes the technique selection output from Level 2 of the LangGraph decomposition pipeline.
 * Shows selected techniques for each paradigm with formal justifications, prerequisites, and literature citations.
 *
 * @param data - The technique selection data containing selected techniques and alternatives
 * @param className - Optional additional CSS classes
 */
export function TechniqueSelectionDisplay({ data, className }: TechniqueSelectionDisplayProps) {
  const paradigms = Object.keys(data.selectedTechniques);

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">🔧</span>
          Selected Techniques
        </CardTitle>
        <CardDescription>
          Level 2 output showing algorithmic techniques selected from the catalog with formal justification
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {paradigms.map((paradigm) => {
          const technique = data.selectedTechniques[paradigm];
          const alternatives = data.alternativeTechniques?.[paradigm] || [];

          return (
            <div key={paradigm}>
              <TechniqueCard technique={technique} />
              {alternatives.length > 0 && (
                <AlternativeTechniquesSection paradigm={paradigm} alternatives={alternatives} />
              )}
            </div>
          );
        })}

        {/* Summary Footer */}
        <div className="mt-6 pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-gray-700">Total Techniques Selected:</span>
            <span className="font-bold text-blue-700">{paradigms.length}</span>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {paradigms.map((paradigm) => {
              const paradigmInfo = PARADIGM_INFO[paradigm] || { name: paradigm };
              return (
                <Badge key={paradigm} variant="outline" className="font-medium">
                  {paradigmInfo.name}: {data.selectedTechniques[paradigm].name}
                </Badge>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
