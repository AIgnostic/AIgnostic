import type { Config } from 'jest';

const config = {
  displayName: 'aignostic-frontend',
  preset: '../../jest.preset.js',
  transform: {
    '^(?!.*\\.(js|jsx|ts|tsx|css|json)$)': '@nx/react/plugins/jest',
    '^.+\\.[tj]sx?$': ['babel-jest', { configFile: './babel.config.jest.js' }],
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx'],
  moduleNameMapper: {
    // WARNING: If you have another file called env, it will also mock to the same place!
    './env': '<rootDir>/tests/__mocks__/env.ts',
  },
  collectCoverage: true,
  coverageDirectory: '../../coverage/frontend',
  coverageReporters: ['clover', 'json', 'lcov', 'text', 'json-summary', 'html'],
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: '../../reports/frontend',
        outputName: './jest-results.xml',
        ancestorSeparator: ' › ',
        uniqueOutputName: 'false',
        suiteNameTemplate: '{filepath}',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
      },
    ],
  ],
} satisfies Config;

export default config;
