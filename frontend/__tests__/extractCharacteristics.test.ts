import { extractCharacteristics } from '@/lib/extractCharacteristics';

describe('extractCharacteristics', () => {
  describe('Size Estimation', () => {
    it('should estimate small size for simple problems', () => {
      const result = extractCharacteristics('Build a simple calculator');

      expect(result.size.estimated).toBe('small');
      expect(result.size.linesOfCode).toBeLessThan(1000);
      expect(result.size.confidence).toBeGreaterThan(0);
    });

    it('should estimate large size for complex problems', () => {
      const result = extractCharacteristics(
        'Build a comprehensive enterprise-level distributed system with extensive features and scalable architecture'
      );

      expect(['large', 'very large']).toContain(result.size.estimated);
      expect(result.size.linesOfCode).toBeGreaterThan(2000);
    });

    it('should factor in description length', () => {
      const shortDesc = extractCharacteristics('Simple app');
      const longDesc = extractCharacteristics(
        'This is a very detailed and extensive description of a complex problem that requires significant implementation effort and involves multiple components, systems, and integrations across various platforms and technologies'
      );

      expect(longDesc.size.linesOfCode).toBeGreaterThan(shortDesc.size.linesOfCode || 0);
    });
  });

  describe('Complexity Detection', () => {
    it('should detect low complexity for simple problems', () => {
      const result = extractCharacteristics('Create a basic TODO list');

      expect(result.complexity.level).toBe('low');
      expect(result.complexity.factors).toHaveLength(0);
    });

    it('should detect high complexity for algorithmic problems', () => {
      const result = extractCharacteristics(
        'Build a system with complex algorithms, real-time processing, and parallel execution'
      );

      expect(['high', 'very high']).toContain(result.complexity.level);
      expect(result.complexity.factors.length).toBeGreaterThan(0);
    });

    it('should identify specific complexity factors', () => {
      const result = extractCharacteristics(
        'System needs efficient algorithms and real-time concurrent processing'
      );

      expect(result.complexity.factors).toEqual(
        expect.arrayContaining(['algorithms', 'realTime', 'concurrent'])
      );
    });

    it('should detect integration complexity', () => {
      const result = extractCharacteristics(
        'Integrate with multiple external APIs and sync data between systems'
      );

      expect(result.complexity.factors).toContain('integration');
    });

    it('should detect distributed system complexity', () => {
      const result = extractCharacteristics(
        'Build a distributed microservices architecture with clustering'
      );

      expect(result.complexity.factors).toContain('distributed');
    });
  });

  describe('Structure Detection', () => {
    it('should detect graph structure', () => {
      const result = extractCharacteristics(
        'Build a social network with nodes and edges representing relationships'
      );

      expect(result.structure.types).toContain('graph');
    });

    it('should detect hierarchical structure', () => {
      const result = extractCharacteristics(
        'Create a file system with parent-child hierarchy and nested folders'
      );

      expect(result.structure.types).toContain('hierarchy');
    });

    it('should detect sequence structure', () => {
      const result = extractCharacteristics('Build a pipeline with sequential stages and ordered steps');

      expect(result.structure.types).toContain('sequence');
    });

    it('should detect temporal structure', () => {
      const result = extractCharacteristics('System needs to track events over time with historical data');

      expect(result.structure.types).toContain('temporal');
    });

    it('should detect spatial structure', () => {
      const result = extractCharacteristics('Build a map application with geographic coordinates and regions');

      expect(result.structure.types).toContain('spatial');
    });

    it('should detect multiple structures', () => {
      const result = extractCharacteristics(
        'Build a system with graph relationships, tree hierarchy with parent-child levels, and temporal events'
      );

      expect(result.structure.types.length).toBeGreaterThan(1);
      expect(result.structure.types).toEqual(
        expect.arrayContaining(['graph', 'hierarchy', 'temporal'])
      );
    });

    it('should default to functional when no structure detected', () => {
      const result = extractCharacteristics('Build an application');

      expect(result.structure.types).toContain('functional');
    });
  });

  describe('Resource Requirements', () => {
    it('should detect high compute requirements', () => {
      const result = extractCharacteristics(
        'System requires intensive CPU processing and complex calculations'
      );

      expect(result.resources.compute).toBe('high');
    });

    it('should detect high memory requirements', () => {
      const result = extractCharacteristics('Process large datasets in-memory with extensive caching');

      expect(result.resources.memory).toBe('high');
    });

    it('should detect real-time requirements', () => {
      const result = extractCharacteristics('Build a real-time streaming system with live updates');

      expect(result.resources.realTime).toBe(true);
    });

    it('should detect distributed requirements', () => {
      const result = extractCharacteristics('Build a distributed cluster with multiple servers');

      expect(result.resources.distributed).toBe(true);
    });

    it('should default to low for simple problems', () => {
      const result = extractCharacteristics('Create a simple form');

      expect(result.resources.compute).toBe('low');
      expect(result.resources.memory).toBe('low');
      expect(result.resources.realTime).toBe(false);
      expect(result.resources.distributed).toBe(false);
    });
  });

  describe('Domain Detection', () => {
    it('should detect API domain', () => {
      const result = extractCharacteristics('Build a REST API with GraphQL endpoints');

      expect(result.domains.detected).toContain('api');
    });

    it('should detect data domain', () => {
      const result = extractCharacteristics('Create a database system with SQL queries and data storage');

      expect(result.domains.detected).toContain('data');
    });

    it('should detect ML domain', () => {
      const result = extractCharacteristics('Build a machine learning model with neural network training');

      expect(result.domains.detected).toContain('ml');
    });

    it('should detect security domain', () => {
      const result = extractCharacteristics('System needs authentication, authorization, and encryption');

      expect(result.domains.detected).toContain('security');
    });

    it('should detect frontend domain', () => {
      const result = extractCharacteristics('Build a React UI with interactive interface');

      expect(result.domains.detected).toContain('frontend');
    });

    it('should detect backend domain', () => {
      const result = extractCharacteristics('Create a backend server with microservices');

      expect(result.domains.detected).toContain('backend');
    });

    it('should detect mobile domain', () => {
      const result = extractCharacteristics('Build an iOS and Android mobile app');

      expect(result.domains.detected).toContain('mobile');
    });

    it('should detect multiple domains', () => {
      const result = extractCharacteristics(
        'Build a full-stack application with React frontend, REST API backend, and database storage'
      );

      expect(result.domains.detected.length).toBeGreaterThan(1);
      expect(result.domains.detected).toEqual(
        expect.arrayContaining(['frontend', 'api', 'backend', 'data'])
      );
    });
  });

  describe('Constraint Extraction', () => {
    it('should extract timing constraints', () => {
      const result = extractCharacteristics('System must respond within 100ms and process data in 2 seconds');

      expect(result.constraints.timing.length).toBeGreaterThan(0);
      expect(result.constraints.timing.some((t) => t.includes('100'))).toBe(true);
    });

    it('should detect dependency constraints', () => {
      const result = extractCharacteristics('System depends on external services and requires authentication');

      expect(result.constraints.dependencies.length).toBeGreaterThan(0);
    });

    it('should detect technical constraints', () => {
      const result = extractCharacteristics(
        'Must be fast, scalable, secure, and highly available'
      );

      expect(result.constraints.technical.length).toBeGreaterThan(0);
    });
  });

  describe('Confidence Levels', () => {
    it('should provide confidence scores for all characteristics', () => {
      const result = extractCharacteristics('Build a complex distributed system');

      expect(result.size.confidence).toBeGreaterThan(0);
      expect(result.size.confidence).toBeLessThanOrEqual(1);

      expect(result.complexity.confidence).toBeGreaterThan(0);
      expect(result.complexity.confidence).toBeLessThanOrEqual(1);

      expect(result.structure.confidence).toBeGreaterThan(0);
      expect(result.structure.confidence).toBeLessThanOrEqual(1);

      expect(result.resources.confidence).toBeGreaterThan(0);
      expect(result.resources.confidence).toBeLessThanOrEqual(1);

      expect(result.domains.confidence).toBeGreaterThan(0);
      expect(result.domains.confidence).toBeLessThanOrEqual(1);

      expect(result.constraints.confidence).toBeGreaterThan(0);
      expect(result.constraints.confidence).toBeLessThanOrEqual(1);
    });

    it('should increase confidence with more matches', () => {
      const simple = extractCharacteristics('Build an app');
      const detailed = extractCharacteristics(
        'Build a complex distributed real-time system with graph structure, hierarchical organization, API integration, database storage, and machine learning models'
      );

      // Detailed description should have higher confidence in some areas
      expect(detailed.structure.confidence).toBeGreaterThanOrEqual(simple.structure.confidence);
      expect(detailed.domains.confidence).toBeGreaterThanOrEqual(simple.domains.confidence);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty string', () => {
      const result = extractCharacteristics('');

      expect(result).toBeDefined();
      expect(result.size).toBeDefined();
      expect(result.complexity).toBeDefined();
    });

    it('should handle very short text', () => {
      const result = extractCharacteristics('App');

      expect(result.size.estimated).toBe('small');
    });

    it('should handle text with special characters', () => {
      const result = extractCharacteristics('Build a system @#$% with <html> & special chars');

      expect(result).toBeDefined();
    });

    it('should handle text with numbers', () => {
      const result = extractCharacteristics('System must handle 1000000 records with 99.9% uptime');

      expect(result).toBeDefined();
    });

    it('should be case insensitive', () => {
      const lower = extractCharacteristics('build a real-time distributed graph system');
      const upper = extractCharacteristics('BUILD A REAL-TIME DISTRIBUTED GRAPH SYSTEM');

      expect(lower.resources.realTime).toBe(upper.resources.realTime);
      expect(lower.resources.distributed).toBe(upper.resources.distributed);
      expect(lower.structure.types).toEqual(upper.structure.types);
    });
  });

  describe('Real-World Examples', () => {
    it('should analyze a collaborative editor problem', () => {
      const result = extractCharacteristics(
        'Build a real-time collaborative text editor with efficient algorithms, conflict resolution, parallel processing, supporting multiple concurrent users editing the same document simultaneously. The system should handle operational transformations, maintain version history, and provide cursor tracking.'
      );

      expect(result.size.estimated).toMatch(/medium|large/);
      expect(result.complexity.level).toMatch(/medium|high|very high/);
      expect(result.resources.realTime).toBe(true);
      expect(result.structure.types.length).toBeGreaterThan(0);
      expect(result.domains.detected.length).toBeGreaterThan(0);
    });

    it('should analyze a e-commerce platform problem', () => {
      const result = extractCharacteristics(
        'Create a scalable e-commerce platform with API services, database storage, payment processing, order management, machine learning recommendations, and user authentication with encryption. Must handle high traffic and provide real-time inventory updates.'
      );

      expect(result.size.estimated).toMatch(/large|very large/);
      expect(result.resources.distributed).toBe(true);
      expect(result.resources.realTime).toBe(true);
      expect(result.domains.detected.length).toBeGreaterThan(2);
      expect(result.domains.detected).toContain('security');
    });

    it('should analyze a data processing pipeline problem', () => {
      const result = extractCharacteristics(
        'Build a data processing pipeline that ingests large datasets, performs transformations, applies machine learning models, and outputs results to a database. Must be efficient and handle parallel processing.'
      );

      expect(result.complexity.factors).toEqual(expect.arrayContaining(['algorithms']));
      expect(result.domains.detected).toContain('data');
      expect(result.domains.detected).toContain('ml');
      expect(result.structure.types).toContain('sequence');
    });
  });
});
