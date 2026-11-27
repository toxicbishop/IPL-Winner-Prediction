import fs from 'node:fs'
import path from 'node:path'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { PAGE_META, renderMetaTags, resolvePageMeta } from './seo.config.ts'

const SEO_BLOCK_REGEX = /<!-- SEO_META_START -->[\s\S]*?<!-- SEO_META_END -->/

function replaceSeoBlock(html: string, routePath: string): string {
  const tags = renderMetaTags(resolvePageMeta(routePath))
  const block = `<!-- SEO_META_START -->\n${tags}\n    <!-- SEO_META_END -->`
  return html.replace(SEO_BLOCK_REGEX, block)
}

function buildTimeSeoPlugin(): Plugin {
  let outDir = 'dist'

  return {
    name: 'build-time-seo-meta',
    configResolved(config) {
      outDir = path.resolve(config.root, config.build.outDir)
    },
    transformIndexHtml(html) {
      return replaceSeoBlock(html, '/')
    },
    closeBundle() {
      const indexPath = path.join(outDir, 'index.html')
      if (!fs.existsSync(indexPath)) {
        return
      }
      const baseHtml = fs.readFileSync(indexPath, 'utf-8')
      for (const routePath of Object.keys(PAGE_META)) {
        if (routePath === '/') {
          continue
        }
        const slug = routePath.replace(/^\/+|\/+$/g, '')
        const routeHtml = replaceSeoBlock(baseHtml, routePath)
        const targetFile = path.join(outDir, `${slug}.html`)
        fs.mkdirSync(path.dirname(targetFile), { recursive: true })
        fs.writeFileSync(targetFile, routeHtml, 'utf-8')
      }
    },
  }
}

export default defineConfig({
  plugins: [react(), buildTimeSeoPlugin()],
  build: {
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000',
      '/assets': 'http://localhost:8000'
    }
  }
})
