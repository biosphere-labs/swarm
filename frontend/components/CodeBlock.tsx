/**
 * CodeBlock Component
 *
 * A specialized component for rendering code blocks with:
 * - Syntax highlighting using react-syntax-highlighter
 * - Copy-to-clipboard functionality
 * - Language badge display
 * - Optional line numbers
 * - Theme support (light/dark)
 * - Responsive design
 */

'use client';

import React, { useState, useCallback } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import {
  vscDarkPlus,
  vs,
} from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  extractLanguage,
  getLanguageDisplayName,
  SYNTAX_THEMES,
  type SyntaxTheme,
} from '@/lib/markdown-config';

export interface CodeBlockProps {
  /**
   * The code content to display
   */
  children?: React.ReactNode;

  /**
   * The className from the markdown parser (e.g., 'language-python')
   */
  className?: string;

  /**
   * Whether to show line numbers
   * @default false
   */
  showLineNumbers?: boolean;

  /**
   * Theme for syntax highlighting
   * @default 'dark'
   */
  theme?: SyntaxTheme;

  /**
   * Whether to show the copy button
   * @default true
   */
  showCopyButton?: boolean;

  /**
   * Whether to show the language badge
   * @default true
   */
  showLanguageBadge?: boolean;

  /**
   * Additional CSS classes
   */
  wrapperClassName?: string;

  /**
   * Callback when code is copied
   */
  onCopy?: (code: string) => void;
}

/**
 * CodeBlock - A component for rendering syntax-highlighted code blocks
 *
 * @example
 * ```tsx
 * <CodeBlock className="language-python" showLineNumbers theme="dark">
 *   {`def hello():
 *     print("Hello, world!")`}
 * </CodeBlock>
 * ```
 */
export function CodeBlock({
  children,
  className,
  showLineNumbers = false,
  theme = 'dark',
  showCopyButton = true,
  showLanguageBadge = true,
  wrapperClassName,
  onCopy,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  // Extract code content and language
  const code = String(children).replace(/\n$/, '');
  const language = extractLanguage(className);
  const displayLanguage = language ? getLanguageDisplayName(language) : 'Code';

  // Select syntax highlighting style based on theme
  const syntaxStyle = theme === 'dark' ? vscDarkPlus : vs;

  /**
   * Handle copy to clipboard
   */
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      onCopy?.(code);

      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  }, [code, onCopy]);

  return (
    <div
      className={cn(
        'relative group rounded-lg overflow-hidden my-4',
        'border border-gray-200 dark:border-gray-700',
        wrapperClassName
      )}
      data-testid="code-block"
    >
      {/* Header with language badge and copy button */}
      <div
        className={cn(
          'flex items-center justify-between px-4 py-2',
          'bg-gray-100 dark:bg-gray-800',
          'border-b border-gray-200 dark:border-gray-700'
        )}
      >
        {showLanguageBadge && (
          <div
            className={cn(
              'text-xs font-semibold uppercase tracking-wide',
              'text-gray-600 dark:text-gray-400'
            )}
            data-testid="language-badge"
          >
            {displayLanguage}
          </div>
        )}

        {!showLanguageBadge && <div />}

        {showCopyButton && (
          <button
            onClick={handleCopy}
            className={cn(
              'flex items-center gap-1.5 px-2.5 py-1.5 rounded-md',
              'text-xs font-medium transition-all duration-200',
              'hover:bg-gray-200 dark:hover:bg-gray-700',
              'focus:outline-none focus:ring-2 focus:ring-blue-500',
              copied
                ? 'text-green-600 dark:text-green-400'
                : 'text-gray-600 dark:text-gray-400'
            )}
            aria-label={copied ? 'Copied' : 'Copy code'}
            data-testid="copy-button"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Code content with syntax highlighting */}
      <div className="overflow-x-auto">
        <SyntaxHighlighter
          language={language || 'text'}
          style={syntaxStyle}
          showLineNumbers={showLineNumbers}
          customStyle={{
            margin: 0,
            padding: '1rem',
            background: theme === 'dark' ? '#1e1e1e' : '#ffffff',
            fontSize: '0.875rem',
            lineHeight: '1.5',
          }}
          codeTagProps={{
            className: 'text-sm',
            style: {
              fontFamily:
                'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace',
            },
          }}
          lineNumberStyle={{
            minWidth: '2.5rem',
            paddingRight: '1rem',
            color: theme === 'dark' ? '#858585' : '#6e7781',
            userSelect: 'none',
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}

/**
 * InlineCode - A component for rendering inline code snippets
 *
 * @example
 * ```tsx
 * <InlineCode>const x = 42;</InlineCode>
 * ```
 */
export interface InlineCodeProps {
  children?: React.ReactNode;
  className?: string;
}

export function InlineCode({ children, className }: InlineCodeProps) {
  return (
    <code
      className={cn(
        'px-1.5 py-0.5 rounded-md',
        'bg-gray-100 dark:bg-gray-800',
        'text-gray-800 dark:text-gray-200',
        'font-mono text-sm',
        'border border-gray-200 dark:border-gray-700',
        className
      )}
      data-testid="inline-code"
    >
      {children}
    </code>
  );
}

export default CodeBlock;
