# Multi-Agent Portfolio Analysis - Next.js Frontend

A modern, responsive web application for portfolio analysis built with Next.js, TypeScript, and Tailwind CSS.

## 🚀 Features

- **📊 Portfolio Dashboard**: Real-time portfolio metrics and volatility tracking
- **🔍 Ad-hoc Analysis**: Individual stock analysis with AI-powered insights
- **🧠 Knowledge Evolution**: Historical insights timeline and learning visualization
- **⚡ Event Monitoring**: Real-time alerts and notifications with auto-refresh
- **🕐 Background Scheduling**: Configurable automated analysis intervals
- **⚙️ Settings Management**: System configuration and preferences

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React Query for server state
- **Icons**: Lucide React
- **Charts**: Recharts for data visualization
- **Notifications**: React Hot Toast
- **HTTP Client**: Axios

## 🏗️ Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable components
│   │   ├── layout/        # Layout components (Header, Sidebar, Layout)
│   │   └── common/        # Common UI components
│   ├── hooks/             # Custom React hooks
│   ├── pages/             # Next.js pages
│   │   ├── index.tsx      # Portfolio Dashboard
│   │   ├── analysis.tsx   # Ad-hoc Analysis
│   │   ├── knowledge.tsx  # Knowledge Evolution
│   │   ├── events.tsx     # Event Monitoring
│   │   ├── scheduler.tsx  # Background Scheduling
│   │   └── settings.tsx   # Settings
│   ├── styles/            # Global styles
│   ├── types/             # TypeScript type definitions
│   └── utils/             # Utility functions and API client
├── next.config.js         # Next.js configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Python backend API running (see main README)

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## 🔧 Configuration

### Environment Variables

The frontend automatically detects the environment and configures API endpoints:

- **Development**: `http://localhost:3000/api`
- **Production**: Uses relative URLs for Vercel deployment

### API Integration

The application integrates with the existing Python API endpoints:

- `POST /api/app` - Portfolio analysis and insights
- `GET /api/app` - System status
- All requests are proxied through Next.js API routes

## 🎨 Design System

### Color Palette

- **Primary**: Blue (`#0ea5e9`)
- **Success**: Green (`#22c55e`)
- **Warning**: Yellow (`#f59e0b`)
- **Error**: Red (`#ef4444`)

### Typography

- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

### Components

- **MetricCard**: Displays key metrics with icons and change indicators
- **LoadingSpinner**: Consistent loading states
- **ErrorMessage**: Error handling with retry functionality
- **Layout**: Responsive layout with sidebar navigation

## 📱 Responsive Design

The application is fully responsive and optimized for:

- **Desktop**: Full feature set with sidebar navigation
- **Tablet**: Responsive grid layouts and touch-friendly interactions
- **Mobile**: Optimized mobile experience with collapsible navigation

## 🔄 Data Management

### React Query

- **Caching**: Intelligent caching with stale-while-revalidate
- **Auto-refetch**: Automatic data refetching on intervals
- **Error Handling**: Robust error handling with retry logic
- **Optimistic Updates**: Instant UI updates with background sync

### State Management

- **Server State**: React Query for API data
- **Local State**: React hooks for component state
- **Global State**: Context for shared application state

## 🚀 Deployment

### Vercel (Recommended)

The application is optimized for Vercel deployment:

1. Push to GitHub repository
2. Connect to Vercel
3. Deploy automatically on every push
4. Environment variables configured in Vercel dashboard

### Build Configuration

```json
{
  "scripts": {
    "build": "next build",
    "start": "next start"
  }
}
```

### Performance Optimization

- **Code Splitting**: Automatic code splitting by Next.js
- **Image Optimization**: Next.js Image component
- **Static Generation**: Static generation for better performance
- **Bundle Analysis**: Bundle analyzer for optimization insights

## 🔐 Security

- **Environment Variables**: Secure handling of sensitive data
- **HTTPS**: Enforced HTTPS in production
- **CORS**: Configured for secure cross-origin requests
- **Content Security Policy**: CSP headers for XSS protection

## 🧪 Testing

Testing setup includes:

- **Unit Tests**: Jest and React Testing Library
- **Integration Tests**: API integration testing
- **E2E Tests**: Cypress for end-to-end testing
- **Type Safety**: Full TypeScript coverage

## 📊 Features Overview

### Portfolio Dashboard
- Real-time portfolio metrics
- Volatility tracking
- Risk assessment
- Recent insights display

### Ad-hoc Analysis
- Individual stock analysis
- Popular stock quick buttons
- Analysis history
- Email notifications

### Knowledge Evolution
- Historical insights timeline
- Learning visualization
- Evolution patterns
- Ticker-specific analysis

### Event Monitoring
- Real-time event tracking
- Auto-refresh functionality
- Event filtering and search
- Color-coded event types

### Background Scheduling
- Configurable analysis intervals
- Scheduler status monitoring
- Preset interval options
- Performance tracking

### Settings
- System configuration
- Portfolio management
- Notification settings
- Security information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the main project README
- Review the API documentation
- Open an issue on GitHub 