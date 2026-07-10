declare module 'react-syntax-highlighter/dist/esm/prism-light' {
  import { ComponentType, CSSProperties } from 'react';

  export interface SyntaxHighlighterProps {
    language?: string;
    style?: Record<string, CSSProperties>;
    children?: string;
    customStyle?: CSSProperties;
    codeTagProps?: Record<string, unknown>;
    showLineNumbers?: boolean;
    showInlineLineNumbers?: boolean;
    startingLineNumber?: number;
    lineNumberStyle?: CSSProperties;
    lineNumberContainerStyle?: CSSProperties;
    wrapLines?: boolean;
    wrapLongLines?: boolean;
    lineProps?: Record<string, unknown> | ((lineNumber: number) => Record<string, unknown>);
    PreTag?: ComponentType<Record<string, unknown>>;
    CodeTag?: ComponentType<Record<string, unknown>>;
    [key: string]: unknown;
  }

  const SyntaxHighlighter: ComponentType<SyntaxHighlighterProps> & {
    registerLanguage: (name: string, language: unknown) => void;
  };

  export default SyntaxHighlighter;
}

declare module 'react-syntax-highlighter/dist/esm/languages/prism/yaml' {
  const yaml: unknown;
  export default yaml;
}

declare module 'react-syntax-highlighter/dist/esm/styles/prism/one-dark' {
  import { CSSProperties } from 'react';
  const oneDark: Record<string, CSSProperties>;
  export default oneDark;
}
