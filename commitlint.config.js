module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "Feat",
        "Fix",
        "Docs",
        "Style",
        "Refactor",
        "Test",
        "Chore",
        "Setup",
        "CI",
        "Mock",
      ],
    ],
    "subject-case": [2, "always", "sentence-case"],
    "type-case": [2, "always", "sentence-case"],
    'header-max-length': [2, 'always', 135],
  },
  parserPreset: {
    parserOpts: {
      headerPattern: /^\((?<type>[^)]+)\):\s(?<subject>.+)$/,
      headerCorrespondence: ["type", "subject"],
    },
  },
};
