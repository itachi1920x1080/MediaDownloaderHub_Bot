# MediaDownloaderHub - Frontend

This is the Vue 3 + Vite frontend for the MediaDownloaderHub project.

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```
*Note: During local development, the Vite proxy will automatically forward `/api` requests to `http://127.0.0.1:5000`.*

### Compile and Minify for Production (Vercel)

```sh
npm run build
```
*Note: In production, the API URL is defined in the components to point directly to the remote backend (e.g. Render).*
