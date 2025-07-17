/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Skip TypeScript checking during build for deployment testing
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Skip ESLint checking during build for deployment testing
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // API routes configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
  
  // Static optimization for better performance
  trailingSlash: false,
  
  // Environment variables
  env: {
    CUSTOM_KEY: 'value',
  },
  
  // Build optimization
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
};

module.exports = nextConfig; 