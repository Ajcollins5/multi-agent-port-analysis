import asyncio
import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor
import time

from .base_agent import BaseAgent
from ..utils.cache_manager import cache_market_data, cached
from ..utils.circuit_breaker import yfinance_circuit_breaker

class EnhancedRiskAgent(BaseAgent):
    """
    Optimized Risk Agent with advanced analytics, parallel processing, and intelligent caching
    """
    
    def __init__(self):
        super().__init__("EnhancedRiskAgent")
        self.risk_thresholds = {
            'volatility': {'low': 0.15, 'medium': 0.25, 'high': 0.35},
            'beta': {'low': 0.8, 'medium': 1.2, 'high': 1.5},
            'volume_spike': {'low': 1.5, 'medium': 2.0, 'high': 3.0},
            'price_change': {'low': 0.03, 'medium': 0.05, 'high': 0.08}
        }
        self.confidence_weights = {
            'data_quality': 0.3,
            'time_coverage': 0.2,
            'market_conditions': 0.2,
            'volatility_consistency': 0.3
        }
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    @cache_market_data(ttl=300)  # Cache for 5 minutes
    async def fetch_optimized_stock_data(self, ticker: str, period: str = "30d") -> Dict[str, Any]:
        """
        Optimized stock data fetching with circuit breaker and advanced metrics
        """
        try:
            # Use circuit breaker for external API calls
            stock_data = await yfinance_circuit_breaker.call(self._fetch_yfinance_data, ticker, period)
            
            if not stock_data["success"]:
                return stock_data
            
            # Calculate advanced metrics in parallel
            hist = stock_data["hist"]
            
            # Parallel calculation of metrics
            tasks = [
                self._calculate_volatility_metrics(hist),
                self._calculate_momentum_indicators(hist),
                self._calculate_volume_metrics(hist),
                self._calculate_risk_metrics(hist)
            ]
            
            metrics_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine all metrics
            combined_metrics = {
                "ticker": ticker,
                "success": True,
                "data_points": len(hist),
                "period": period,
                "timestamp": datetime.now().isoformat()
            }
            
            for result in metrics_results:
                if isinstance(result, dict):
                    combined_metrics.update(result)
                else:
                    logging.warning(f"Metric calculation failed: {result}")
            
            # Store performance metric
            await self.store_system_metric(
                metric_type="stock_data_fetch_optimized",
                metric_value=1,
                additional_data={
                    "ticker": ticker,
                    "data_points": len(hist),
                    "metrics_calculated": len([r for r in metrics_results if isinstance(r, dict)])
                }
            )
            
            return combined_metrics
            
        except Exception as e:
            error_msg = f"Optimized fetch failed for {ticker}: {str(e)}"
            logging.error(error_msg)
            
            await self.store_system_metric(
                metric_type="stock_data_fetch_optimized",
                metric_value=0,
                additional_data={"ticker": ticker, "error": error_msg}
            )
            
            return {"success": False, "error": error_msg}
    
    async def _fetch_yfinance_data(self, ticker: str, period: str) -> Dict[str, Any]:
        """Internal method for yfinance data fetching"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {"success": False, "error": f"No data for {ticker}"}
            
            return {"success": True, "hist": hist, "ticker": ticker}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_volatility_metrics(self, hist: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive volatility metrics"""
        try:
            returns = hist['Close'].pct_change().dropna()
            
            # Multiple volatility measures
            volatility_1d = returns.std()
            volatility_annualized = volatility_1d * np.sqrt(252)
            
            # Rolling volatility for trend analysis
            rolling_vol = returns.rolling(window=10).std()
            vol_trend = (rolling_vol.iloc[-1] - rolling_vol.iloc[-5]) / rolling_vol.iloc[-5] if len(rolling_vol) >= 5 else 0
            
            # Volatility of volatility (vol clustering)
            vol_of_vol = rolling_vol.std() if len(rolling_vol) > 1 else 0
            
            # Downside deviation (risk-adjusted measure)
            negative_returns = returns[returns < 0]
            downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
            
            return {
                "volatility_daily": volatility_1d,
                "volatility_annualized": volatility_annualized,
                "volatility_trend": vol_trend,
                "volatility_of_volatility": vol_of_vol,
                "downside_deviation": downside_deviation,
                "volatility_percentile": np.percentile(rolling_vol.dropna(), 75) if len(rolling_vol) > 4 else volatility_1d
            }
            
        except Exception as e:
            logging.error(f"Volatility calculation error: {e}")
            return {"volatility_annualized": 0.0}
    
    async def _calculate_momentum_indicators(self, hist: pd.DataFrame) -> Dict[str, float]:
        """Calculate momentum and trend indicators"""
        try:
            close_prices = hist['Close']
            
            # Price momentum
            price_change_1d = (close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2] if len(close_prices) >= 2 else 0
            price_change_5d = (close_prices.iloc[-1] - close_prices.iloc[-6]) / close_prices.iloc[-6] if len(close_prices) >= 6 else 0
            price_change_20d = (close_prices.iloc[-1] - close_prices.iloc[-21]) / close_prices.iloc[-21] if len(close_prices) >= 21 else 0
            
            # Moving averages
            ma_5 = close_prices.rolling(window=5).mean().iloc[-1] if len(close_prices) >= 5 else close_prices.iloc[-1]
            ma_20 = close_prices.rolling(window=20).mean().iloc[-1] if len(close_prices) >= 20 else close_prices.iloc[-1]
            
            # Relative position to moving averages
            price_to_ma5 = (close_prices.iloc[-1] - ma_5) / ma_5
            price_to_ma20 = (close_prices.iloc[-1] - ma_20) / ma_20
            
            # RSI-like momentum
            gains = close_prices.diff().clip(lower=0)
            losses = -close_prices.diff().clip(upper=0)
            avg_gain = gains.rolling(window=14).mean().iloc[-1] if len(gains) >= 14 else 0
            avg_loss = losses.rolling(window=14).mean().iloc[-1] if len(losses) >= 14 else 0
            
            rsi = 100 - (100 / (1 + (avg_gain / avg_loss))) if avg_loss != 0 else 50
            
            return {
                "price_change_1d": price_change_1d,
                "price_change_5d": price_change_5d,
                "price_change_20d": price_change_20d,
                "price_to_ma5": price_to_ma5,
                "price_to_ma20": price_to_ma20,
                "rsi": rsi,
                "momentum_score": (price_change_5d + price_to_ma5 + (rsi - 50) / 50) / 3
            }
            
        except Exception as e:
            logging.error(f"Momentum calculation error: {e}")
            return {"price_change_1d": 0.0}
    
    async def _calculate_volume_metrics(self, hist: pd.DataFrame) -> Dict[str, float]:
        """Calculate volume-based risk indicators"""
        try:
            volume = hist['Volume']
            close_prices = hist['Close']
            
            # Volume statistics
            avg_volume = volume.mean()
            current_volume = volume.iloc[-1]
            volume_spike = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volume trend
            volume_ma5 = volume.rolling(window=5).mean().iloc[-1] if len(volume) >= 5 else current_volume
            volume_trend = (current_volume - volume_ma5) / volume_ma5 if volume_ma5 > 0 else 0
            
            # Price-volume relationship
            price_changes = close_prices.pct_change()
            volume_changes = volume.pct_change()
            
            # Correlation between price and volume changes
            pv_correlation = price_changes.corr(volume_changes) if len(price_changes) > 10 else 0
            
            # Volume-weighted average price deviation
            vwap = (close_prices * volume).sum() / volume.sum() if volume.sum() > 0 else close_prices.mean()
            vwap_deviation = (close_prices.iloc[-1] - vwap) / vwap
            
            return {
                "volume_spike": volume_spike,
                "volume_trend": volume_trend,
                "price_volume_correlation": pv_correlation,
                "vwap_deviation": vwap_deviation,
                "volume_consistency": 1 - (volume.std() / avg_volume) if avg_volume > 0 else 0
            }
            
        except Exception as e:
            logging.error(f"Volume calculation error: {e}")
            return {"volume_spike": 1.0}
    
    async def _calculate_risk_metrics(self, hist: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        try:
            returns = hist['Close'].pct_change().dropna()
            
            # Value at Risk (VaR) - 95% confidence
            var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
            
            # Expected Shortfall (Conditional VaR)
            es_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else var_95
            
            # Maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Sharpe ratio approximation (assuming risk-free rate of 2%)
            excess_returns = returns - (0.02 / 252)  # Daily risk-free rate
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # Skewness and kurtosis
            skewness = returns.skew() if len(returns) > 2 else 0
            kurtosis = returns.kurtosis() if len(returns) > 3 else 0
            
            return {
                "var_95": var_95,
                "expected_shortfall": es_95,
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe_ratio,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "tail_risk_score": abs(skewness) + max(0, kurtosis - 3)  # Excess kurtosis
            }
            
        except Exception as e:
            logging.error(f"Risk metrics calculation error: {e}")
            return {"var_95": 0.0}
    
    async def analyze_stock_risk_enhanced(self, ticker: str) -> Dict[str, Any]:
        """
        Enhanced stock risk analysis with comprehensive metrics and intelligent scoring
        """
        try:
            # Fetch optimized data
            stock_data = await self.fetch_optimized_stock_data(ticker)
            
            if not stock_data["success"]:
                return stock_data
            
            # Calculate composite risk score
            risk_score = await self._calculate_composite_risk_score(stock_data)
            
            # Determine risk level with more nuanced thresholds
            risk_level, impact_level = self._determine_risk_levels(risk_score, stock_data)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(stock_data)
            
            # Generate intelligent insights
            insights = self._generate_risk_insights(stock_data, risk_score)
            
            # Create comprehensive result
            result = {
                "success": True,
                "ticker": ticker,
                "risk_level": risk_level,
                "impact_level": impact_level,
                "risk_score": risk_score,
                "confidence": confidence,
                "insights": insights,
                "metrics": {
                    "volatility": stock_data.get("volatility_annualized", 0),
                    "var_95": stock_data.get("var_95", 0),
                    "max_drawdown": stock_data.get("max_drawdown", 0),
                    "sharpe_ratio": stock_data.get("sharpe_ratio", 0),
                    "volume_spike": stock_data.get("volume_spike", 1),
                    "momentum_score": stock_data.get("momentum_score", 0)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Store enhanced insight
            await self.store_insight(
                ticker=ticker,
                insight=f"Enhanced risk analysis: {risk_level} risk (score: {risk_score:.1f}). {insights['primary_insight']}",
                volatility=stock_data.get("volatility_annualized"),
                impact_level=impact_level,
                confidence=confidence,
                metadata={
                    "analysis_type": "enhanced_risk",
                    "risk_score": risk_score,
                    "metrics": result["metrics"],
                    "insights_count": len(insights.get("detailed_insights", []))
                }
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Enhanced risk analysis failed for {ticker}: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
    
    async def _calculate_composite_risk_score(self, data: Dict[str, Any]) -> float:
        """Calculate a composite risk score from multiple metrics"""
        try:
            # Weight different risk factors
            weights = {
                'volatility': 0.25,
                'tail_risk': 0.20,
                'momentum': 0.15,
                'volume': 0.15,
                'drawdown': 0.15,
                'var': 0.10
            }
            
            # Normalize metrics to 0-100 scale
            volatility_score = min(100, (data.get("volatility_annualized", 0) / 0.5) * 100)
            tail_risk_score = min(100, data.get("tail_risk_score", 0) * 20)
            momentum_score = abs(data.get("momentum_score", 0)) * 100
            volume_score = min(100, max(0, data.get("volume_spike", 1) - 1) * 50)
            drawdown_score = min(100, abs(data.get("max_drawdown", 0)) * 200)
            var_score = min(100, abs(data.get("var_95", 0)) * 1000)
            
            # Calculate weighted composite score
            composite_score = (
                volatility_score * weights['volatility'] +
                tail_risk_score * weights['tail_risk'] +
                momentum_score * weights['momentum'] +
                volume_score * weights['volume'] +
                drawdown_score * weights['drawdown'] +
                var_score * weights['var']
            )
            
            return min(100, composite_score)
            
        except Exception as e:
            logging.error(f"Composite risk score calculation error: {e}")
            return 50.0  # Default medium risk
    
    def _determine_risk_levels(self, risk_score: float, data: Dict[str, Any]) -> Tuple[str, str]:
        """Determine risk and impact levels based on composite score and specific metrics"""
        # Base determination on composite score
        if risk_score >= 70:
            base_risk = "HIGH"
            base_impact = "HIGH"
        elif risk_score >= 40:
            base_risk = "MEDIUM"
            base_impact = "MEDIUM"
        else:
            base_risk = "LOW"
            base_impact = "LOW"
        
        # Adjust based on specific high-risk indicators
        volatility = data.get("volatility_annualized", 0)
        volume_spike = data.get("volume_spike", 1)
        max_drawdown = abs(data.get("max_drawdown", 0))
        
        # Override to HIGH if any critical threshold is exceeded
        if volatility > 0.4 or volume_spike > 3.0 or max_drawdown > 0.2:
            return "HIGH", "HIGH"
        
        return base_risk, base_impact
    
    def _calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data quality and consistency"""
        try:
            # Data quality factors
            data_points = data.get("data_points", 0)
            data_quality = min(1.0, data_points / 30)  # 30 days is ideal
            
            # Time coverage (how recent and complete the data is)
            time_coverage = 0.9  # Assume good coverage for now
            
            # Market conditions factor (lower confidence during high volatility periods)
            volatility = data.get("volatility_annualized", 0)
            market_conditions = max(0.5, 1.0 - (volatility / 0.5))  # Lower confidence for high vol
            
            # Volatility consistency (how stable the volatility measure is)
            vol_of_vol = data.get("volatility_of_volatility", 0)
            volatility_consistency = max(0.5, 1.0 - (vol_of_vol / 0.1))
            
            # Weighted confidence score
            confidence = (
                data_quality * self.confidence_weights['data_quality'] +
                time_coverage * self.confidence_weights['time_coverage'] +
                market_conditions * self.confidence_weights['market_conditions'] +
                volatility_consistency * self.confidence_weights['volatility_consistency']
            )
            
            return min(0.95, max(0.3, confidence))  # Bound between 30% and 95%
            
        except Exception as e:
            logging.error(f"Confidence calculation error: {e}")
            return 0.7  # Default confidence
    
    def _generate_risk_insights(self, data: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
        """Generate intelligent insights based on the analysis"""
        insights = {
            "primary_insight": "",
            "detailed_insights": [],
            "recommendations": []
        }
        
        try:
            # Primary insight based on dominant risk factor
            volatility = data.get("volatility_annualized", 0)
            volume_spike = data.get("volume_spike", 1)
            momentum = data.get("momentum_score", 0)
            
            if volatility > 0.3:
                insights["primary_insight"] = f"High volatility ({volatility:.1%}) is the primary risk driver"
            elif volume_spike > 2.0:
                insights["primary_insight"] = f"Unusual volume activity ({volume_spike:.1f}x normal) indicates potential volatility"
            elif abs(momentum) > 0.5:
                insights["primary_insight"] = f"Strong momentum ({momentum:.2f}) suggests trend continuation risk"
            else:
                insights["primary_insight"] = f"Moderate risk profile with balanced metrics"
            
            # Detailed insights
            if data.get("max_drawdown", 0) < -0.15:
                insights["detailed_insights"].append("Significant historical drawdowns indicate potential for large losses")
            
            if data.get("sharpe_ratio", 0) < 0:
                insights["detailed_insights"].append("Negative risk-adjusted returns suggest poor risk/reward profile")
            
            if data.get("tail_risk_score", 0) > 2:
                insights["detailed_insights"].append("High tail risk indicates potential for extreme price movements")
            
            # Recommendations
            if risk_score > 70:
                insights["recommendations"].extend([
                    "Consider reducing position size",
                    "Implement stop-loss orders",
                    "Monitor closely for exit opportunities"
                ])
            elif risk_score > 40:
                insights["recommendations"].extend([
                    "Maintain current position with caution",
                    "Set alerts for volatility changes"
                ])
            else:
                insights["recommendations"].append("Position appears suitable for current risk tolerance")
            
        except Exception as e:
            logging.error(f"Insight generation error: {e}")
            insights["primary_insight"] = "Analysis completed with limited insights due to data constraints"
        
        return insights

# Global enhanced risk agent instance
enhanced_risk_agent = EnhancedRiskAgent()
