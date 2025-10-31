/**
 * Markdown Configuration
 *
 * This module provides configuration for react-markdown, including:
 * - Rehype and remark plugins for extended markdown support
 * - Syntax highlighting themes for code blocks
 * - Custom component mappings
 * - Utility functions for markdown processing
 */

import { Options } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

/**
 * Available syntax highlighting themes
 */
export const SYNTAX_THEMES = {
  light: 'github',
  dark: 'vscode-dark',
} as const;

export type SyntaxTheme = keyof typeof SYNTAX_THEMES;

/**
 * Base react-markdown configuration
 * Includes GFM (GitHub Flavored Markdown) support and HTML support
 */
export const baseMarkdownOptions: Partial<Options> = {
  remarkPlugins: [remarkGfm],
  rehypePlugins: [rehypeRaw as any],
};

/**
 * Configuration for markdown parsing with HTML support disabled
 */
export const safeMarkdownOptions: Partial<Options> = {
  remarkPlugins: [remarkGfm],
  // No rehypeRaw plugin - HTML will be escaped
};

/**
 * Extracts the language from a code block className
 * @param className - The className string from a code element
 * @returns The language identifier or empty string
 *
 * @example
 * extractLanguage('language-python') // 'python'
 * extractLanguage('language-typescript') // 'typescript'
 */
export function extractLanguage(className?: string): string {
  if (!className) return '';
  const match = className.match(/language-(\w+)/);
  return match ? match[1] : '';
}

/**
 * Gets the display name for a language
 * @param language - The language identifier
 * @returns A human-readable language name
 *
 * @example
 * getLanguageDisplayName('ts') // 'TypeScript'
 * getLanguageDisplayName('py') // 'Python'
 */
export function getLanguageDisplayName(language: string): string {
  const languageMap: Record<string, string> = {
    js: 'JavaScript',
    ts: 'TypeScript',
    jsx: 'JSX',
    tsx: 'TSX',
    py: 'Python',
    rb: 'Ruby',
    go: 'Go',
    rs: 'Rust',
    java: 'Java',
    cpp: 'C++',
    c: 'C',
    cs: 'C#',
    php: 'PHP',
    swift: 'Swift',
    kt: 'Kotlin',
    sql: 'SQL',
    sh: 'Shell',
    bash: 'Bash',
    yaml: 'YAML',
    yml: 'YAML',
    json: 'JSON',
    xml: 'XML',
    html: 'HTML',
    css: 'CSS',
    scss: 'SCSS',
    md: 'Markdown',
    docker: 'Dockerfile',
    dockerfile: 'Dockerfile',
  };

  return languageMap[language.toLowerCase()] || language.toUpperCase();
}

/**
 * Determines if a URL is external
 * @param url - The URL to check
 * @returns True if the URL is external
 */
export function isExternalUrl(url: string): boolean {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    // Relative URLs will throw, which means they're internal
    return false;
  }
}

/**
 * Generates a slug from heading text for anchor links
 * @param text - The heading text
 * @returns A URL-safe slug
 *
 * @example
 * generateHeadingSlug('Hello World') // 'hello-world'
 * generateHeadingSlug('API Reference (v2)') // 'api-reference-v2'
 */
export function generateHeadingSlug(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
    .trim();
}

/**
 * Processes markdown content before rendering
 * Can be used to add custom transformations
 * @param content - The raw markdown content
 * @returns Processed markdown content
 */
export function preprocessMarkdown(content: string): string {
  // Add any pre-processing transformations here
  // For now, just return the content as-is
  return content;
}

/**
 * Configuration for different markdown rendering contexts
 */
export const markdownContexts = {
  /**
   * Configuration for rendering user-submitted content
   * More restrictive to prevent XSS attacks
   */
  userContent: {
    allowHtml: false,
    options: safeMarkdownOptions,
  },

  /**
   * Configuration for rendering trusted content (e.g., documentation)
   * Allows HTML for more flexibility
   */
  trustedContent: {
    allowHtml: true,
    options: baseMarkdownOptions,
  },

  /**
   * Configuration for rendering solution/code content
   * Optimized for technical documentation
   */
  solutionContent: {
    allowHtml: false,
    options: baseMarkdownOptions,
  },
} as const;

export type MarkdownContext = keyof typeof markdownContexts;
