'use client'

import React, { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { DashboardLayout } from '@/components/DashboardLayout'
import { DashboardView } from '@/components/DashboardNavigation'
import ProblemInputDisplay from '@/components/ProblemInputDisplay'
import { ParadigmSelectionViz } from '@/components/ParadigmSelectionViz'
import { TechniqueSelectionDisplay } from '@/components/TechniqueSelectionDisplay'
import { DecompositionGraphViz } from '@/components/DecompositionGraphViz'
import { AgentPoolMonitor } from '@/components/AgentPoolMonitor'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, CheckCircle, FileOutput, Loader2 } from 'lucide-react'

// Mock data for demonstrations
const mockParadigmData = {
  selectedParadigms: ['structural', 'functional', 'temporal'],
  paradigmScores: {
    structural: 0.85,
    functional: 0.78,
    temporal: 0.72,
    spatial: 0.45,
    hierarchical: 0.52,
    computational: 0.38,
    data: 0.41,
    dependency: 0.55
  },
  paradigmReasoning: {
    structural: 'High component modularity and clear separation of concerns',
    functional: 'Well-defined operations and transformations',
    temporal: 'Strong time-based sequencing requirements',
    spatial: 'Limited spatial distribution needs',
    hierarchical: 'Some layered architecture elements',
    computational: 'Moderate computational requirements',
    data: 'Simple data partitioning needs',
    dependency: 'Some dependency ordering required'
  }
}

const mockTechniqueData = {
  selectedTechniques: {
    structural: {
      name: 'Component-Based Decomposition',
      paradigm: 'structural',
      formalDefinition: 'G = (V, E) where V = components, E = interfaces',
      prerequisites: ['Clear component boundaries', 'Defined interfaces', 'Loose coupling'],
      prerequisitesStatus: {
        'Clear component boundaries': true,
        'Defined interfaces': true,
        'Loose coupling': true
      },
      complexity: 'O(n log n) for n components',
      applicabilityScore: 0.85,
      references: [
        'Gamma et al. (1994) - Design Patterns',
        'Parnas (1972) - On the Criteria To Be Used in Decomposing Systems'
      ],
      implementationStrategy: 'Top-down component identification with interface extraction',
      reasoning: 'Selected due to high modularity and clear separation of concerns in the problem domain'
    },
    functional: {
      name: 'Pipeline Decomposition',
      paradigm: 'functional',
      formalDefinition: 'f(x) = fn ∘ fn-1 ∘ ... ∘ f1(x)',
      prerequisites: ['Sequential operations', 'Stateless transformations', 'Clear data flow'],
      prerequisitesStatus: {
        'Sequential operations': true,
        'Stateless transformations': true,
        'Clear data flow': true
      },
      complexity: 'O(n) for n stages',
      applicabilityScore: 0.78,
      references: [
        'Stevens & Ripley (1995) - S Programming',
        'Armstrong (2007) - Programming Erlang'
      ],
      implementationStrategy: 'Identify transformation stages and compose them sequentially',
      reasoning: 'Well-suited for the sequential transformation requirements in the problem'
    }
  },
  alternativeTechniques: {
    structural: [
      {
        name: 'Layered Architecture',
        paradigm: 'structural',
        formalDefinition: 'L = {L1, L2, ..., Ln} where Li depends only on Li-1',
        prerequisites: ['Layer separation', 'Downward dependencies'],
        prerequisitesStatus: { 'Layer separation': false, 'Downward dependencies': true },
        complexity: 'O(n) for n layers',
        applicabilityScore: 0.62,
        references: ['Buschmann et al. (1996) - Pattern-Oriented Software Architecture'],
        implementationStrategy: 'Define layers bottom-up with strict dependency rules',
        reasoning: 'Less applicable due to non-hierarchical nature of the problem'
      }
    ]
  }
}

const mockGraphData = {
  subproblems: [
    {
      id: 'sp-1',
      name: 'Authentication Module',
      paradigm: 'structural' as const,
      description: 'Handle user authentication and session management',
      dependencies: [],
      status: 'complete' as const,
      estimatedEffort: 8,
      assignedAgent: 'agent-001',
      metadata: { priority: 'high', complexity: 'medium' }
    },
    {
      id: 'sp-2',
      name: 'Data Processing Pipeline',
      paradigm: 'functional' as const,
      description: 'Transform and validate input data',
      dependencies: ['sp-1'],
      status: 'in_progress' as const,
      estimatedEffort: 12,
      assignedAgent: 'agent-002',
      metadata: { priority: 'high', complexity: 'high' }
    },
    {
      id: 'sp-3',
      name: 'API Endpoints',
      paradigm: 'structural' as const,
      description: 'REST API implementation',
      dependencies: ['sp-1', 'sp-2'],
      status: 'pending' as const,
      estimatedEffort: 6,
      metadata: { priority: 'medium', complexity: 'low' }
    }
  ],
  dependencies: [
    { from: 'sp-1', to: 'sp-2', type: 'data' as const },
    { from: 'sp-1', to: 'sp-3', type: 'control' as const },
    { from: 'sp-2', to: 'sp-3', type: 'data' as const }
  ],
  metadata: {
    paradigmsUsed: ['structural', 'functional'],
    totalSubproblems: 3,
    completedSubproblems: 1
  }
}

// View component wrapper for loading states
function ViewWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {children}
    </div>
  )
}

