import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import morgan from 'morgan';
import router from './routes/index.js'; // Use .js extension since we use NodeNext module resolution
import { hostValidation } from './proxy.js';

const app: Application = express();

// Trust proxy to support hosting behind reverse proxies (Render, AWS, GCP, Cloudflare, etc.)
app.set('trust proxy', true);

// Host validation middleware
app.use(hostValidation);


// Configure CORS
const allowedOrigins = ['https://www.myaitask.io', 'http://www.myaitask.io'];
if (process.env.NODE_ENV === 'development') {
  allowedOrigins.push(
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5001',
    'http://127.0.0.1:5001'
  );
}

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (like server-to-server or mobile apps)
    if (!origin) return callback(null, true);
    if (allowedOrigins.includes(origin)) {
      return callback(null, true);
    } else {
      return callback(new Error('Not allowed by CORS'), false);
    }
  },
  credentials: true,
}));
app.use(express.json());
app.use(morgan('dev'));


// Routes
app.use('/api', router);

// Default Route
app.get('/', (req: Request, res: Response) => {
  res.json({
    message: 'Welcome to the WhatsApp Clone API Backend',
    docs: '/api/health or /api/messages',
  });
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined,
  });
});

export default app;
