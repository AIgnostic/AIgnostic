module.exports = {
    extends: ['@commitlint/config-conventional'],
    rules: {
      'type-enum': [
        2,
        'always',
        ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'setup'],
      ],
      'subject-case': [2, 'always', 'sentence-case'],
    },
    parserPreset: {
      parserOpts: {
        headerPattern: /^\((?<type>[^)]+)\):\s(?<subject>.+)$/,
        headerCorrespondence: ['type', 'subject'],
      },
    },
  };
  