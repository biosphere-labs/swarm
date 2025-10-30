import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import {
  TechniqueSelectionDisplay,
  TechniqueSelectionData,
  Technique,
} from "@/components/TechniqueSelectionDisplay";

// Mock sample data for testing
const mockTechnique: Technique = {
  name: "Divide and Conquer",
  paradigm: "structural",
  formalDefinition: "T(n) = aT(n/b) + f(n)",
  prerequisites: ["problem_is_divisible", "subproblems_independent"],
  prerequisitesStatus: {
    problem_is_divisible: true,
    subproblems_independent: true,
  },
  complexity: "O(n log n) typical",
  applicabilityScore: 0.91,
  references: ["CLRS Chapter 4", "Bentley 1980"],
  implementationStrategy: "Recursively split, solve subproblems, merge results",
  reasoning:
    "Problem exhibits recursive structure with independent subproblems. Divide-and-conquer is optimal for this type of decomposition based on problem size and structure characteristics.",
};

const mockAlternativeTechnique: Technique = {
  name: "Graph Partitioning",
  paradigm: "structural",
  formalDefinition: "Partition G(V,E) into k subgraphs minimizing edge cut",
  prerequisites: ["problem_is_graph", "nodes_identifiable"],
  prerequisitesStatus: {
    problem_is_graph: false,
    nodes_identifiable: true,
  },
  complexity: "O(|E| log |V|) with heuristics",
  applicabilityScore: 0.72,
  references: ["Kernighan-Lin 1970"],
  implementationStrategy: "Build graph, apply partitioning algorithm",
  reasoning: "While problem has graph-like structure, it's not explicitly a graph problem.",
};

const mockData: TechniqueSelectionData = {
  selectedTechniques: {
    structural: mockTechnique,
  },
  techniqueScores: {
    structural: 0.91,
  },
  techniqueJustification: {
    structural: "Best fit for recursive problem structure",
  },
  alternativeTechniques: {
    structural: [mockAlternativeTechnique],
  },
};

const mockMultiParadigmData: TechniqueSelectionData = {
  selectedTechniques: {
    structural: mockTechnique,
    temporal: {
      name: "Event-Driven Pipeline",
      paradigm: "temporal",
      formalDefinition: "Events → Handlers → State Updates",
      prerequisites: ["sequential_stages_identifiable", "event_ordering_maintained"],
      prerequisitesStatus: {
        sequential_stages_identifiable: true,
        event_ordering_maintained: true,
      },
      complexity: "O(n) throughput after warmup",
      applicabilityScore: 0.88,
      references: ["SEDA Architecture (Welsh 2001)", "Event Sourcing (Fowler 2005)"],
      implementationStrategy: "Define event types, create handlers, implement state update logic",
      reasoning: "Problem has clear sequential stages with event-driven characteristics.",
    },
  },
};

