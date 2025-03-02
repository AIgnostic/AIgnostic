/// <reference types='vitest' />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// import { nxViteTsPaths } from '@nx/vite/plugins/nx-tsconfig-paths.plugin';
// import { nxCopyAssetsPlugin } from '@nx/vite/plugins/nx-copy-assets.plugin';

export default defineConfig({
  root: __dirname,
  base: '/',
  cacheDir: '../node_modules/.vite/frontend',
  server: {
    port: 4200,
    host: 'localhost',
    fs: {
      strict: false, // Disable strict file watching
      allow: ['../'], // Limit the directories being watched
    },
  },
  preview: {
    port: 4300,
    host: 'localhost',
  },
  plugins: [react() /* nxViteTsPaths(), nxCopyAssetsPlugin(['*.md']) */], // Disabled due to "Watcher not constructor" error (bug in Nx)
  // Uncomment this if you are using workers.
  // worker: {
  //  plugins: [ nxViteTsPaths() ],
  // },
  assetsInclude: ['**/*.md'],
  build: {
    outDir: '../../dist/frontend',
    emptyOutDir: true,
    reportCompressedSize: true,
    commonjsOptions: {
      transformMixedEsModules: true,
    },
  },
});
