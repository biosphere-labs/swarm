const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^react-syntax-highlighter$': '<rootDir>/__mocks__/react-syntax-highlighter.tsx',
    '^react-syntax-highlighter/dist/esm/(.*)$': '<rootDir>/__mocks__/react-syntax-highlighter.tsx',
    '^react-markdown$': '<rootDir>/__mocks__/react-markdown.tsx',
    '^remark-gfm$': '<rootDir>/__mocks__/remark-gfm.ts',
    '^rehype-raw$': '<rootDir>/__mocks__/rehype-raw.ts',
  },
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
  transformIgnorePatterns: [
    'node_modules/(?!(react-markdown|remark-gfm|rehype-raw|unified|unist-util-visit|unist-util-is|vfile|micromark|decode-named-character-reference|character-entities|trim-lines|mdast-util-to-hast|hast-util-raw|hast-util-from-parse5|parse5)/)',
  ],
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
