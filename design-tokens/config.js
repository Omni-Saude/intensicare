/**
 * Style Dictionary build configuration for IntensiCare design tokens.
 *
 * Generates CSS custom properties with dark-first theme resolution,
 * plus TypeScript type definitions for token consumers.
 *
 * Source: docs/plan/design/design-tokens.md §1
 *
 * Usage: npx style-dictionary build --config design-tokens/config.js
 */

const path = require('path');

const TOKENS_DIR = path.resolve(__dirname);

module.exports = {
  source: [
    `${TOKENS_DIR}/primitives/*.json`,
    `${TOKENS_DIR}/clinical/*.json`,
    `${TOKENS_DIR}/semantic/*.json`,
  ],

  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: `${TOKENS_DIR}/build/`,
      files: [
        {
          destination: 'tokens.css',
          format: 'css/variables',
          options: {
            outputReferences: true,
            selector: ':root, [data-theme="dark"]',
          },
        },
        {
          destination: 'tokens-dark.css',
          format: 'css/variables',
          options: {
            outputReferences: true,
            selector: ':root, [data-theme="dark"]',
          },
          filter: (token) => {
            return token.attributes?.theme === 'dark' || !token.attributes?.theme;
          },
        },
        {
          destination: 'tokens-light.css',
          format: 'css/variables',
          options: {
            outputReferences: true,
            selector: '[data-theme="light"]',
          },
          filter: (token) => {
            return token.attributes?.theme === 'light' || !token.attributes?.theme;
          },
        },
      ],
    },

    ts: {
      transformGroup: 'js',
      buildPath: `${TOKENS_DIR}/build/`,
      files: [
        {
          destination: 'tokens.ts',
          format: 'typescript/es6-declarations',
          options: {
            outputStringLiterals: true,
          },
        },
      ],
    },

    json: {
      transformGroup: 'web',
      buildPath: `${TOKENS_DIR}/build/`,
      files: [
        {
          destination: 'tokens.json',
          format: 'json/flat',
        },
      ],
    },
  },
};
