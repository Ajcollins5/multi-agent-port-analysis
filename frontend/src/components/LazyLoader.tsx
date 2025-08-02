import React, { Suspense, lazy, ComponentType, ReactNode } from 'react';
import { Loader2 } from 'lucide-react';

interface LazyLoaderProps {
  children: ReactNode;
  fallback?: ReactNode;
  error?: ReactNode;
}

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

// Default loading spinner component
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  text = 'Loading...', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <div className={`flex items-center justify-center p-4 ${className}`}>
      <div className="flex flex-col items-center space-y-2">
        <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-600`} />
        {text && (
          <p className="text-sm text-gray-600 animate-pulse">{text}</p>
        )}
      </div>
    </div>
  );
};

// Skeleton loader for different content types
export const SkeletonLoader: React.FC<{ type?: 'card' | 'list' | 'chart' | 'table' }> = ({ 
  type = 'card' 
}) => {
  const skeletons = {
    card: (
      <div className="animate-pulse">
        <div className="bg-gray-200 rounded-lg p-4 space-y-3">
          <div className="h-4 bg-gray-300 rounded w-3/4"></div>
          <div className="h-3 bg-gray-300 rounded w-1/2"></div>
          <div className="h-3 bg-gray-300 rounded w-5/6"></div>
        </div>
      </div>
    ),
    list: (
      <div className="animate-pulse space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-gray-300 rounded-full"></div>
            <div className="flex-1 space-y-1">
              <div className="h-3 bg-gray-300 rounded w-3/4"></div>
              <div className="h-2 bg-gray-300 rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    ),
    chart: (
      <div className="animate-pulse">
        <div className="bg-gray-200 rounded-lg p-4">
          <div className="h-4 bg-gray-300 rounded w-1/3 mb-4"></div>
          <div className="h-48 bg-gray-300 rounded"></div>
        </div>
      </div>
    ),
    table: (
      <div className="animate-pulse">
        <div className="bg-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-300 h-10"></div>
          {[...Array(4)].map((_, i) => (
            <div key={i} className="border-t border-gray-300 h-8 bg-gray-200"></div>
          ))}
        </div>
      </div>
    )
  };

  return skeletons[type];
};

// Main lazy loader component
export const LazyLoader: React.FC<LazyLoaderProps> = ({ 
  children, 
  fallback,
  error 
}) => {
  const defaultFallback = <LoadingSpinner />;
  
  return (
    <Suspense fallback={fallback || defaultFallback}>
      {children}
    </Suspense>
  );
};

// Higher-order component for lazy loading
export function withLazyLoading<P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>,
  fallback?: ReactNode,
  displayName?: string
) {
  const LazyComponent = lazy(importFunc);
  
  const WrappedComponent: React.FC<P> = (props) => (
    <LazyLoader fallback={fallback}>
      <LazyComponent {...props} />
    </LazyLoader>
  );
  
  WrappedComponent.displayName = displayName || 'LazyLoadedComponent';
  
  return WrappedComponent;
}

// Intersection Observer based lazy loading for images and components
interface IntersectionLazyLoaderProps {
  children: ReactNode;
  fallback?: ReactNode;
  rootMargin?: string;
  threshold?: number;
  className?: string;
}

export const IntersectionLazyLoader: React.FC<IntersectionLazyLoaderProps> = ({
  children,
  fallback = <SkeletonLoader />,
  rootMargin = '50px',
  threshold = 0.1,
  className = ''
}) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [hasLoaded, setHasLoaded] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasLoaded) {
          setIsVisible(true);
          setHasLoaded(true);
          observer.disconnect();
        }
      },
      {
        rootMargin,
        threshold
      }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [rootMargin, threshold, hasLoaded]);

  return (
    <div ref={ref} className={className}>
      {isVisible ? children : fallback}
    </div>
  );
};

// Preload utilities for better performance
export const preloadComponent = (importFunc: () => Promise<any>) => {
  // Preload the component
  importFunc();
};

export const preloadRoute = (href: string) => {
  // Preload Next.js route
  if (typeof window !== 'undefined') {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = href;
    document.head.appendChild(link);
  }
};

// Performance monitoring for lazy loaded components
interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  componentName: string;
}

export const withPerformanceMonitoring = <P extends object>(
  Component: ComponentType<P>,
  componentName: string
) => {
  const MonitoredComponent: React.FC<P> = (props) => {
    const startTime = React.useRef(performance.now());
    const [metrics, setMetrics] = React.useState<PerformanceMetrics | null>(null);

    React.useEffect(() => {
      const loadTime = performance.now() - startTime.current;
      
      // Measure render time
      const renderStartTime = performance.now();
      
      requestAnimationFrame(() => {
        const renderTime = performance.now() - renderStartTime;
        
        const newMetrics: PerformanceMetrics = {
          loadTime,
          renderTime,
          componentName
        };
        
        setMetrics(newMetrics);
        
        // Log performance metrics in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`Performance metrics for ${componentName}:`, newMetrics);
        }
        
        // Send to analytics in production (if available)
        if (process.env.NODE_ENV === 'production' && window.gtag) {
          window.gtag('event', 'component_performance', {
            component_name: componentName,
            load_time: loadTime,
            render_time: renderTime
          });
        }
      });
    }, []);

    return <Component {...props} />;
  };

  MonitoredComponent.displayName = `withPerformanceMonitoring(${componentName})`;
  
  return MonitoredComponent;
};

// Utility for creating optimized lazy components
export const createLazyComponent = <P extends object>(
  importFunc: () => Promise<{ default: ComponentType<P> }>,
  options: {
    fallback?: ReactNode;
    displayName?: string;
    preload?: boolean;
    monitor?: boolean;
  } = {}
) => {
  const {
    fallback = <LoadingSpinner />,
    displayName = 'LazyComponent',
    preload = false,
    monitor = false
  } = options;

  // Preload if requested
  if (preload && typeof window !== 'undefined') {
    // Preload after a short delay to not block initial render
    setTimeout(() => preloadComponent(importFunc), 100);
  }

  let LazyComponent = lazy(importFunc);

  // Add performance monitoring if requested
  if (monitor) {
    const OriginalLazyComponent = LazyComponent;
    LazyComponent = lazy(async () => {
      const module = await importFunc();
      const MonitoredComponent = withPerformanceMonitoring(module.default, displayName);
      return { default: MonitoredComponent };
    });
  }

  const WrappedComponent: React.FC<P> = (props) => (
    <LazyLoader fallback={fallback}>
      <LazyComponent {...props} />
    </LazyLoader>
  );

  WrappedComponent.displayName = displayName;

  return WrappedComponent;
};
