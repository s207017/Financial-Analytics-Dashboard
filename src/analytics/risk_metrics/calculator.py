"""
Risk metrics calculator for portfolio analysis.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from scipy import stats
from scipy.optimize import minimize_scalar

logger = logging.getLogger(__name__)


class RiskCalculator:
    """Risk metrics calculator for portfolio analysis."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize risk calculator.
        
        Args:
            risk_free_rate: Risk-free rate for risk-adjusted metrics
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_sharpe_ratio(
        self, 
        returns: pd.Series, 
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Portfolio returns
            risk_free_rate: Risk-free rate (if None, uses instance default)
            
        Returns:
            Sharpe ratio
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return excess_returns.mean() / returns.std() * np.sqrt(252)
    
    def calculate_sortino_ratio(
        self, 
        returns: pd.Series, 
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sortino ratio (downside deviation).
        
        Args:
            returns: Portfolio returns
            risk_free_rate: Risk-free rate (if None, uses instance default)
            
        Returns:
            Sortino ratio
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        excess_returns = returns - risk_free_rate / 252
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return np.inf
        
        downside_deviation = downside_returns.std() * np.sqrt(252)
        return excess_returns.mean() / downside_deviation * np.sqrt(252)
    
    def calculate_calmar_ratio(self, returns: pd.Series) -> float:
        """
        Calculate Calmar ratio (annual return / max drawdown).
        
        Args:
            returns: Portfolio returns
            
        Returns:
            Calmar ratio
        """
        annual_return = returns.mean() * 252
        max_drawdown = self.calculate_max_drawdown(returns)
        
        if max_drawdown == 0:
            return np.inf
        
        return annual_return / abs(max_drawdown)
    
    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        Calculate maximum drawdown.
        
        Args:
            returns: Portfolio returns
            
        Returns:
            Maximum drawdown (negative value)
        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def calculate_var(
        self, 
        returns: pd.Series, 
        confidence_level: float = 0.05
    ) -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Portfolio returns
            confidence_level: Confidence level (e.g., 0.05 for 95% VaR)
            
        Returns:
            VaR value
        """
        return np.percentile(returns, confidence_level * 100)
    
    def calculate_cvar(
        self, 
        returns: pd.Series, 
        confidence_level: float = 0.05
    ) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) / Expected Shortfall.
        
        Args:
            returns: Portfolio returns
            confidence_level: Confidence level (e.g., 0.05 for 95% CVaR)
            
        Returns:
            CVaR value
        """
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
    
    def calculate_beta(
        self, 
        portfolio_returns: pd.Series, 
        market_returns: pd.Series
    ) -> float:
        """
        Calculate portfolio beta.
        
        Args:
            portfolio_returns: Portfolio returns
            market_returns: Market returns (benchmark)
            
        Returns:
            Beta coefficient
        """
        # Align the series
        aligned_data = pd.concat([portfolio_returns, market_returns], axis=1, join='inner')
        portfolio_aligned = aligned_data.iloc[:, 0]
        market_aligned = aligned_data.iloc[:, 1]
        
        covariance = np.cov(portfolio_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)
        
        return covariance / market_variance if market_variance > 0 else 0
    
    def calculate_tracking_error(
        self, 
        portfolio_returns: pd.Series, 
        benchmark_returns: pd.Series
    ) -> float:
        """
        Calculate tracking error.
        
        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Tracking error (annualized)
        """
        # Align the series
        aligned_data = pd.concat([portfolio_returns, benchmark_returns], axis=1, join='inner')
        portfolio_aligned = aligned_data.iloc[:, 0]
        benchmark_aligned = aligned_data.iloc[:, 1]
        
        excess_returns = portfolio_aligned - benchmark_aligned
        return excess_returns.std() * np.sqrt(252)
    
    def calculate_information_ratio(
        self, 
        portfolio_returns: pd.Series, 
        benchmark_returns: pd.Series
    ) -> float:
        """
        Calculate information ratio.
        
        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Information ratio
        """
        # Align the series
        aligned_data = pd.concat([portfolio_returns, benchmark_returns], axis=1, join='inner')
        portfolio_aligned = aligned_data.iloc[:, 0]
        benchmark_aligned = aligned_data.iloc[:, 1]
        
        excess_returns = portfolio_aligned - benchmark_aligned
        tracking_error = excess_returns.std()
        
        return excess_returns.mean() / tracking_error * np.sqrt(252) if tracking_error > 0 else 0
    
    def calculate_volatility(self, returns: pd.Series, window: int = 30) -> pd.Series:
        """
        Calculate rolling volatility.
        
        Args:
            returns: Portfolio returns
            window: Rolling window size
            
        Returns:
            Rolling volatility series
        """
        return returns.rolling(window=window).std() * np.sqrt(252)
    
    def calculate_correlation_matrix(self, returns_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate correlation matrix.
        
        Args:
            returns_data: DataFrame with asset returns
            
        Returns:
            Correlation matrix
        """
        return returns_data.corr()
    
    def calculate_risk_metrics(
        self, 
        portfolio_returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        confidence_levels: List[float] = [0.05, 0.01]
    ) -> Dict:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            portfolio_returns: Portfolio returns
            benchmark_returns: Benchmark returns (optional)
            confidence_levels: List of confidence levels for VaR/CVaR
            
        Returns:
            Dictionary with risk metrics
        """
        metrics = {}
        
        # Basic risk metrics
        metrics['sharpe_ratio'] = self.calculate_sharpe_ratio(portfolio_returns)
        metrics['sortino_ratio'] = self.calculate_sortino_ratio(portfolio_returns)
        metrics['calmar_ratio'] = self.calculate_calmar_ratio(portfolio_returns)
        metrics['max_drawdown'] = self.calculate_max_drawdown(portfolio_returns)
        metrics['volatility'] = portfolio_returns.std() * np.sqrt(252)
        metrics['annual_return'] = portfolio_returns.mean() * 252
        
        # VaR and CVaR
        for conf_level in confidence_levels:
            metrics[f'var_{int((1-conf_level)*100)}'] = self.calculate_var(portfolio_returns, conf_level)
            metrics[f'cvar_{int((1-conf_level)*100)}'] = self.calculate_cvar(portfolio_returns, conf_level)
        
        # Benchmark-relative metrics
        if benchmark_returns is not None:
            metrics['beta'] = self.calculate_beta(portfolio_returns, benchmark_returns)
            metrics['tracking_error'] = self.calculate_tracking_error(portfolio_returns, benchmark_returns)
            metrics['information_ratio'] = self.calculate_information_ratio(portfolio_returns, benchmark_returns)
            
            # Excess returns
            aligned_data = pd.concat([portfolio_returns, benchmark_returns], axis=1, join='inner')
            excess_returns = aligned_data.iloc[:, 0] - aligned_data.iloc[:, 1]
            metrics['excess_return'] = excess_returns.mean() * 252
            metrics['excess_volatility'] = excess_returns.std() * np.sqrt(252)
        
        return metrics
    
    def calculate_risk_attribution(
        self, 
        portfolio_weights: Dict[str, float],
        returns_data: pd.DataFrame,
        cov_matrix: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        Calculate risk attribution for portfolio components.
        
        Args:
            portfolio_weights: Dictionary with asset weights
            returns_data: DataFrame with asset returns
            cov_matrix: Covariance matrix (if None, calculated from returns)
            
        Returns:
            Dictionary with risk attribution
        """
        if cov_matrix is None:
            cov_matrix = returns_data.cov()
        
        # Convert weights to array
        assets = list(portfolio_weights.keys())
        weights = np.array([portfolio_weights[asset] for asset in assets])
        
        # Portfolio volatility
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix.loc[assets, assets], weights)))
        
        # Risk contributions
        marginal_contrib = np.dot(cov_matrix.loc[assets, assets], weights) / portfolio_vol
        risk_contrib = weights * marginal_contrib
        
        # Risk attribution
        attribution = {}
        for i, asset in enumerate(assets):
            attribution[asset] = {
                'weight': weights[i],
                'risk_contribution': risk_contrib[i],
                'risk_contribution_pct': risk_contrib[i] / portfolio_vol * 100,
                'marginal_risk_contribution': marginal_contrib[i]
            }
        
        return {
            'portfolio_volatility': portfolio_vol,
            'attribution': attribution
        }
