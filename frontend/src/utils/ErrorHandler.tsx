// Standardized Error Handling for Better UX

interface UserFriendlyError {
  title: string;
  message: string;
  actionable: boolean;
  retryable: boolean;
  supportContact?: string;
}

class ErrorHandler {
  static formatForUser(error: any): UserFriendlyError {
    // Convert technical errors to user-friendly messages
    if (error.message?.includes('timeout')) {
      return {
        title: "Analysis Taking Longer Than Expected",
        message: "Our AI agents are working hard on your analysis. Please try again in a moment.",
        actionable: true,
        retryable: true
      };
    }
    
    if (error.message?.includes('rate limit')) {
      return {
        title: "Too Many Requests",
        message: "Please wait a moment before requesting another analysis.",
        actionable: true,
        retryable: true
      };
    }
    
    // Default fallback
    return {
      title: "Something Went Wrong",
      message: "We're experiencing technical difficulties. Our team has been notified.",
      actionable: false,
      retryable: true,
      supportContact: "support@example.com"
    };
  }
}