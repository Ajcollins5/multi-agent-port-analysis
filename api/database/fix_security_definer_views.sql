-- Fix for SECURITY DEFINER views - Security vulnerability remediation
-- This script replaces the problematic views with secure alternatives

-- Drop existing views that use SECURITY DEFINER
DROP VIEW IF EXISTS public.system_health;
DROP VIEW IF EXISTS public.portfolio_summary;
DROP VIEW IF EXISTS public.recent_insights;

-- Create secure system_health view without SECURITY DEFINER
-- This view provides system health metrics based on recent data
CREATE VIEW public.system_health AS
SELECT 
    'overall' as component,
    CASE 
        WHEN COUNT(DISTINCT sm.metric_type) >= 3 THEN 'healthy'
        WHEN COUNT(DISTINCT sm.metric_type) >= 1 THEN 'warning'
        ELSE 'critical'
    END as status,
    COUNT(DISTINCT sm.metric_type) as active_metrics,
    MAX(sm.timestamp) as last_metric_time,
    AVG(CASE WHEN sm.metric_type = 'response_time' THEN sm.metric_value END) as avg_response_time,
    COUNT(CASE WHEN i.created_at > NOW() - INTERVAL '1 hour' THEN 1 END) as insights_last_hour,
    COUNT(CASE WHEN e.created_at > NOW() - INTERVAL '1 hour' THEN 1 END) as events_last_hour
FROM system_metrics sm
FULL OUTER JOIN insights i ON true
FULL OUTER JOIN events e ON true
WHERE sm.timestamp > NOW() - INTERVAL '24 hours' OR sm.timestamp IS NULL
GROUP BY 1;

-- Create secure portfolio_summary view without SECURITY DEFINER
-- This view provides an overview of portfolio analysis metrics
CREATE VIEW public.portfolio_summary AS
SELECT 
    COALESCE(pa.portfolio_size, 0) as portfolio_size,
    COALESCE(pa.analyzed_stocks, 0) as analyzed_stocks,
    COALESCE(pa.high_impact_count, 0) as high_impact_count,
    COALESCE(pa.portfolio_risk, 'UNKNOWN') as portfolio_risk,
    pa.timestamp as last_analysis,
    COALESCE(pa.analysis_duration, 0) as analysis_duration,
    -- Calculate additional metrics from related tables
    COUNT(DISTINCT i.ticker) as unique_tickers_with_insights,
    COUNT(CASE WHEN i.impact_level = 'HIGH' THEN 1 END) as high_impact_insights,
    COUNT(CASE WHEN e.severity IN ('HIGH', 'CRITICAL') THEN 1 END) as critical_events,
    AVG(i.confidence) as avg_confidence,
    MAX(i.timestamp) as last_insight_time,
    MAX(e.timestamp) as last_event_time
FROM portfolio_analysis pa
LEFT JOIN insights i ON i.timestamp > NOW() - INTERVAL '24 hours'
LEFT JOIN events e ON e.timestamp > NOW() - INTERVAL '24 hours'
WHERE pa.timestamp = (
    SELECT MAX(timestamp) FROM portfolio_analysis
)
GROUP BY 
    pa.portfolio_size, 
    pa.analyzed_stocks, 
    pa.high_impact_count, 
    pa.portfolio_risk, 
    pa.timestamp, 
    pa.analysis_duration;

-- Create secure recent_insights view without SECURITY DEFINER
-- This view provides recent insights with key metadata
CREATE VIEW public.recent_insights AS
SELECT 
    i.id,
    i.ticker,
    i.insight,
    i.agent,
    i.timestamp,
    i.impact_level,
    i.confidence,
    i.volatility,
    i.refined,
    -- Add contextual information
    ROW_NUMBER() OVER (PARTITION BY i.ticker ORDER BY i.timestamp DESC) as insight_rank,
    COUNT(*) OVER (PARTITION BY i.ticker) as total_insights_for_ticker,
    COUNT(*) OVER (PARTITION BY i.agent) as total_insights_from_agent,
    -- Add time-based context
    EXTRACT(EPOCH FROM (NOW() - i.timestamp)) / 3600 as hours_ago,
    CASE 
        WHEN i.timestamp > NOW() - INTERVAL '1 hour' THEN 'very_recent'
        WHEN i.timestamp > NOW() - INTERVAL '6 hours' THEN 'recent'
        WHEN i.timestamp > NOW() - INTERVAL '24 hours' THEN 'today'
        ELSE 'older'
    END as recency_category
FROM insights i
WHERE i.timestamp > NOW() - INTERVAL '7 days'  -- Only show insights from last 7 days
ORDER BY i.timestamp DESC;

-- Enable RLS on the views if needed (views inherit RLS from base tables)
-- Note: Views don't support RLS directly, but they inherit security from base tables

-- Add comments to document the security changes
COMMENT ON VIEW public.system_health IS 'System health metrics view - Removed SECURITY DEFINER for improved security';
COMMENT ON VIEW public.portfolio_summary IS 'Portfolio analysis summary view - Removed SECURITY DEFINER for improved security';
COMMENT ON VIEW public.recent_insights IS 'Recent insights view - Removed SECURITY DEFINER for improved security';

-- Grant appropriate permissions to roles
-- These grants ensure the views work properly with your RLS policies
GRANT SELECT ON public.system_health TO authenticated;
GRANT SELECT ON public.portfolio_summary TO authenticated;
GRANT SELECT ON public.recent_insights TO authenticated;

-- Service role should have full access (matching your existing RLS policies)
GRANT SELECT ON public.system_health TO service_role;
GRANT SELECT ON public.portfolio_summary TO service_role;
GRANT SELECT ON public.recent_insights TO service_role; 