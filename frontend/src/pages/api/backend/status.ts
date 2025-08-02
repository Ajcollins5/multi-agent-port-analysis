import { NextApiRequest, NextApiResponse } from 'next';

interface BackendStatus {
  backend_available: boolean;
  api_key_configured: boolean;
  database_connected: boolean;
  optimizations_active: boolean;
  response_time: number;
  version: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<BackendStatus | { error: string }>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const startTime = Date.now();

  try {
    // Try to call the Python backend
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(`${backendUrl}/api/v1/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Add timeout to prevent hanging
        signal: AbortSignal.timeout(5000)
      });

      const responseTime = Date.now() - startTime;

      if (response.ok) {
        const data = await response.json();
        return res.status(200).json({
          ...data,
          response_time: responseTime
        });
      } else {
        // Backend is running but returned an error
        return res.status(200).json({
          backend_available: false,
          api_key_configured: false,
          database_connected: false,
          optimizations_active: false,
          response_time: responseTime,
          version: 'unknown'
        });
      }
    } catch (backendError) {
      console.log('Backend status check failed:', backendError);
      
      // Backend is not available, return mock status
      const responseTime = Date.now() - startTime;
      return res.status(200).json({
        backend_available: false,
        api_key_configured: false,
        database_connected: false,
        optimizations_active: true, // Frontend optimizations are still active
        response_time: responseTime,
        version: 'frontend-only'
      });
    }

  } catch (error) {
    console.error('Status check error:', error);
    
    const responseTime = Date.now() - startTime;
    res.status(200).json({
      backend_available: false,
      api_key_configured: false,
      database_connected: false,
      optimizations_active: false,
      response_time: responseTime,
      version: 'error'
    });
  }
}
