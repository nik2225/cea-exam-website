import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import express from 'express'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
    {
      name: 'local-api',
      configureServer(server) {
        server.middlewares.use(express.json({ limit: '50mb' }));
        
        server.middlewares.use('/api/save-questions', (req: any, res) => {
          if (req.method === 'POST') {
            const { subject, questions } = req.body;
            const safeName = subject.replace(/ /g, '_').replace(/&/g, 'and').replace(/,/g, '');
            const filepath = path.resolve(__dirname, `src/data/${safeName}.json`);
            
            fs.writeFileSync(filepath, JSON.stringify(questions, null, 2));
            
            res.statusCode = 200;
            res.end(JSON.stringify({ success: true }));
          } else {
            res.statusCode = 405;
            res.end();
          }
        });
      }
    }
  ],
})
