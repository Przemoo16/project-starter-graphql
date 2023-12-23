/** @type {import("prettier").Config} */
module.exports = {
  singleQuote: true,
  arrowParens: 'avoid',
  trailingComma: 'all',
  // Dynamically resolve plugin path so it can be used together with the pre-commit
  plugins: [require.resolve('prettier-plugin-tailwindcss')],
};
