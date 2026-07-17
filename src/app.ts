import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import morgan from 'morgan';
import router from './routes/index.js'; // Use .js extension since we use NodeNext module resolution

const app: Application = express();

// Host validation middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  const host = req.headers.host;
  const hostname = host ? host.split(':')[0] : '';
  const allowedHosts = ['backend.mysitask.com'];
  if (process.env.NODE_ENV === 'development') {
    allowedHosts.push('localhost', '127.0.0.1');
  }

  if (!allowedHosts.includes(hostname)) {
    return res.status(403).json({
      success: false,
      error: 'Forbidden',
      message: 'Access Denied: Invalid Host',
    });
  }
  next();
});

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
