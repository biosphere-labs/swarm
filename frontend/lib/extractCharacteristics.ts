/**
 * Extract problem characteristics from problem description text
 * Uses pattern matching and heuristics to identify key attributes
 */

export interface ProblemCharacteristics {
  // Size characteristics
  size: {
    estimated: string; // small, medium, large, very large
    linesOfCode?: number;
    confidence: number;
  };

  // Complexity indicators
  complexity: {
    level: string; // low, medium, high, very high
    factors: string[];
    confidence: number;
  };

  // Structure detection
  structure: {
    types: string[]; // graph, hierarchy, sequence, spatial, etc.
    confidence: number;
  };

  // Resource requirements
  resources: {
    compute: string; // low, medium, high
    memory: string; // low, medium, high
    realTime: boolean;
    distributed: boolean;
    confidence: number;
  };

  // Domain hints
  domains: {
    detected: string[]; // api, data, ml, security, frontend, backend, etc.
    confidence: number;
  };

  // Constraints
  constraints: {
    timing: string[];
    dependencies: string[];
    technical: string[];
    confidence: number;
  };
}

// Keywords for different characteristics
const KEYWORDS = {
  size: {
    small: ['simple', 'basic', 'minimal', 'small', 'quick', 'single'],
    medium: ['standard', 'typical', 'moderate', 'several', 'multiple'],
    large: ['complex', 'large', 'extensive', 'comprehensive', 'full-featured'],
    veryLarge: ['enterprise', 'massive', 'distributed', 'scalable', 'platform'],
  },
  complexity: {
    algorithms: ['algorithm', 'optimize', 'efficient', 'performance', 'complexity'],
    integration: ['integrate', 'connect', 'sync', 'api', 'webhook', 'interface'],
    concurrent: ['concurrent', 'parallel', 'async', 'multi-threaded', 'race condition'],
    realTime: ['real-time', 'live', 'instant', 'streaming', 'websocket'],
    distributed: ['distributed', 'microservices', 'cluster', 'sharding', 'replication'],
  },
  structure: {
    graph: ['graph', 'network', 'node', 'edge', 'relationship', 'connection'],
    hierarchy: ['hierarchy', 'tree', 'parent', 'child', 'nested', 'level'],
    sequence: ['sequence', 'order', 'pipeline', 'stage', 'step', 'flow'],
    spatial: ['spatial', 'coordinate', 'location', 'geographic', 'map', 'region'],
    temporal: ['temporal', 'time', 'schedule', 'timeline', 'event', 'historical'],
  },
  resources: {
    highCompute: ['compute', 'calculation', 'processing', 'cpu', 'gpu', 'simulation'],
    highMemory: ['memory', 'cache', 'buffer', 'large dataset', 'in-memory'],
    realTime: ['real-time', 'live', 'instant', 'immediate', 'streaming'],
    distributed: ['distributed', 'cluster', 'multi-server', 'cloud', 'scalable'],
  },
  domains: {
    api: ['api', 'rest', 'graphql', 'endpoint', 'http', 'service'],
    data: ['database', 'data', 'storage', 'query', 'sql', 'nosql', 'persistence'],
    ml: ['machine learning', 'ml', 'ai', 'model', 'training', 'prediction', 'neural'],
    security: ['security', 'auth', 'authentication', 'authorization', 'encrypt', 'secure'],
    frontend: ['ui', 'interface', 'frontend', 'react', 'vue', 'angular', 'web app'],
    backend: ['backend', 'server', 'api', 'microservice', 'service'],
    mobile: ['mobile', 'ios', 'android', 'app', 'native'],
  },
  constraints: {
    performance: ['performance', 'fast', 'speed', 'latency', 'throughput'],
    scalability: ['scalable', 'scale', 'growth', 'load'],
    reliability: ['reliable', 'fault-tolerant', 'available', 'uptime'],
    security: ['secure', 'encrypted', 'safe', 'protected'],
  },
};

/**
 * Extract characteristics from problem description
 */
export function extractCharacteristics(problemText: string): ProblemCharacteristics {
  const lowerText = problemText.toLowerCase();
  const words = lowerText.split(/\s+/);
  const wordCount = words.length;

  // Estimate size based on description length and keywords
  const size = estimateSize(lowerText, wordCount);

  // Detect complexity
  const complexity = detectComplexity(lowerText);

  // Detect structure types
  const structure = detectStructure(lowerText);

  // Estimate resource requirements
  const resources = estimateResources(lowerText);

  // Detect domains
  const domains = detectDomains(lowerText);

  // Extract constraints
  const constraints = extractConstraints(lowerText);

  return {
    size,
    complexity,
    structure,
    resources,
    domains,
    constraints,
  };
}

