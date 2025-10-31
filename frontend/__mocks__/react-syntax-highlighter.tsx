/**
 * Mock for react-syntax-highlighter
 * Used in Jest tests to avoid ESM issues
 */

import React from 'react';

export const Prism = ({ children, ...props }: any) => {
  return <pre data-testid="syntax-highlighter" {...props}>{children}</pre>;
};

export default Prism;
