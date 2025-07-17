import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="utf-8" />
        <meta name="description" content="Multi-Agent Portfolio Analysis System - Real-time market analysis with AI-powered insights" />
        <meta name="keywords" content="portfolio, analysis, AI, stocks, trading, investment, market, insights" />
        <meta name="author" content="Multi-Agent Portfolio Analysis System" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0ea5e9" />
        <meta name="msapplication-TileColor" content="#0ea5e9" />
        <meta name="msapplication-config" content="/browserconfig.xml" />
        
        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="Multi-Agent Portfolio Analysis System" />
        <meta property="og:description" content="Real-time market analysis with AI-powered insights" />
        <meta property="og:url" content="https://your-domain.vercel.app" />
        <meta property="og:image" content="/og-image.png" />
        
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Multi-Agent Portfolio Analysis System" />
        <meta name="twitter:description" content="Real-time market analysis with AI-powered insights" />
        <meta name="twitter:image" content="/twitter-image.png" />
        
        {/* Preconnect to external domains */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
} 