describe("TechniqueSelectionDisplay", () => {
  it("renders without crashing", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Selected Techniques")).toBeInTheDocument();
  });

  it("displays technique name and score", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Divide and Conquer")).toBeInTheDocument();
    expect(screen.getByText("91%")).toBeInTheDocument();
  });

  it("displays paradigm information", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Structural Decomposition")).toBeInTheDocument();
  });

  it("displays formal definition", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Formal Definition")).toBeInTheDocument();
    expect(screen.getByText("T(n) = aT(n/b) + f(n)")).toBeInTheDocument();
  });

  it("displays prerequisites with validation status", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Prerequisites Validation")).toBeInTheDocument();
    expect(screen.getByText("problem_is_divisible")).toBeInTheDocument();
    expect(screen.getByText("subproblems_independent")).toBeInTheDocument();
    expect(screen.getByText("✓ All Met")).toBeInTheDocument();
  });

  it("displays complexity and implementation strategy", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Complexity")).toBeInTheDocument();
    expect(screen.getByText("O(n log n) typical")).toBeInTheDocument();
    expect(screen.getByText("Implementation Strategy")).toBeInTheDocument();
    expect(screen.getByText("Recursively split, solve subproblems, merge results")).toBeInTheDocument();
  });

  it("displays literature references", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Literature References")).toBeInTheDocument();
    expect(screen.getByText("CLRS Chapter 4")).toBeInTheDocument();
    expect(screen.getByText("Bentley 1980")).toBeInTheDocument();
  });

  it("toggles formal justification visibility", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);

    const justificationButton = screen.getByText("Formal Justification");
    expect(justificationButton).toBeInTheDocument();

    // Initially hidden
    expect(
      screen.queryByText(/Problem exhibits recursive structure/)
    ).not.toBeInTheDocument();

    // Click to show
    fireEvent.click(justificationButton);
    expect(screen.getByText(/Problem exhibits recursive structure/)).toBeInTheDocument();

    // Click to hide
    fireEvent.click(justificationButton);
    expect(
      screen.queryByText(/Problem exhibits recursive structure/)
    ).not.toBeInTheDocument();
  });

  it("displays alternative techniques section", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Alternative Techniques Considered (1)")).toBeInTheDocument();
  });

  it("toggles alternative techniques visibility", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);

    const alternativesButton = screen.getByText("Alternative Techniques Considered (1)");

    // Initially hidden
    expect(screen.queryByText("Graph Partitioning")).not.toBeInTheDocument();

    // Click to show
    fireEvent.click(alternativesButton);
    expect(screen.getByText("Graph Partitioning")).toBeInTheDocument();
    expect(screen.getByText("72%")).toBeInTheDocument();

    // Click to hide
    fireEvent.click(alternativesButton);
    expect(screen.queryByText("Graph Partitioning")).not.toBeInTheDocument();
  });

  it("handles multiple paradigms correctly", () => {
    render(<TechniqueSelectionDisplay data={mockMultiParadigmData} />);

    expect(screen.getByText("Structural Decomposition")).toBeInTheDocument();
    expect(screen.getByText("Temporal Decomposition")).toBeInTheDocument();
    expect(screen.getByText("Divide and Conquer")).toBeInTheDocument();
    expect(screen.getByText("Event-Driven Pipeline")).toBeInTheDocument();
    expect(screen.getByText("Total Techniques Selected:")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("shows prerequisites not met badge when prerequisites fail", () => {
    const dataWithFailedPrereqs: TechniqueSelectionData = {
      selectedTechniques: {
        structural: {
          ...mockTechnique,
          prerequisitesStatus: {
            problem_is_divisible: true,
            subproblems_independent: false,
          },
        },
      },
    };

    render(<TechniqueSelectionDisplay data={dataWithFailedPrereqs} />);
    expect(screen.getByText("Prerequisites Not Met")).toBeInTheDocument();
  });

  it("displays summary footer with technique count", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    expect(screen.getByText("Total Techniques Selected:")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("Structural: Divide and Conquer")).toBeInTheDocument();
  });

  it("handles data without alternatives gracefully", () => {
    const dataWithoutAlternatives: TechniqueSelectionData = {
      selectedTechniques: {
        structural: mockTechnique,
      },
    };

    render(<TechniqueSelectionDisplay data={dataWithoutAlternatives} />);
    expect(screen.getByText("Divide and Conquer")).toBeInTheDocument();
    // Should not show alternatives section if none exist
    expect(screen.queryByText(/Alternative Techniques Considered/)).not.toBeInTheDocument();
  });

  it("applies correct score color classes", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);
    const scoreElement = screen.getByText("91%");
    expect(scoreElement).toHaveClass("text-green-700");
  });

  it("has proper accessibility attributes", () => {
    render(<TechniqueSelectionDisplay data={mockData} />);

    // Check for ARIA attributes
    const progressBar = screen.getByRole("progressbar");
    expect(progressBar).toHaveAttribute("aria-valuenow", "91");
    expect(progressBar).toHaveAttribute("aria-valuemin", "0");
    expect(progressBar).toHaveAttribute("aria-valuemax", "100");

    // Check for expandable sections - get the button element
    const justificationButton = screen.getByText("Formal Justification").closest("button");
    expect(justificationButton).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(justificationButton!);
    expect(justificationButton).toHaveAttribute("aria-expanded", "true");
  });

  it("renders with custom className", () => {
    const { container } = render(
      <TechniqueSelectionDisplay data={mockData} className="custom-class" />
    );
    const card = container.querySelector(".custom-class");
    expect(card).toBeInTheDocument();
  });
});
