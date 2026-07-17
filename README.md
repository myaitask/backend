# WhatsApp Clone API Backend

This is the Express + TypeScript backend for the WhatsApp Clone application.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or higher recommended)
- npm, yarn, pnpm, or bun

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment variables**:
   Copy `.env.example` to `.env` (already done by setup):
   ```bash
   cp .env.example .env
   ```
   You can adjust the `PORT` variable (default is `5000`) if needed.

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   The server will start at `http://localhost:5000` (or whatever `PORT` you configured). It will automatically restart when you make changes to files in the `src/` directory.

## Build and Production

To build the TypeScript files to JavaScript:
```bash
npm run build
```

To run the built production server:
```bash
npm run start
```

## API Endpoints

- `GET /` - Base greeting endpoint
- `GET /api/health` - Check health, uptime, and server timestamp
- `GET /api/messages` - Retrieve all messages
- `POST /api/messages` - Send a new message
  - Body: `{ "sender": "Name", "text": "Message content" }`
