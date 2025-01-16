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
      ],
    ],
    "subject-case": [2, "always", "sentence-case"],
    "type-case": [2, "always", "sentence-case",
    ],
  },
  parserPreset: {
    parserOpts: {
      headerPattern: /^\((?<type>[^)]+)\):\s(?<subject>.+)$/,
      headerCorrespondence: ["type", "subject"],
    },
  },
};
