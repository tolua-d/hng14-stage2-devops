module.exports = {
  env: {
    node: true,
    es2021: true,
  },
  extends: "eslint:recommended",
  parserOptions: {
    ecmaVersion: 2021,
  },
  rules: {
    "no-console": "off",
    "no-unused-vars": "error",
    "no-undef": "error",
  },
};