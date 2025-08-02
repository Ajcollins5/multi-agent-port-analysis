-- High-Traffic Query Analysis

-- Current bottleneck: Insights retrieval by ticker
-- Query: SELECT * FROM insights WHERE ticker = ? ORDER BY created_at DESC
-- Current performance: 200-500ms for popular tickers

-- Optimization 1: Add covering index
CREATE INDEX CONCURRENTLY idx_insights_ticker_covering 
ON insights(ticker, created_at DESC) 
INCLUDE (insight, confidence, impact_level, metadata);

-- Optimization 2: Partition large tables by date
CREATE TABLE insights_2024_01 PARTITION OF insights 
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Expected improvement: 200-500ms → 50-100ms (60-80% reduction)