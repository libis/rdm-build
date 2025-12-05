/**
 * Vite Configuration for Standalone DVWebloader V2 Bundle
 *
 * This builds the file uploader as a standalone bundle that can be used
 * independently from the main Dataverse SPA. It uses local copies of:
 * - dataverse-frontend (source files)
 * - dataverse-client-javascript (built dist)
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js'
import commonjs from '@rollup/plugin-commonjs'
import * as path from 'path'

const frontendPath = path.resolve(__dirname, '../../../../dataverse-frontend')
const clientJsPath = path.resolve(__dirname, '../../../../dataverse-client-javascript')
const clientJsDistPath = path.resolve(clientJsPath, 'dist')

export default defineConfig({
  plugins: [
    react(),
    // Inject CSS into the JS bundle so we only have a single file to load
    cssInjectedByJsPlugin()
  ],
  // Don't copy public folder contents
  publicDir: false,
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // Target modern browsers for smaller bundle size
    target: 'es2020',
    rollupOptions: {
      input: path.resolve(frontendPath, 'src/standalone-uploader/index.tsx'),
      output: {
        // Single entry file
        entryFileNames: 'dvwebloader-v2.js',
        // Inline all chunks into the main bundle
        inlineDynamicImports: true,
        // Asset file naming
        assetFileNames: 'assets/[name].[ext]'
      },
      plugins: [
        // Better CommonJS handling for nested re-exports
        commonjs({
          include: [/dataverse-client-javascript/],
          // Force named exports detection
          requireReturnsDefault: 'namespace',
          // Be more aggressive about detecting exports
          dynamicRequireTargets: [
            path.resolve(clientJsDistPath, '**/*.js')
          ]
        })
      ]
    },
    // Increase chunk size warning limit since we're bundling everything
    chunkSizeWarningLimit: 2000,
    // Enable minification
    minify: 'esbuild',
    // Generate sourcemaps for debugging
    sourcemap: true
  },
  resolve: {
    alias: {
      // Map @ to dataverse-frontend/src
      '@': path.resolve(frontendPath, 'src'),
      '@tests': path.resolve(frontendPath, 'tests'),
      // Use the local built dataverse-client-javascript
      // The main package points to dist/, subpath imports like /dist/core/... should resolve to dist/core/...
      '@iqss/dataverse-client-javascript/dist': clientJsDistPath,
      '@iqss/dataverse-client-javascript': clientJsDistPath
    }
  },
  // Force Vite to pre-bundle the CommonJS package
  optimizeDeps: {
    include: [],
    esbuildOptions: {
      // Force esbuild to handle CJS
      format: 'esm'
    }
  },
  define: {
    // Define production mode
    'process.env.NODE_ENV': '"production"'
  }
})
