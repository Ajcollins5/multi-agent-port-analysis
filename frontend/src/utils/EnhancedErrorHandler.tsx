import React from 'react';
import toast from 'react-hot-toast';

// OPTIMIZATION: Enhanced error categorization and handling
interface ErrorContext {
  component?: string;
  action?: string;
  ticker?: string;
  timestamp?: string;
  userId?: string;
  sessionId?: string;
}

interface ErrorMetrics {
  errorCount: number;
  lastErrorTime: number;
  errorTypes: Record<string, number>;
  recoveryAttempts: number;
}

interface UserFriendlyError {
  title: string;
  message: string;
  actionable: boolean;
  retryable: boolean;
  supportContact?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'network' | 'api' | 'validation' | 'permission' | 'system' | 'unknown';
  suggestedActions?: string[];
}

class EnhancedErrorHandler {
  private static errorMetrics: ErrorMetrics = {
    errorCount: 0,
    lastErrorTime: 0,
    errorTypes: {},
    recoveryAttempts: 0
  };

  private static errorQueue: Array<{error: any, context: ErrorContext, timestamp: number}> = [];
  private static maxQueueSize = 50;
  private static reportingThreshold = 5; // Report after 5 errors

  static formatForUser(error: any, context: ErrorContext = {}): UserFriendlyError {
    const errorMessage = error?.message || error?.toString() || 'Unknown error';
    const errorType = this.categorizeError(error);
    
    // Update metrics
    this.updateMetrics(errorType);
    
    // Add to error queue for analysis
    this.addToQueue(error, context);
    
    // OPTIMIZATION: Specific error handling for news pipeline
    if (errorMessage.includes('timeout') || errorMessage.includes('TIMEOUT')) {
      return {
        title: "Request Timeout",
        message: "The news analysis is taking longer than expected. This might be due to high server load.",
        actionable: true,
        retryable: true,
        severity: 'medium',
        category: 'network',
        suggestedActions: [
          "Wait a moment and try again",
          "Check your internet connection",
          "Try analyzing fewer stocks at once"
        ]
      };
    }
    
    if (errorMessage.includes('rate limit') || errorMessage.includes('429')) {
      return {
        title: "Rate Limit Exceeded",
        message: "Too many requests have been made. Please wait before trying again.",
        actionable: true,
        retryable: true,
        severity: 'medium',
        category: 'api',
        suggestedActions: [
          "Wait 1-2 minutes before retrying",
          "Reduce the frequency of requests",
          "Consider upgrading your plan for higher limits"
        ]
      };
    }
    
    if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
      return {
        title: "Network Connection Issue",
        message: "Unable to connect to our servers. Please check your internet connection.",
        actionable: true,
        retryable: true,
        severity: 'high',
        category: 'network',
        suggestedActions: [
          "Check your internet connection",
          "Try refreshing the page",
          "Disable VPN if using one"
        ]
      };
    }
    
    if (errorMessage.includes('unauthorized') || errorMessage.includes('401')) {
      return {
        title: "Authentication Required",
        message: "Your session has expired. Please log in again.",
        actionable: true,
        retryable: false,
        severity: 'high',
        category: 'permission',
        suggestedActions: [
          "Refresh the page",
          "Clear browser cache",
          "Contact support if issue persists"
        ]
      };
    }
    
    if (errorMessage.includes('validation') || errorMessage.includes('invalid')) {
      return {
        title: "Invalid Input",
        message: "The provided information is not valid. Please check your input and try again.",
        actionable: true,
        retryable: true,
        severity: 'low',
        category: 'validation',
        suggestedActions: [
          "Check ticker symbol format (e.g., AAPL)",
          "Ensure all required fields are filled",
          "Verify date ranges are valid"
        ]
      };
    }
    
    if (errorMessage.includes('quota') || errorMessage.includes('limit exceeded')) {
      return {
        title: "Usage Limit Reached",
        message: "You've reached your usage limit for this feature.",
        actionable: true,
        retryable: false,
        severity: 'medium',
        category: 'api',
        suggestedActions: [
          "Wait until your quota resets",
          "Consider upgrading your plan",
          "Contact support for assistance"
        ]
      };
    }
    
    // OPTIMIZATION: Handle specific news pipeline errors
    if (context.component === 'NewsIntelligenceDashboard') {
      if (errorMessage.includes('no data') || errorMessage.includes('empty')) {
        return {
          title: "No News Data Available",
          message: "No news articles found for the selected criteria.",
          actionable: true,
          retryable: true,
          severity: 'low',
          category: 'api',
          suggestedActions: [
            "Try a different ticker symbol",
            "Expand the date range",
            "Check if the market is open"
          ]
        };
      }
    }
    
