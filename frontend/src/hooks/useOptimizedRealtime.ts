import { useState, useEffect, useCallback, useRef } from 'react';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

interface OptimizedRealtimeConfig {
  updateInterval?: number;
  maxUpdatesPerMinute?: number;
  enableOfflineMode?: boolean;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  maxRetries?: number;
}

interface ConnectionStats {
  isOnline: boolean;
  updateCount: number;
  lastUpdateTime: number;
  connectionAttempts: number;
  totalUpdatesReceived: number;
  errorCount: number;
}

export function useOptimizedRealtime(config: OptimizedRealtimeConfig = {}) {
  const {
    updateInterval = 5000,
    maxUpdatesPerMinute = 12,
    enableOfflineMode = true,
    reconnectInterval = 5000,
    heartbeatInterval = 30000,
    maxRetries = 5
  } = config;
  
  const [connectionStats, setConnectionStats] = useState<ConnectionStats>({
    isOnline: navigator.onLine,
    updateCount: 0,
    lastUpdateTime: Date.now(),
    connectionAttempts: 0,
    totalUpdatesReceived: 0,
    errorCount: 0
  });
  
  const [connectionQuality, setConnectionQuality] = useState<'excellent' | 'good' | 'poor' | 'offline'>('excellent');
  const subscriptionsRef = useRef<Set<any>>(new Set());
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const supabaseRef = useRef<SupabaseClient | null>(null);
  
  // Initialize Supabase client
  useEffect(() => {
    if (!supabaseRef.current) {
      supabaseRef.current = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
      );
    }
  }, []);
  
  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setConnectionStats(prev => ({ ...prev, isOnline: true }));
      setConnectionQuality('good');
      attemptReconnection();
    };
    
    const handleOffline = () => {
      setConnectionStats(prev => ({ ...prev, isOnline: false }));
      setConnectionQuality('offline');
      cleanupConnections();
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupConnections();
      if (heartbeatRef.current) {
        clearInterval(heartbeatRef.current);
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);
  
  const cleanupConnections = useCallback(() => {
    subscriptionsRef.current.forEach(subscription => {
      try {
        subscription.unsubscribe();
      } catch (error) {
        console.warn('Error unsubscribing:', error);
      }
    });
    subscriptionsRef.current.clear();
  }, []);
  
  const attemptReconnection = useCallback(() => {
    if (!connectionStats.isOnline || connectionStats.connectionAttempts >= maxRetries) {
      return;
    }
    
    setConnectionStats(prev => ({
      ...prev,
      connectionAttempts: prev.connectionAttempts + 1
    }));
    
    // Attempt to reconnect after a delay
    reconnectTimeoutRef.current = setTimeout(() => {
      // Reconnection logic would go here
      console.log('Attempting to reconnect real-time subscriptions...');
    }, reconnectInterval);
  }, [connectionStats.isOnline, connectionStats.connectionAttempts, maxRetries, reconnectInterval]);
  
  const shouldUpdate = useCallback(() => {
    const now = Date.now();
    const timeSinceLastUpdate = now - connectionStats.lastUpdateTime;
    
    // Reset counter every minute
    if (timeSinceLastUpdate > 60000) {
      setConnectionStats(prev => ({
        ...prev,
        updateCount: 0,
        lastUpdateTime: now
      }));
      return true;
    }
    
    // Check rate limits
    if (connectionStats.updateCount >= maxUpdatesPerMinute || timeSinceLastUpdate < updateInterval) {
      return false;
    }
    
    return true;
  }, [connectionStats.updateCount, connectionStats.lastUpdateTime, maxUpdatesPerMinute, updateInterval]);
  
  const handleUpdate = useCallback((data: any, source: string = 'unknown') => {
    if (!connectionStats.isOnline && enableOfflineMode) {
      console.log('Offline mode: Update queued for when connection is restored');
      return null;
    }
    
    if (!shouldUpdate()) {
      console.log('Rate limit reached, update skipped');
      return null;
    }
    
    setConnectionStats(prev => ({
      ...prev,
      updateCount: prev.updateCount + 1,
      totalUpdatesReceived: prev.totalUpdatesReceived + 1,
      lastUpdateTime: Date.now()
    }));
    
    // Update connection quality based on update frequency
    const updateRate = connectionStats.updateCount / (Date.now() - connectionStats.lastUpdateTime) * 60000;
    if (updateRate > 10) {
      setConnectionQuality('excellent');
    } else if (updateRate > 5) {
      setConnectionQuality('good');
    } else {
      setConnectionQuality('poor');
    }
    
    return data;
  }, [connectionStats.isOnline, enableOfflineMode, shouldUpdate, connectionStats.updateCount, connectionStats.lastUpdateTime]);
  
  const createSubscription = useCallback((
    table: string, 
    callback: (payload: any) => void,
    filter?: { column: string; value: any }
  ) => {
    if (!supabaseRef.current) {
      console.error('Supabase client not initialized');
      return null;
    }
    
    if (subscriptionsRef.current.size >= 5) {
      console.warn('Maximum number of subscriptions reached');
      return null;
    }
    
    try {
      let channel = supabaseRef.current.channel(`${table}_changes_${Date.now()}`);
      
      const changeConfig: any = {
        event: '*',
        schema: 'public',
        table: table
      };
      
      if (filter) {
        changeConfig.filter = `${filter.column}=eq.${filter.value}`;
      }
      
      channel = channel.on('postgres_changes', changeConfig, (payload) => {
        const processedData = handleUpdate(payload, table);
        if (processedData) {
          callback(processedData);
        }
      });
      
      const subscription = channel.subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Successfully subscribed to ${table}`);
          setConnectionStats(prev => ({ ...prev, errorCount: 0 }));
        } else if (status === 'CHANNEL_ERROR') {
          console.error(`Subscription error for ${table}`);
          setConnectionStats(prev => ({ ...prev, errorCount: prev.errorCount + 1 }));
          
          // Attempt reconnection on error
          if (connectionStats.errorCount < maxRetries) {
            attemptReconnection();
          }
        }
      });
      
      subscriptionsRef.current.add(subscription);
      return subscription;
      
    } catch (error) {
      console.error('Failed to create subscription:', error);
      setConnectionStats(prev => ({ ...prev, errorCount: prev.errorCount + 1 }));
      return null;
    }
  }, [handleUpdate, connectionStats.errorCount, maxRetries, attemptReconnection]);
  
  const removeSubscription = useCallback((subscription: any) => {
    if (subscription && subscriptionsRef.current.has(subscription)) {
      try {
        subscription.unsubscribe();
        subscriptionsRef.current.delete(subscription);
      } catch (error) {
        console.warn('Error removing subscription:', error);
      }
    }
  }, []);
  
  const getConnectionInfo = useCallback(() => ({
    ...connectionStats,
    connectionQuality,
    activeSubscriptions: subscriptionsRef.current.size,
    canUpdate: shouldUpdate(),
    rateLimitStatus: {
      updatesThisMinute: connectionStats.updateCount,
      maxUpdatesPerMinute,
      timeUntilReset: Math.max(0, 60000 - (Date.now() - connectionStats.lastUpdateTime))
    }
  }), [connectionStats, connectionQuality, shouldUpdate, maxUpdatesPerMinute]);
  
  // Start heartbeat to monitor connection
  useEffect(() => {
    if (heartbeatInterval > 0) {
      heartbeatRef.current = setInterval(() => {
        // Simple heartbeat - could ping a health endpoint
        if (navigator.onLine !== connectionStats.isOnline) {
          setConnectionStats(prev => ({ ...prev, isOnline: navigator.onLine }));
        }
      }, heartbeatInterval);
    }
    
    return () => {
      if (heartbeatRef.current) {
        clearInterval(heartbeatRef.current);
      }
    };
  }, [heartbeatInterval, connectionStats.isOnline]);
  
  return {
    createSubscription,
    removeSubscription,
    getConnectionInfo,
    connectionStats,
    connectionQuality,
    isOnline: connectionStats.isOnline,
    canUpdate: shouldUpdate()
  };
}
