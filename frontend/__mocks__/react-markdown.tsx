/**
 * Mock for react-markdown
 * Used in Jest tests to avoid ESM issues
 */

import React from 'react';

const ReactMarkdown = ({ children, components, ...props }: any) => {
  const content = typeof children === 'string' ? children : '';

  // Parse markdown into React elements
  const parseMarkdown = (md: string): React.ReactNode => {
    const elements: React.ReactNode[] = [];
    const lines = md.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Code blocks
      if (line.startsWith('```')) {
        const language = line.slice(3);
        const codeLines = [];
        i++;
        while (i < lines.length && !lines[i].startsWith('```')) {
          codeLines.push(lines[i]);
          i++;
        }
        const code = codeLines.join('\n');
        const CodeComponent = components?.code || 'code';
        elements.push(
          React.createElement(CodeComponent, {
            key: i,
            inline: false,
            className: language ? `language-${language}` : '',
            children: code,
          })
        );
        continue;
      }

      // Headings
      const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        const level = headingMatch[1].length as 1 | 2 | 3 | 4 | 5 | 6;
        const text = headingMatch[2];
        const tag = `h${level}` as 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
        const Component = components?.[tag] || tag;
        elements.push(
          React.createElement(Component, { key: i, children: text })
        );
        continue;
      }

      // Lists
      if (line.match(/^[-*]\s+(.+)$/)) {
        const text = line.replace(/^[-*]\s+/, '');
        const Li = components?.li || 'li';
        elements.push(
          React.createElement(Li, { key: i, children: text })
        );
        continue;
      }

      // Links
      const linkMatch = line.match(/\[([^\]]+)\]\(([^)]+)\)/);
      if (linkMatch) {
        const text = linkMatch[1];
        const href = linkMatch[2];
        const A = components?.a || 'a';
        elements.push(
          React.createElement(A, { key: i, href, children: text })
        );
        continue;
      }

      // Images
      const imgMatch = line.match(/!\[([^\]]*)\]\(([^)]+)\)/);
      if (imgMatch) {
        const alt = imgMatch[1];
        const src = imgMatch[2];
        const Img = components?.img || 'img';
        elements.push(
          React.createElement(Img, { key: i, src, alt })
        );
        continue;
      }

      // Inline code
      const inlineCodeMatch = line.match(/`([^`]+)`/);
      if (inlineCodeMatch) {
        const code = inlineCodeMatch[1];
        const before = line.substring(0, inlineCodeMatch.index);
        const after = line.substring(inlineCodeMatch.index! + inlineCodeMatch[0].length);
        const CodeComponent = components?.code || 'code';
        elements.push(
          <span key={i}>
            {before}
            {React.createElement(CodeComponent, { inline: true, children: code })}
            {after}
          </span>
        );
        continue;
      }

      // Bold
      const boldMatch = line.match(/\*\*([^*]+)\*\*/);
      if (boldMatch) {
        const text = boldMatch[1];
        const Strong = components?.strong || 'strong';
        elements.push(
          React.createElement(Strong, { key: i, children: text })
        );
        continue;
      }

      // Italic
      const italicMatch = line.match(/[_]([^_]+)[_]/);
      if (italicMatch) {
        const text = italicMatch[1];
        const Em = components?.em || 'em';
        elements.push(
          React.createElement(Em, { key: i, children: text })
        );
        continue;
      }

      // Strikethrough
      const strikeMatch = line.match(/~~([^~]+)~~/);
      if (strikeMatch) {
        const text = strikeMatch[1];
        const Del = components?.del || 'del';
        elements.push(
          React.createElement(Del, { key: i, children: text })
        );
        continue;
      }

      // Blockquote
      if (line.startsWith('> ')) {
        const text = line.slice(2);
        const Blockquote = components?.blockquote || 'blockquote';
        elements.push(
          React.createElement(Blockquote, { key: i, children: text })
        );
        continue;
      }

      // Regular paragraph
      if (line.trim()) {
        const P = components?.p || 'p';
        elements.push(
          React.createElement(P, { key: i, children: line })
        );
      }
    }

    return elements;
  };

  return (
    <div data-testid="markdown-renderer" {...props}>
      {parseMarkdown(content)}
    </div>
  );
};

export default ReactMarkdown;
export { ReactMarkdown };