// Placeholder component for views not yet implemented
function PlaceholderView({
  title,
  description,
  icon: Icon
}: {
  title: string
  description: string
  icon: React.ElementType
}) {
  return (
    <ViewWrapper>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Icon className="w-6 h-6" />
            {title}
          </CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Loader2 className="w-12 h-12 text-gray-400 mb-4 animate-spin" />
            <p className="text-lg font-medium text-gray-600 mb-2">
              View coming soon
            </p>
            <p className="text-sm text-gray-500">
              This view is currently under development
            </p>
          </div>
        </CardContent>
      </Card>
    </ViewWrapper>
  )
}

// Integration Conflicts View
function IntegrationConflictsView() {
  return (
    <ViewWrapper>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-6 h-6" />
            Integration Conflicts
          </CardTitle>
          <CardDescription>
            Detected conflicts and resolution status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-yellow-50 dark:bg-yellow-900/10 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-yellow-900 dark:text-yellow-100">
                    API Contract Mismatch
                  </h4>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    Authentication module and API endpoints have incompatible data schemas
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" className="text-xs">
                      sp-1
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      sp-3
                    </Badge>
                  </div>
                </div>
              </div>
              <Badge className="bg-yellow-600">Pending</Badge>
            </div>

            <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/10 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-green-900 dark:text-green-100">
                    Data Format Alignment
                  </h4>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                    Successfully aligned data formats between processing pipeline and API
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" className="text-xs">
                      sp-2
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      sp-3
                    </Badge>
                  </div>
                </div>
              </div>
              <Badge className="bg-green-600">Resolved</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </ViewWrapper>
  )
}

// Approval Gates View
function ApprovalGatesView() {
  return (
    <ViewWrapper>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="w-6 h-6" />
            Human Approval Gates
          </CardTitle>
          <CardDescription>
            Review and approve critical pipeline stages
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-blue-900 dark:text-blue-100">
                    Paradigm Selection Approval
                  </h4>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                    Review and approve selected decomposition paradigms
                  </p>
                </div>
                <Badge className="bg-blue-600">Approved</Badge>
              </div>
              <div className="flex gap-2">
                <Badge variant="outline">Structural</Badge>
                <Badge variant="outline">Functional</Badge>
                <Badge variant="outline">Temporal</Badge>
              </div>
            </div>

            <div className="p-4 bg-orange-50 dark:bg-orange-900/10 rounded-lg border border-orange-200 dark:border-orange-800">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-orange-900 dark:text-orange-100">
                    Decomposition Structure Approval
                  </h4>
                  <p className="text-sm text-orange-700 dark:text-orange-300 mt-1">
                    Review the decomposition graph before execution
                  </p>
                </div>
                <Badge className="bg-orange-600">Awaiting Review</Badge>
              </div>
              <div className="text-sm text-orange-700 dark:text-orange-300">
                3 subproblems, 3 dependencies
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </ViewWrapper>
  )
}

// Solution Output View
function SolutionOutputView() {
  return (
    <ViewWrapper>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileOutput className="w-6 h-6" />
            Solution Output
          </CardTitle>
          <CardDescription>
            Final integrated solution and artifacts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border">
              <h4 className="font-semibold mb-2">Output Status</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Total Files:</span>
                  <span className="ml-2 font-semibold">24</span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Lines of Code:</span>
                  <span className="ml-2 font-semibold">3,847</span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Test Coverage:</span>
                  <span className="ml-2 font-semibold">87%</span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Documentation:</span>
                  <span className="ml-2 font-semibold">Complete</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-green-50 dark:bg-green-900/10 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <h4 className="font-semibold text-green-900 dark:text-green-100">
                  Integration Complete
                </h4>
              </div>
              <p className="text-sm text-green-700 dark:text-green-300">
                All subproblems have been successfully integrated and validated
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </ViewWrapper>
  )
}

// Main dashboard content component
function DashboardContent() {
  const searchParams = useSearchParams()
  const view = (searchParams.get('view') as DashboardView) || 'problem-input'

  const renderView = () => {
    switch (view) {
      case 'problem-input':
        return (
          <ViewWrapper>
            <ProblemInputDisplay
              onSubmit={(text, chars) => {
                console.log('Problem submitted:', text, chars)
              }}
            />
          </ViewWrapper>
        )

      case 'paradigm-selection':
        return (
          <ViewWrapper>
            <ParadigmSelectionViz data={mockParadigmData} />
          </ViewWrapper>
        )

      case 'technique-selection':
        return (
          <ViewWrapper>
            <TechniqueSelectionDisplay data={mockTechniqueData} />
          </ViewWrapper>
        )

      case 'decomposition-graph':
        return (
          <ViewWrapper>
            <Card>
              <CardHeader>
                <CardTitle>Decomposition Graph</CardTitle>
                <CardDescription>
                  Interactive visualization of subproblem structure
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DecompositionGraphViz
                  graph={mockGraphData}
                  height="600px"
                  onNodeSelect={(nodeId) => {
                    console.log('Selected node:', nodeId)
                  }}
                />
              </CardContent>
            </Card>
          </ViewWrapper>
        )

      case 'agent-pool':
        return (
          <ViewWrapper>
            <AgentPoolMonitor />
          </ViewWrapper>
        )

      case 'integration-conflicts':
        return <IntegrationConflictsView />

      case 'approval-gates':
        return <ApprovalGatesView />

      case 'solution-output':
        return <SolutionOutputView />

      default:
        return (
          <ViewWrapper>
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-gray-600">View not found: {view}</p>
              </CardContent>
            </Card>
          </ViewWrapper>
        )
    }
  }

  return <DashboardLayout currentView={view}>{renderView()}</DashboardLayout>
}

// Main page component with Suspense boundary
export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <DashboardLayout>
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        </DashboardLayout>
      }
    >
      <DashboardContent />
    </Suspense>
  )
}
