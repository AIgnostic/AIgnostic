import { getJestProjectsAsync } from '@nx/jest';

export default async () => ({
  projects: await getJestProjectsAsync(),
  transform: {
    '^.+\\.[tj]sx?$': ['babel-jest', { presets: ['@nx/react/babel'] }]
  },
  transformIgnorePatterns: ['node_modules/(?!.*\\.mjs$)'],
});
