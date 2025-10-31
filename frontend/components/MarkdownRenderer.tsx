/**
 * MarkdownRenderer Component
 *
 * A comprehensive markdown renderer with:
 * - Full GFM (GitHub Flavored Markdown) support
 * - Syntax highlighting for code blocks
 * - Custom styling with Tailwind CSS
 * - Theme support (light/dark)
 * - Responsive design
 * - Accessibility features
 *
 * Supports:
 * - Headings (h1-h6) with auto-generated anchors
 * - Lists (ordered, unordered, task lists)
 * - Code blocks with syntax highlighting
 * - Inline code
 * - Links (with external link handling)
 * - Images (with lazy loading)
 * - Tables (responsive)
 * - Blockquotes
 * - Bold, italic, strikethrough
 * - Horizontal rules
 */

'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Components } from 'react-markdown';
import { cn } from '@/lib/utils';
import {
  baseMarkdownOptions,
  safeMarkdownOptions,
  isExternalUrl,
  generateHeadingSlug,
  preprocessMarkdown,
  type SyntaxTheme,
} from '@/lib/markdown-config';
import { CodeBlock, InlineCode } from './CodeBlock';

export interface MarkdownRendererProps {
  /**
   * The markdown content to render
   */
  content: string;

  /**
   * Additional CSS classes for the wrapper
   */
  className?: string;

  /**
   * Theme for syntax highlighting
   * @default 'dark'
   */
  theme?: SyntaxTheme;

  /**
   * Whether to show line numbers in code blocks
   * @default false
   */
  showLineNumbers?: boolean;

  /**
   * Whether to allow raw HTML in markdown
   * WARNING: Only enable for trusted content to prevent XSS attacks
   * @default false
   */
  allowHtml?: boolean;

  /**
   * Whether to open external links in a new tab
   * @default true
   */
  openLinksInNewTab?: boolean;

  /**
   * Whether to enable lazy loading for images
   * @default true
   */
  lazyLoadImages?: boolean;

  /**
   * Callback when a link is clicked
   */
  onLinkClick?: (href: string, event: React.MouseEvent) => void;

  /**
   * Callback when an image fails to load
   */
  onImageError?: (src: string, error: Event) => void;

  /**
   * Custom components to override default rendering
   */
  components?: Partial<Components>;
}

/**
 * MarkdownRenderer - A feature-rich markdown renderer
 *
 * @example
 * ```tsx
 * // Basic usage
 * <MarkdownRenderer content="# Hello\n\nThis is **markdown**" />
 *
 * // With code highlighting
 * <MarkdownRenderer
 *   content="```python\nprint('hello')\n```"
 *   theme="dark"
 *   showLineNumbers
 * />
 *
 * // In solution display
 * <MarkdownRenderer content={solution.content} theme="dark" />
 * ```
 */
