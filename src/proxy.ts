import { Request, Response, NextFunction } from 'express';

export function hostValidation(req: Request, res: Response, next: NextFunction) {
  let host = (req.headers['x-forwarded-host'] as string) || req.headers.host;
  if (host && typeof host === 'string') {
    host = host.split(',')[0].trim();
  }
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
}