function estimateSize(text: string, wordCount: number): ProblemCharacteristics['size'] {
  let score = 0;
  let matchCount = 0;

  // Check keywords
  Object.entries(KEYWORDS.size).forEach(([sizeType, keywords]) => {
    keywords.forEach((keyword) => {
      if (text.includes(keyword)) {
        matchCount++;
        if (sizeType === 'small') score += 1;
        else if (sizeType === 'medium') score += 2;
        else if (sizeType === 'large') score += 3;
        else if (sizeType === 'veryLarge') score += 4;
      }
    });
  });

  // Factor in description length
  if (wordCount < 20) score += 0.5;
  else if (wordCount < 50) score += 1;
  else if (wordCount < 100) score += 2;
  else score += 3;

  // Determine size category
  let estimated: string;
  let linesOfCode: number | undefined;

  if (score < 2) {
    estimated = 'small';
    linesOfCode = 500;
  } else if (score < 4) {
    estimated = 'medium';
    linesOfCode = 2000;
  } else if (score < 6) {
    estimated = 'large';
    linesOfCode = 5000;
  } else {
    estimated = 'very large';
    linesOfCode = 10000;
  }

  const confidence = Math.min(0.3 + (matchCount * 0.1), 0.9);

  return { estimated, linesOfCode, confidence };
}

function detectComplexity(text: string): ProblemCharacteristics['complexity'] {
  const factors: string[] = [];
  let score = 0;

  Object.entries(KEYWORDS.complexity).forEach(([factor, keywords]) => {
    const hasMatch = keywords.some((keyword) => text.includes(keyword));
    if (hasMatch) {
      factors.push(factor);
      score++;
    }
  });

  let level: string;
  if (score === 0) level = 'low';
  else if (score === 1) level = 'medium';
  else if (score === 2) level = 'high';
  else level = 'very high';

  const confidence = Math.min(0.4 + (factors.length * 0.15), 0.9);

  return { level, factors, confidence };
}

function detectStructure(text: string): ProblemCharacteristics['structure'] {
  const types: string[] = [];

  Object.entries(KEYWORDS.structure).forEach(([structType, keywords]) => {
    const hasMatch = keywords.some((keyword) => text.includes(keyword));
    if (hasMatch) {
      types.push(structType);
    }
  });

  // Default to functional if no structure detected
  if (types.length === 0) {
    types.push('functional');
  }

  const confidence = Math.min(0.4 + (types.length * 0.2), 0.9);

  return { types, confidence };
}

function estimateResources(text: string): ProblemCharacteristics['resources'] {
  let computeScore = 0;
  let memoryScore = 0;
  let realTime = false;
  let distributed = false;

  KEYWORDS.resources.highCompute.forEach((keyword) => {
    if (text.includes(keyword)) computeScore++;
  });

  KEYWORDS.resources.highMemory.forEach((keyword) => {
    if (text.includes(keyword)) memoryScore++;
  });

  KEYWORDS.resources.realTime.forEach((keyword) => {
    if (text.includes(keyword)) realTime = true;
  });

  KEYWORDS.resources.distributed.forEach((keyword) => {
    if (text.includes(keyword)) distributed = true;
  });

  const compute = computeScore === 0 ? 'low' : computeScore === 1 ? 'medium' : 'high';
  const memory = memoryScore === 0 ? 'low' : memoryScore === 1 ? 'medium' : 'high';

  const confidence = 0.6;

  return { compute, memory, realTime, distributed, confidence };
}

function detectDomains(text: string): ProblemCharacteristics['domains'] {
  const detected: string[] = [];

  Object.entries(KEYWORDS.domains).forEach(([domain, keywords]) => {
    const hasMatch = keywords.some((keyword) => text.includes(keyword));
    if (hasMatch) {
      detected.push(domain);
    }
  });

  const confidence = Math.min(0.5 + (detected.length * 0.1), 0.9);

  return { detected, confidence };
}

function extractConstraints(text: string): ProblemCharacteristics['constraints'] {
  const timing: string[] = [];
  const dependencies: string[] = [];
  const technical: string[] = [];

  // Extract performance constraints
  Object.entries(KEYWORDS.constraints).forEach(([constraint, keywords]) => {
    keywords.forEach((keyword) => {
      if (text.includes(keyword)) {
        technical.push(`${constraint}: ${keyword}`);
      }
    });
  });

  // Look for explicit timing mentions
  const timeMatches = text.match(/(\d+)\s*(ms|millisecond|second|minute|hour)/gi);
  if (timeMatches) {
    timing.push(...timeMatches);
  }

  // Look for dependency mentions
  const depKeywords = ['depends on', 'requires', 'needs', 'must have', 'prerequisite'];
  depKeywords.forEach((keyword) => {
    if (text.includes(keyword)) {
      dependencies.push(keyword);
    }
  });

  const confidence = 0.5;

  return { timing, dependencies, technical, confidence };
}