    // Default fallback with enhanced context
    return {
      title: "Unexpected Error",
      message: this.getContextualMessage(context),
      actionable: false,
      retryable: true,
      severity: 'medium',
      category: 'system',
      supportContact: "support@newsanalysis.com",
      suggestedActions: [
        "Try refreshing the page",
        "Clear browser cache",
        "Contact support with error details"
      ]
    };
  }

  private static categorizeError(error: any): string {
    const message = error?.message || error?.toString() || '';
    
    if (message.includes('network') || message.includes('fetch')) return 'network';
    if (message.includes('timeout')) return 'timeout';
    if (message.includes('rate limit') || message.includes('429')) return 'rate_limit';
    if (message.includes('unauthorized') || message.includes('401')) return 'auth';
    if (message.includes('validation') || message.includes('invalid')) return 'validation';
    if (message.includes('quota') || message.includes('limit')) return 'quota';
    
    return 'unknown';
  }

  private static updateMetrics(errorType: string) {
    this.errorMetrics.errorCount++;
    this.errorMetrics.lastErrorTime = Date.now();
    this.errorMetrics.errorTypes[errorType] = (this.errorMetrics.errorTypes[errorType] || 0) + 1;
  }

  private static addToQueue(error: any, context: ErrorContext) {
    this.errorQueue.push({
      error,
      context,
      timestamp: Date.now()
    });

    // Maintain queue size
    if (this.errorQueue.length > this.maxQueueSize) {
      this.errorQueue.shift();
    }

    // Auto-report if threshold reached
    if (this.errorMetrics.errorCount % this.reportingThreshold === 0) {
      this.reportErrors();
    }
  }

  private static getContextualMessage(context: ErrorContext): string {
    if (context.component === 'NewsIntelligenceDashboard') {
      return "There was an issue loading the news intelligence dashboard. Our team has been notified.";
    }
    
    if (context.component === 'AutomatedPipelineDashboard') {
      return "The automated news pipeline encountered an error. Please try again in a moment.";
    }
    
    if (context.action === 'fetch_news') {
      return "Unable to fetch the latest news data. Please check your connection and try again.";
    }
    
    return "We're experiencing technical difficulties. Our team has been notified and is working on a fix.";
  }

  static async reportErrors() {
    try {
      // OPTIMIZATION: Batch error reporting to reduce API calls
      const recentErrors = this.errorQueue.slice(-10); // Last 10 errors
      
      await fetch('/api/error-reporting', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          errors: recentErrors,
          metrics: this.errorMetrics,
          userAgent: navigator.userAgent,
          url: window.location.href,
          timestamp: Date.now()
        })
      });
    } catch (reportingError) {
      console.error('Failed to report errors:', reportingError);
    }
  }

  static getMetrics(): ErrorMetrics {
    return { ...this.errorMetrics };
  }

  static clearMetrics() {
    this.errorMetrics = {
      errorCount: 0,
      lastErrorTime: 0,
      errorTypes: {},
      recoveryAttempts: 0
    };
    this.errorQueue = [];
  }

  // OPTIMIZATION: Smart retry logic with exponential backoff
  static async retryWithBackoff<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000,
    context: ErrorContext = {}
  ): Promise<T> {
    let lastError: any;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        if (attempt > 0) {
          this.errorMetrics.recoveryAttempts++;
        }
        
        return await operation();
      } catch (error) {
        lastError = error;
        
        if (attempt === maxRetries) {
          break;
        }
        
        // Calculate delay with exponential backoff and jitter
        const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
        
        console.warn(`Attempt ${attempt + 1} failed, retrying in ${delay}ms:`, error);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError;
  }

  // OPTIMIZATION: Toast notifications with smart deduplication
  static showErrorToast(error: any, context: ErrorContext = {}) {
    const userError = this.formatForUser(error, context);
    
    // Deduplicate similar errors
    const errorKey = `${userError.title}_${userError.category}`;
    const now = Date.now();
    const lastShown = this.getLastToastTime(errorKey);
    
    if (now - lastShown < 5000) { // Don't show same error within 5 seconds
      return;
    }
    
    this.setLastToastTime(errorKey, now);
    
    const toastOptions = {
      duration: userError.severity === 'critical' ? 8000 : 4000,
      icon: this.getErrorIcon(userError.severity),
      style: {
        background: this.getErrorColor(userError.severity),
        color: 'white',
      }
    };
    
    toast.error(`${userError.title}: ${userError.message}`, toastOptions);
    
    // Show suggested actions if available
    if (userError.suggestedActions && userError.suggestedActions.length > 0) {
      setTimeout(() => {
        toast(
          <div>
            <strong>Suggested actions:</strong>
            <ul className="mt-1 text-sm">
              {userError.suggestedActions!.slice(0, 2).map((action, index) => (
                <li key={index}>• {action}</li>
              ))}
            </ul>
          </div>,
          { duration: 6000, icon: '💡' }
        );
      }, 1000);
    }
  }

  private static toastTimes: Record<string, number> = {};
  
  private static getLastToastTime(key: string): number {
    return this.toastTimes[key] || 0;
  }
  
  private static setLastToastTime(key: string, time: number) {
    this.toastTimes[key] = time;
  }

  private static getErrorIcon(severity: string): string {
    switch (severity) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return 'ℹ️';
      default: return '❌';
    }
  }

  private static getErrorColor(severity: string): string {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'high': return '#ea580c';
      case 'medium': return '#d97706';
      case 'low': return '#2563eb';
      default: return '#6b7280';
    }
  }
}

export default EnhancedErrorHandler;
export type { UserFriendlyError, ErrorContext, ErrorMetrics };
