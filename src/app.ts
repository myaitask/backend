import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import morgan from 'morgan';
import router from './routes/index.js'; // Use .js extension since we use NodeNext module resolution

const app: Application = express();

// Middlewares
app.use(cors());
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
