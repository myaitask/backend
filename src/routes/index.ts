import { Router, Request, Response } from 'express';
import authRouter from './auth.js';

const router = Router();

// Mount authentication API routes
router.use('/auth', authRouter);

// Health Check
router.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

export default router;
