module.exports = {
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  extends: [
    'standard-with-typescript',
    'plugin:qwik/recommended',
    'prettier', // Turn off all rules that are unnecessary or might conflict with Prettier
  ],
  plugins: ['simple-import-sort'],
  parserOptions: {
    tsconfigRootDir: __dirname,
    project: ['./tsconfig.json'],
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    'simple-import-sort/imports': 'error',
    'simple-import-sort/exports': 'error',
    '@typescript-eslint/consistent-type-definitions': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    // FIXME: Remove the rule below if narrowing element type in tests is possible
    '@typescript-eslint/non-nullable-type-assertion-style': 'off',
    '@typescript-eslint/strict-boolean-expressions': 'off',
  },
};
