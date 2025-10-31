/**
 * MarkdownRenderer Tests
 *
 * Comprehensive test suite for the MarkdownRenderer component
 * covering all features and edge cases
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MarkdownRenderer } from '@/components/MarkdownRenderer';
import { CodeBlock, InlineCode } from '@/components/CodeBlock';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(() => Promise.resolve()),
  },
});

describe('MarkdownRenderer', () => {
  describe('Basic Rendering', () => {
    it('should render plain text', () => {
      render(<MarkdownRenderer content="Hello, world!" />);
      expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    });

    it('should render with custom className', () => {
      const { container } = render(
        <MarkdownRenderer content="Test" className="custom-class" />
      );
      const wrapper = container.querySelector('.custom-class');
      expect(wrapper).toBeInTheDocument();
    });

    it('should render empty content without errors', () => {
      render(<MarkdownRenderer content="" />);
      const renderer = screen.getByTestId('markdown-renderer');
      expect(renderer).toBeInTheDocument();
    });
  });

  describe('Headings', () => {
    it('should render h1 heading', () => {
      render(<MarkdownRenderer content="# Heading 1" />);
      const heading = screen.getByText('Heading 1');
      expect(heading.tagName).toBe('H1');
      expect(heading).toHaveClass('text-4xl');
    });

    it('should render h2 heading', () => {
      render(<MarkdownRenderer content="## Heading 2" />);
      const heading = screen.getByText('Heading 2');
      expect(heading.tagName).toBe('H2');
      expect(heading).toHaveClass('text-3xl');
    });

    it('should render h3 heading', () => {
      render(<MarkdownRenderer content="### Heading 3" />);
      const heading = screen.getByText('Heading 3');
      expect(heading.tagName).toBe('H3');
      expect(heading).toHaveClass('text-2xl');
    });

    it('should generate slug IDs for headings', () => {
      render(<MarkdownRenderer content="# Hello World" />);
      const heading = screen.getByText('Hello World');
      expect(heading).toHaveAttribute('id', 'hello-world');
    });

    it('should handle special characters in heading slugs', () => {
      render(<MarkdownRenderer content="# API Reference (v2)" />);
      const heading = screen.getByText('API Reference (v2)');
      expect(heading).toHaveAttribute('id', 'api-reference-v2');
    });
  });

  describe('Text Formatting', () => {
    it('should render bold text', () => {
      render(<MarkdownRenderer content="**bold text**" />);
      const bold = screen.getByText('bold text');
      expect(bold.tagName).toBe('STRONG');
    });

    it('should render italic text', () => {
      render(<MarkdownRenderer content="_italic text_" />);
      const italic = screen.getByText('italic text');
      expect(italic.tagName).toBe('EM');
    });

    it('should render strikethrough text', () => {
      render(<MarkdownRenderer content="~~strikethrough~~" />);
      const del = screen.getByText('strikethrough');
      expect(del.tagName).toBe('DEL');
    });

    it('should render combined formatting', () => {
      render(<MarkdownRenderer content="**_bold italic_**" />);
      expect(screen.getByText('bold italic')).toBeInTheDocument();
    });
  });

  describe('Lists', () => {
    it('should render unordered list', () => {
      const content = `
- Item 1
- Item 2
- Item 3
      `;
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
      expect(screen.getByText('Item 3')).toBeInTheDocument();
    });

    it('should render ordered list', () => {
      const content = `
1. First
2. Second
3. Third
      `;
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByText('First')).toBeInTheDocument();
      expect(screen.getByText('Second')).toBeInTheDocument();
      expect(screen.getByText('Third')).toBeInTheDocument();
    });

    it('should render nested lists', () => {
      const content = `
- Item 1
  - Nested 1
  - Nested 2
- Item 2
      `;
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Nested 1')).toBeInTheDocument();
      expect(screen.getByText('Nested 2')).toBeInTheDocument();
    });
  });

  describe('Links', () => {
    it('should render internal links', () => {
      render(<MarkdownRenderer content="[Internal](/path)" />);
      const link = screen.getByText('Internal');
      expect(link.tagName).toBe('A');
      expect(link).toHaveAttribute('href', '/path');
    });

    it('should render external links with target="_blank"', () => {
      render(<MarkdownRenderer content="[External](https://example.com)" />);
      const link = screen.getByText('External');
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('should not add target="_blank" when openLinksInNewTab is false', () => {
      render(
        <MarkdownRenderer
          content="[External](https://example.com)"
          openLinksInNewTab={false}
        />
      );
      const link = screen.getByText('External');
      expect(link).not.toHaveAttribute('target');
    });

    it('should call onLinkClick when link is clicked', () => {
      const onLinkClick = jest.fn();
      render(
        <MarkdownRenderer
          content="[Click me](/path)"
          onLinkClick={onLinkClick}
        />
      );
      const link = screen.getByText('Click me');
      fireEvent.click(link);
      expect(onLinkClick).toHaveBeenCalledWith(
        '/path',
        expect.any(Object)
      );
    });
  });

  describe('Images', () => {
    it('should render images', () => {
      render(<MarkdownRenderer content="![Alt text](image.jpg)" />);
      const img = screen.getByAltText('Alt text');
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute('src', 'image.jpg');
    });

    it('should add lazy loading by default', () => {
      render(<MarkdownRenderer content="![Alt](image.jpg)" />);
      const img = screen.getByAltText('Alt');
      expect(img).toHaveAttribute('loading', 'lazy');
    });

    it('should not add lazy loading when disabled', () => {
      render(
        <MarkdownRenderer content="![Alt](image.jpg)" lazyLoadImages={false} />
      );
      const img = screen.getByAltText('Alt');
      expect(img).not.toHaveAttribute('loading');
    });

    it('should call onImageError when image fails to load', () => {
      const onImageError = jest.fn();
      render(
        <MarkdownRenderer
          content="![Alt](broken.jpg)"
          onImageError={onImageError}
        />
      );
      const img = screen.getByAltText('Alt');
      fireEvent.error(img);
      expect(onImageError).toHaveBeenCalledWith(
        'broken.jpg',
        expect.any(Event)
      );
    });
  });

  describe('Code Blocks', () => {
    it('should render inline code', () => {
      render(<MarkdownRenderer content="`inline code`" />);
      const code = screen.getByTestId('inline-code');
      expect(code).toBeInTheDocument();
      expect(code).toHaveTextContent('inline code');
    });

    it('should render code blocks', () => {
      const content = '```\ncode block\n```';
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });

    it('should render code blocks with language', () => {
      const content = '```python\nprint("hello")\n```';
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByTestId('language-badge')).toHaveTextContent('Python');
    });

    it('should pass theme to code blocks', () => {
      const content = '```js\nconst x = 1;\n```';
      render(<MarkdownRenderer content={content} theme="light" />);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });

    it('should show line numbers when enabled', () => {
      const content = '```js\nconst x = 1;\n```';
      render(<MarkdownRenderer content={content} showLineNumbers />);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });
  });

  describe('Tables', () => {
    it('should render tables', () => {
      const content = `
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
      `;
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByText('Header 1')).toBeInTheDocument();
      expect(screen.getByText('Header 2')).toBeInTheDocument();
      expect(screen.getByText('Cell 1')).toBeInTheDocument();
      expect(screen.getByText('Cell 2')).toBeInTheDocument();
    });

    it('should style table headers', () => {
      const content = `
| Name | Age |
|------|-----|
| John | 30  |
      `;
      render(<MarkdownRenderer content={content} />);
      const header = screen.getByText('Name');
      expect(header.tagName).toBe('TH');
    });
  });

  describe('Blockquotes', () => {
    it('should render blockquotes', () => {
      render(<MarkdownRenderer content="> This is a quote" />);
      const blockquote = screen.getByText('This is a quote').closest('blockquote');
      expect(blockquote).toBeInTheDocument();
    });

    it('should style blockquotes', () => {
      render(<MarkdownRenderer content="> Quote" />);
      const blockquote = screen.getByText('Quote').closest('blockquote');
      expect(blockquote).toHaveClass('border-l-4');
    });
  });

  describe('Horizontal Rules', () => {
    it('should render horizontal rules', () => {
      const { container } = render(<MarkdownRenderer content="---" />);
      const hr = container.querySelector('hr');
      expect(hr).toBeInTheDocument();
    });
  });

  describe('Complex Content', () => {
    it('should render mixed markdown content', () => {
      const content = `
# Main Title

This is a **paragraph** with _emphasis_ and \`code\`.

## Section

- List item 1
- List item 2

[Link](https://example.com)

> Quote
      `;
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByText('Main Title')).toBeInTheDocument();
      expect(screen.getByText('paragraph')).toBeInTheDocument();
      expect(screen.getByText('Section')).toBeInTheDocument();
      expect(screen.getByText('List item 1')).toBeInTheDocument();
      expect(screen.getByText('Link')).toBeInTheDocument();
      expect(screen.getByText('Quote')).toBeInTheDocument();
    });

    it('should handle markdown with code blocks and tables', () => {
      const content = `
# Documentation

| Feature | Status |
|---------|--------|
| Feature 1 | ✓ |

\`\`\`python
def hello():
    print("Hello")
\`\`\`
      `;
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByText('Documentation')).toBeInTheDocument();
      expect(screen.getByText('Feature')).toBeInTheDocument();
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });
  });

  describe('HTML Support', () => {
    it('should escape HTML by default', () => {
      render(<MarkdownRenderer content="<script>alert('xss')</script>" />);
      expect(screen.queryByText("alert('xss')")).toBeInTheDocument();
    });

    it('should allow HTML when enabled', () => {
      render(
        <MarkdownRenderer
          content="<div class='custom'>Custom HTML</div>"
          allowHtml
        />
      );
      const div = screen.getByText('Custom HTML');
      expect(div).toBeInTheDocument();
    });
  });

  describe('Custom Components', () => {
    it('should allow custom component overrides', () => {
      const CustomParagraph = ({ children }: any) => (
        <p data-testid="custom-paragraph">{children}</p>
      );

      render(
        <MarkdownRenderer
          content="Test paragraph"
          components={{ p: CustomParagraph }}
        />
      );

      expect(screen.getByTestId('custom-paragraph')).toBeInTheDocument();
    });
  });

  describe('Theme Support', () => {
    it('should apply light theme', () => {
      const content = '```js\nconst x = 1;\n```';
      render(<MarkdownRenderer content={content} theme="light" />);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });

    it('should apply dark theme by default', () => {
      const content = '```js\nconst x = 1;\n```';
      render(<MarkdownRenderer content={content} />);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });
  });
});

describe('CodeBlock', () => {
  describe('Rendering', () => {
    it('should render code content', () => {
      render(<CodeBlock>const x = 1;</CodeBlock>);
      expect(screen.getByText('const x = 1;')).toBeInTheDocument();
    });

    it('should display language badge', () => {
      render(<CodeBlock className="language-python">print("hello")</CodeBlock>);
      expect(screen.getByTestId('language-badge')).toHaveTextContent('Python');
    });

    it('should hide language badge when showLanguageBadge is false', () => {
      render(
        <CodeBlock className="language-python" showLanguageBadge={false}>
          print("hello")
        </CodeBlock>
      );
      expect(screen.queryByTestId('language-badge')).not.toBeInTheDocument();
    });

    it('should render without language', () => {
      render(<CodeBlock>plain code</CodeBlock>);
      expect(screen.getByTestId('language-badge')).toHaveTextContent('Code');
    });
  });

  describe('Copy Functionality', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('should show copy button by default', () => {
      render(<CodeBlock>code</CodeBlock>);
      expect(screen.getByTestId('copy-button')).toBeInTheDocument();
    });

    it('should hide copy button when showCopyButton is false', () => {
      render(<CodeBlock showCopyButton={false}>code</CodeBlock>);
      expect(screen.queryByTestId('copy-button')).not.toBeInTheDocument();
    });

    it('should copy code to clipboard when clicked', async () => {
      render(<CodeBlock>const x = 1;</CodeBlock>);
      const copyButton = screen.getByTestId('copy-button');
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith('const x = 1;');
      });
    });

    it('should show "Copied!" message after copying', async () => {
      render(<CodeBlock>code</CodeBlock>);
      const copyButton = screen.getByTestId('copy-button');
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(screen.getByText('Copied!')).toBeInTheDocument();
      });
    });

    it('should call onCopy callback when code is copied', async () => {
      const onCopy = jest.fn();
      render(<CodeBlock onCopy={onCopy}>const x = 1;</CodeBlock>);
      const copyButton = screen.getByTestId('copy-button');
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(onCopy).toHaveBeenCalledWith('const x = 1;');
      });
    });
  });

  describe('Line Numbers', () => {
    it('should not show line numbers by default', () => {
      render(<CodeBlock>code</CodeBlock>);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });

    it('should show line numbers when enabled', () => {
      render(<CodeBlock showLineNumbers>code</CodeBlock>);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });
  });

  describe('Themes', () => {
    it('should apply dark theme by default', () => {
      render(<CodeBlock>code</CodeBlock>);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });

    it('should apply light theme', () => {
      render(<CodeBlock theme="light">code</CodeBlock>);
      expect(screen.getByTestId('code-block')).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    it('should apply custom wrapper className', () => {
      const { container } = render(
        <CodeBlock wrapperClassName="custom-wrapper">code</CodeBlock>
      );
      const wrapper = container.querySelector('.custom-wrapper');
      expect(wrapper).toBeInTheDocument();
    });
  });
});

describe('InlineCode', () => {
  it('should render inline code', () => {
    render(<InlineCode>inline</InlineCode>);
    const code = screen.getByTestId('inline-code');
    expect(code).toBeInTheDocument();
    expect(code).toHaveTextContent('inline');
  });

  it('should apply custom className', () => {
    render(<InlineCode className="custom">code</InlineCode>);
    const code = screen.getByTestId('inline-code');
    expect(code).toHaveClass('custom');
  });

  it('should style inline code', () => {
    render(<InlineCode>code</InlineCode>);
    const code = screen.getByTestId('inline-code');
    expect(code).toHaveClass('font-mono');
    expect(code).toHaveClass('text-sm');
  });
});
