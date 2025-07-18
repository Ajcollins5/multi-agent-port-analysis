-- Supabase Migration Schema
-- Multi-Agent Portfolio Analysis System
-- Migration from SQLite to PostgreSQL with real-time capabilities

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Set timezone to UTC
ALTER DATABASE postgres SET timezone TO 'UTC';

-- Create insights table
CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker TEXT NOT NULL,
    insight TEXT NOT NULL,
    agent TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    volatility REAL,
    impact_level TEXT CHECK (impact_level IN ('LOW', 'MEDIUM', 'HIGH')),
    confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB DEFAULT '{}',
    refined BOOLEAN DEFAULT FALSE,
    original_insight TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    ticker TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT DEFAULT 'INFO' CHECK (severity IN ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    volatility REAL,
    volume_spike REAL,
    portfolio_risk TEXT CHECK (portfolio_risk IN ('LOW', 'MEDIUM', 'HIGH')),
    correlation_data JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create knowledge_evolution table
CREATE TABLE IF NOT EXISTS knowledge_evolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker TEXT NOT NULL,
    evolution_type TEXT NOT NULL,
    previous_insight TEXT,
    refined_insight TEXT NOT NULL,
    improvement_score REAL CHECK (improvement_score >= 0 AND improvement_score <= 1),
    agent TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    context TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create portfolio_analysis table
CREATE TABLE IF NOT EXISTS portfolio_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_size INTEGER NOT NULL CHECK (portfolio_size > 0),
    analyzed_stocks INTEGER NOT NULL CHECK (analyzed_stocks >= 0),
    high_impact_count INTEGER NOT NULL CHECK (high_impact_count >= 0),
    portfolio_risk TEXT NOT NULL CHECK (portfolio_risk IN ('LOW', 'MEDIUM', 'HIGH')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_duration REAL DEFAULT 0,
    agents_used TEXT[] DEFAULT '{}',
    synthesis_summary TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create system_metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type TEXT NOT NULL,
    metric_value REAL NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    additional_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_insights_ticker ON insights(ticker);
CREATE INDEX IF NOT EXISTS idx_insights_agent ON insights(agent);
CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON insights(timestamp);
CREATE INDEX IF NOT EXISTS idx_insights_impact_level ON insights(impact_level);
CREATE INDEX IF NOT EXISTS idx_insights_ticker_agent ON insights(ticker, agent);
CREATE INDEX IF NOT EXISTS idx_insights_metadata ON insights USING GIN(metadata);

CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_ticker ON events(ticker);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_ticker_severity ON events(ticker, severity);
CREATE INDEX IF NOT EXISTS idx_events_metadata ON events USING GIN(metadata);

CREATE INDEX IF NOT EXISTS idx_knowledge_ticker ON knowledge_evolution(ticker);
CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_evolution(evolution_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_agent ON knowledge_evolution(agent);
CREATE INDEX IF NOT EXISTS idx_knowledge_timestamp ON knowledge_evolution(timestamp);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata ON knowledge_evolution USING GIN(metadata);

CREATE INDEX IF NOT EXISTS idx_portfolio_timestamp ON portfolio_analysis(timestamp);
CREATE INDEX IF NOT EXISTS idx_portfolio_risk ON portfolio_analysis(portfolio_risk);
CREATE INDEX IF NOT EXISTS idx_portfolio_metadata ON portfolio_analysis USING GIN(metadata);

CREATE INDEX IF NOT EXISTS idx_metrics_type ON system_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_type_timestamp ON system_metrics(metric_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_additional_data ON system_metrics USING GIN(additional_data);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for insights table
CREATE TRIGGER update_insights_updated_at BEFORE UPDATE ON insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_evolution ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_metrics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for service role (backend operations)
CREATE POLICY "Service role can do everything on insights" ON insights
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role can do everything on events" ON events
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role can do everything on knowledge_evolution" ON knowledge_evolution
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role can do everything on portfolio_analysis" ON portfolio_analysis
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role can do everything on system_metrics" ON system_metrics
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Create policies for authenticated users (frontend read access)
CREATE POLICY "Authenticated users can read insights" ON insights
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can read events" ON events
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can read knowledge_evolution" ON knowledge_evolution
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can read portfolio_analysis" ON portfolio_analysis
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can read system_metrics" ON system_metrics
    FOR SELECT USING (auth.role() = 'authenticated');

-- Enable realtime for all tables
ALTER TABLE insights REPLICA IDENTITY FULL;
ALTER TABLE events REPLICA IDENTITY FULL;
ALTER TABLE knowledge_evolution REPLICA IDENTITY FULL;
ALTER TABLE portfolio_analysis REPLICA IDENTITY FULL;
ALTER TABLE system_metrics REPLICA IDENTITY FULL;

-- Add tables to realtime publication
ALTER PUBLICATION supabase_realtime ADD TABLE insights;
ALTER PUBLICATION supabase_realtime ADD TABLE events;
ALTER PUBLICATION supabase_realtime ADD TABLE knowledge_evolution;
ALTER PUBLICATION supabase_realtime ADD TABLE portfolio_analysis;
ALTER PUBLICATION supabase_realtime ADD TABLE system_metrics;

-- Create helpful views for common queries
CREATE VIEW insights_summary AS
SELECT 
    agent,
    ticker,
    impact_level,
    COUNT(*) as total_insights,
    AVG(confidence) as avg_confidence,
    MAX(timestamp) as last_updated
FROM insights
GROUP BY agent, ticker, impact_level;

CREATE VIEW portfolio_risk_trends AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    portfolio_risk,
    COUNT(*) as analysis_count,
    AVG(high_impact_count) as avg_high_impact,
    AVG(analysis_duration) as avg_duration
FROM portfolio_analysis
GROUP BY DATE_TRUNC('hour', timestamp), portfolio_risk
ORDER BY hour DESC;

-- Create function for cleanup of old data
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    cutoff_date TIMESTAMP WITH TIME ZONE;
    deleted_count INTEGER := 0;
BEGIN
    cutoff_date := NOW() - INTERVAL '1 day' * days_to_keep;
    
    -- Delete old insights
    DELETE FROM insights WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Delete old events
    DELETE FROM events WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
    
    -- Delete old system metrics
    DELETE FROM system_metrics WHERE created_at < cutoff_date;
    GET DIAGNOSTICS deleted_count = deleted_count + ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comment the schema
COMMENT ON TABLE insights IS 'Stores AI-generated insights from portfolio analysis agents';
COMMENT ON TABLE events IS 'Stores real-time events and alerts from portfolio monitoring';
COMMENT ON TABLE knowledge_evolution IS 'Tracks the evolution and refinement of AI insights over time';
COMMENT ON TABLE portfolio_analysis IS 'Stores comprehensive portfolio analysis results';
COMMENT ON TABLE system_metrics IS 'Stores system performance and health metrics'; 