export function MarkdownRenderer({
  content,
  className,
  theme = 'dark',
  showLineNumbers = false,
  allowHtml = false,
  openLinksInNewTab = true,
  lazyLoadImages = true,
  onLinkClick,
  onImageError,
  components: customComponents,
}: MarkdownRendererProps) {
  /**
   * Process markdown content
   */
  const processedContent = useMemo(() => {
    return preprocessMarkdown(content);
  }, [content]);

  /**
   * Custom component renderers for markdown elements
   */
  const components: Partial<Components> = useMemo(
    () => ({
      // Headings with anchor links
      h1: ({ node, children, ...props }) => {
        const text = extractTextFromChildren(children);
        const slug = generateHeadingSlug(text);
        return (
          <h1
            id={slug}
            className={cn(
              'text-4xl font-bold mt-8 mb-4 scroll-mt-20',
              'text-gray-900 dark:text-gray-100',
              'border-b border-gray-200 dark:border-gray-700 pb-2'
            )}
            {...props}
          >
            {children}
          </h1>
        );
      },
      h2: ({ node, children, ...props }) => {
        const text = extractTextFromChildren(children);
        const slug = generateHeadingSlug(text);
        return (
          <h2
            id={slug}
            className={cn(
              'text-3xl font-semibold mt-7 mb-3 scroll-mt-20',
              'text-gray-900 dark:text-gray-100',
              'border-b border-gray-200 dark:border-gray-700 pb-2'
            )}
            {...props}
          >
            {children}
          </h2>
        );
      },
      h3: ({ node, children, ...props }) => {
        const text = extractTextFromChildren(children);
        const slug = generateHeadingSlug(text);
        return (
          <h3
            id={slug}
            className={cn(
              'text-2xl font-semibold mt-6 mb-2 scroll-mt-20',
              'text-gray-900 dark:text-gray-100'
            )}
            {...props}
          >
            {children}
          </h3>
        );
      },
      h4: ({ node, children, ...props }) => {
        const text = extractTextFromChildren(children);
        const slug = generateHeadingSlug(text);
        return (
          <h4
            id={slug}
            className={cn(
              'text-xl font-semibold mt-5 mb-2 scroll-mt-20',
              'text-gray-900 dark:text-gray-100'
            )}
            {...props}
          >
            {children}
          </h4>
        );
      },
      h5: ({ node, children, ...props }) => {
        const text = extractTextFromChildren(children);
        const slug = generateHeadingSlug(text);
        return (
          <h5
            id={slug}
            className={cn(
              'text-lg font-semibold mt-4 mb-2 scroll-mt-20',
              'text-gray-900 dark:text-gray-100'
            )}
            {...props}
          >
            {children}
          </h5>
        );
      },
      h6: ({ node, children, ...props }) => {
        const text = extractTextFromChildren(children);
        const slug = generateHeadingSlug(text);
        return (
          <h6
            id={slug}
            className={cn(
              'text-base font-semibold mt-3 mb-2 scroll-mt-20',
              'text-gray-900 dark:text-gray-100'
            )}
            {...props}
          >
            {children}
          </h6>
        );
      },

      // Paragraphs
      p: ({ node, children, ...props }) => (
        <p
          className={cn(
            'mb-4 leading-7',
            'text-gray-700 dark:text-gray-300'
          )}
          {...props}
        >
          {children}
        </p>
      ),

      // Lists
      ul: ({ node, children, ...props }) => (
        <ul
          className={cn(
            'mb-4 ml-6 list-disc space-y-2',
            'text-gray-700 dark:text-gray-300'
          )}
          {...props}
        >
          {children}
        </ul>
      ),
      ol: ({ node, children, ...props }) => (
        <ol
          className={cn(
            'mb-4 ml-6 list-decimal space-y-2',
            'text-gray-700 dark:text-gray-300'
          )}
          {...props}
        >
          {children}
        </ol>
      ),
      li: ({ node, children, ...props }) => (
        <li className="leading-7" {...props}>
          {children}
        </li>
      ),

      // Code blocks and inline code
      code: ({ node, inline, className, children, ...props }) => {
        if (inline) {
          return <InlineCode className={className}>{children}</InlineCode>;
        }

        return (
          <CodeBlock
            className={className}
            showLineNumbers={showLineNumbers}
            theme={theme}
          >
            {children}
          </CodeBlock>
        );
      },

      // Pre blocks (wrapping code blocks)
      pre: ({ node, children, ...props }) => (
        <div className="my-4" {...props}>
          {children}
        </div>
      ),

      // Links
      a: ({ node, href, children, ...props }) => {
        const isExternal = href ? isExternalUrl(href) : false;
        const targetProps =
          openLinksInNewTab && isExternal
            ? { target: '_blank', rel: 'noopener noreferrer' }
            : {};

        return (
          <a
            href={href}
            className={cn(
              'text-blue-600 dark:text-blue-400 hover:underline',
              'font-medium transition-colors duration-200'
            )}
            onClick={(e) => {
              if (onLinkClick && href) {
                onLinkClick(href, e);
              }
            }}
            {...targetProps}
            {...props}
          >
            {children}
          </a>
        );
      },

      // Images
      img: ({ node, src, alt, ...props }) => {
        const loadingProps = lazyLoadImages ? { loading: 'lazy' as const } : {};

        return (
          <img
            src={src}
            alt={alt || ''}
            className={cn(
              'max-w-full h-auto rounded-lg my-4',
              'border border-gray-200 dark:border-gray-700'
            )}
            onError={(e) => {
              if (onImageError && src) {
                onImageError(src, e.nativeEvent);
              }
            }}
            {...loadingProps}
            {...props}
          />
        );
      },

      // Blockquotes
      blockquote: ({ node, children, ...props }) => (
        <blockquote
          className={cn(
            'border-l-4 border-blue-500 pl-4 my-4 italic',
            'bg-gray-50 dark:bg-gray-800 py-2',
            'text-gray-700 dark:text-gray-300'
          )}
          {...props}
        >
          {children}
        </blockquote>
      ),

      // Tables
      table: ({ node, children, ...props }) => (
        <div className="overflow-x-auto my-4">
          <table
            className={cn(
              'min-w-full divide-y divide-gray-200 dark:divide-gray-700',
              'border border-gray-200 dark:border-gray-700 rounded-lg'
            )}
            {...props}
          >
            {children}
          </table>
        </div>
      ),
      thead: ({ node, children, ...props }) => (
        <thead
          className="bg-gray-50 dark:bg-gray-800"
          {...props}
        >
          {children}
        </thead>
      ),
      tbody: ({ node, children, ...props }) => (
        <tbody
          className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700"
          {...props}
        >
          {children}
        </tbody>
      ),
      tr: ({ node, children, ...props }) => (
        <tr {...props}>{children}</tr>
      ),
      th: ({ node, children, ...props }) => (
        <th
          className={cn(
            'px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider',
            'text-gray-700 dark:text-gray-300'
          )}
          {...props}
        >
          {children}
        </th>
      ),
      td: ({ node, children, ...props }) => (
        <td
          className={cn(
            'px-4 py-3 text-sm',
            'text-gray-700 dark:text-gray-300'
          )}
          {...props}
        >
          {children}
        </td>
      ),

      // Horizontal rule
      hr: ({ node, ...props }) => (
        <hr
          className="my-8 border-t border-gray-300 dark:border-gray-600"
          {...props}
        />
      ),

      // Text formatting
      strong: ({ node, children, ...props }) => (
        <strong className="font-bold text-gray-900 dark:text-gray-100" {...props}>
          {children}
        </strong>
      ),
      em: ({ node, children, ...props }) => (
        <em className="italic" {...props}>
          {children}
        </em>
      ),
      del: ({ node, children, ...props }) => (
        <del className="line-through text-gray-500 dark:text-gray-400" {...props}>
          {children}
        </del>
      ),

      // Merge with custom components
      ...customComponents,
    }),
    [
      theme,
      showLineNumbers,
      openLinksInNewTab,
      lazyLoadImages,
      onLinkClick,
      onImageError,
      customComponents,
    ]
  );

  /**
   * Select markdown options based on allowHtml setting
   */
  const markdownOptions = allowHtml ? baseMarkdownOptions : safeMarkdownOptions;

  return (
    <div
      className={cn(
        'markdown-renderer prose dark:prose-invert max-w-none',
        className
      )}
      data-testid="markdown-renderer"
    >
      <ReactMarkdown
        {...markdownOptions}
        components={components}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
}

/**
 * Extract plain text from React children
 * Used for generating heading slugs
 */
function extractTextFromChildren(children: React.ReactNode): string {
  if (typeof children === 'string') {
    return children;
  }

  if (Array.isArray(children)) {
    return children.map(extractTextFromChildren).join('');
  }

  if (React.isValidElement(children) && children.props.children) {
    return extractTextFromChildren(children.props.children);
  }

  return '';
}

export default MarkdownRenderer;
