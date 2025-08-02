-- News Intelligence Database Schema
-- Stores compressed news snapshots and stock personality data

-- News snapshots table - stores the 2-sentence compressed articles
CREATE TABLE IF NOT EXISTS news_snapshots (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    category VARCHAR(50) NOT NULL, -- earnings, product_launch, regulatory, etc.
    impact VARCHAR(20) NOT NULL, -- very_positive, positive, neutral, negative, very_negative
    price_change_1h DECIMAL(8,4) NOT NULL, -- percentage change 1 hour after news
    price_change_24h DECIMAL(8,4) NOT NULL, -- percentage change 24 hours after news
    summary_line_1 TEXT NOT NULL, -- First sentence - what happened
    summary_line_2 TEXT NOT NULL, -- Second sentence - market reaction
    source_url TEXT, -- Original article URL
    confidence_score DECIMAL(3,2) NOT NULL, -- 0.00 to 1.00
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stock personalities table - aggregated analysis of how stocks react to news
CREATE TABLE IF NOT EXISTS stock_personalities (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    total_events INTEGER NOT NULL DEFAULT 0,
    avg_volatility DECIMAL(8,4) NOT NULL DEFAULT 0, -- average absolute price change
    sentiment_sensitivity DECIMAL(3,2) NOT NULL DEFAULT 0.5, -- 0.0 to 1.0
    news_momentum DECIMAL(3,2) NOT NULL DEFAULT 0.5, -- how quickly stock reacts
    reaction_patterns JSONB, -- category -> {avg_impact, frequency, volatility}
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reaction patterns table - detailed breakdown by category
CREATE TABLE IF NOT EXISTS reaction_patterns (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    category VARCHAR(50) NOT NULL,
    avg_impact DECIMAL(8,4) NOT NULL, -- average price change for this category
    frequency DECIMAL(3,2) NOT NULL, -- how often this category appears (0.0 to 1.0)
    volatility DECIMAL(8,4) NOT NULL, -- average absolute price change
    event_count INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ticker, category)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_news_snapshots_ticker ON news_snapshots(ticker);
CREATE INDEX IF NOT EXISTS idx_news_snapshots_timestamp ON news_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_news_snapshots_category ON news_snapshots(category);
CREATE INDEX IF NOT EXISTS idx_news_snapshots_impact ON news_snapshots(impact);
CREATE INDEX IF NOT EXISTS idx_news_snapshots_ticker_timestamp ON news_snapshots(ticker, timestamp);

CREATE INDEX IF NOT EXISTS idx_stock_personalities_ticker ON stock_personalities(ticker);
CREATE INDEX IF NOT EXISTS idx_reaction_patterns_ticker ON reaction_patterns(ticker);
CREATE INDEX IF NOT EXISTS idx_reaction_patterns_category ON reaction_patterns(category);

-- Views for common queries

-- Recent news snapshots with impact analysis
CREATE OR REPLACE VIEW recent_news_analysis AS
SELECT 
    ns.ticker,
    ns.timestamp,
    ns.category,
    ns.impact,
    ns.price_change_1h,
    ns.price_change_24h,
    ns.summary_line_1,
    ns.summary_line_2,
    ns.confidence_score,
    sp.avg_volatility as stock_avg_volatility,
    sp.sentiment_sensitivity,
    sp.news_momentum
FROM news_snapshots ns
LEFT JOIN stock_personalities sp ON ns.ticker = sp.ticker
WHERE ns.timestamp >= NOW() - INTERVAL '30 days'
ORDER BY ns.timestamp DESC;

-- Stock personality summary with event counts
CREATE OR REPLACE VIEW stock_personality_summary AS
SELECT 
    sp.ticker,
    sp.total_events,
    sp.avg_volatility,
    sp.sentiment_sensitivity,
    sp.news_momentum,
    sp.last_updated,
    COUNT(ns.id) as recent_events_30d,
    AVG(ABS(ns.price_change_24h)) as recent_avg_volatility_30d
FROM stock_personalities sp
LEFT JOIN news_snapshots ns ON sp.ticker = ns.ticker 
    AND ns.timestamp >= NOW() - INTERVAL '30 days'
GROUP BY sp.ticker, sp.total_events, sp.avg_volatility, 
         sp.sentiment_sensitivity, sp.news_momentum, sp.last_updated
ORDER BY sp.total_events DESC;

-- Category impact analysis
CREATE OR REPLACE VIEW category_impact_analysis AS
SELECT 
    category,
    COUNT(*) as total_events,
    AVG(price_change_24h) as avg_impact,
    STDDEV(price_change_24h) as impact_volatility,
    AVG(confidence_score) as avg_confidence,
    COUNT(CASE WHEN impact IN ('positive', 'very_positive') THEN 1 END) as positive_events,
    COUNT(CASE WHEN impact IN ('negative', 'very_negative') THEN 1 END) as negative_events
FROM news_snapshots
WHERE timestamp >= NOW() - INTERVAL '365 days'
GROUP BY category
ORDER BY total_events DESC;

-- Trigger to update stock personalities when new snapshots are added
CREATE OR REPLACE FUNCTION update_stock_personality()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert stock personality
    INSERT INTO stock_personalities (ticker, total_events, avg_volatility, last_updated)
    VALUES (
        NEW.ticker,
        1,
        ABS(NEW.price_change_24h),
        NOW()
    )
    ON CONFLICT (ticker) DO UPDATE SET
        total_events = stock_personalities.total_events + 1,
        avg_volatility = (
            (stock_personalities.avg_volatility * stock_personalities.total_events + ABS(NEW.price_change_24h)) 
            / (stock_personalities.total_events + 1)
        ),
        last_updated = NOW();
    
    -- Update reaction patterns
    INSERT INTO reaction_patterns (ticker, category, avg_impact, frequency, volatility, event_count)
    VALUES (
        NEW.ticker,
        NEW.category,
        NEW.price_change_24h,
        1.0 / (SELECT total_events FROM stock_personalities WHERE ticker = NEW.ticker),
        ABS(NEW.price_change_24h),
        1
    )
    ON CONFLICT (ticker, category) DO UPDATE SET
        avg_impact = (
            (reaction_patterns.avg_impact * reaction_patterns.event_count + NEW.price_change_24h)
            / (reaction_patterns.event_count + 1)
        ),
        volatility = (
            (reaction_patterns.volatility * reaction_patterns.event_count + ABS(NEW.price_change_24h))
            / (reaction_patterns.event_count + 1)
        ),
        event_count = reaction_patterns.event_count + 1,
        frequency = (
            reaction_patterns.event_count + 1
        )::DECIMAL / (SELECT total_events FROM stock_personalities WHERE ticker = NEW.ticker),
        last_updated = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_stock_personality ON news_snapshots;
CREATE TRIGGER trigger_update_stock_personality
    AFTER INSERT ON news_snapshots
    FOR EACH ROW
    EXECUTE FUNCTION update_stock_personality();

-- Sample data for testing
INSERT INTO news_snapshots (ticker, category, impact, price_change_1h, price_change_24h, summary_line_1, summary_line_2, confidence_score) VALUES
('AAPL', 'earnings', 'positive', 2.1, 3.4, 'AAPL reported quarterly earnings with key metrics showing strong performance.', 'The stock rose 3.4% in 24 hours as investors embraced the news.', 0.87),
('AAPL', 'product_launch', 'very_positive', 1.8, 5.2, 'AAPL announced a new product launch that exceeded market expectations.', 'The stock surged 5.2% in 24 hours as investors embraced the news.', 0.92),
('AAPL', 'analyst_rating', 'negative', -1.2, -2.8, 'AAPL received analyst downgrade that negatively impacts its business prospects.', 'The stock fell 2.8% in 24 hours as investors rejected the news.', 0.75),
('TSLA', 'earnings', 'very_positive', 4.2, 8.1, 'TSLA reported quarterly earnings with key metrics showing strong performance.', 'The stock surged 8.1% in 24 hours as investors embraced the news.', 0.89),
('TSLA', 'regulatory', 'negative', -2.1, -4.3, 'TSLA received regulatory news that negatively impacts its business prospects.', 'The stock fell 4.3% in 24 hours as investors rejected the news.', 0.82);

-- Comments explaining the schema design
COMMENT ON TABLE news_snapshots IS 'Stores compressed 2-sentence news articles with price impact data';
COMMENT ON TABLE stock_personalities IS 'Aggregated personality profiles showing how stocks typically react to news';
COMMENT ON TABLE reaction_patterns IS 'Detailed breakdown of how stocks react to different categories of news';

COMMENT ON COLUMN news_snapshots.summary_line_1 IS 'First sentence: what happened in the news';
COMMENT ON COLUMN news_snapshots.summary_line_2 IS 'Second sentence: how the market reacted';
COMMENT ON COLUMN stock_personalities.sentiment_sensitivity IS 'How much stock reacts to sentiment vs fundamentals (0.0 to 1.0)';
COMMENT ON COLUMN stock_personalities.news_momentum IS 'How quickly stock reacts to news (0.0 to 1.0)';
COMMENT ON COLUMN reaction_patterns.frequency IS 'How often this category appears for this stock (0.0 to 1.0)';
