"""
Portfolio optimization using Modern Portfolio Theory and other methods.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from scipy.optimize import minimize
import cvxpy as cp

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """Portfolio optimization using various methods."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize portfolio optimizer.
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_expected_returns(self, returns_data: pd.DataFrame, method: str = "mean") -> np.ndarray:
        """
        Calculate expected returns.
        
        Args:
            returns_data: DataFrame with asset returns
            method: Method for calculating expected returns (mean, capm, black_litterman)
            
        Returns:
            Array of expected returns
        """
        if method == "mean":
            return returns_data.mean().values
        elif method == "capm":
            # Simplified CAPM - would need market data in practice
            return returns_data.mean().values
        else:
            return returns_data.mean().values
    
    def calculate_covariance_matrix(self, returns_data: pd.DataFrame, method: str = "sample") -> np.ndarray:
        """
        Calculate covariance matrix.
        
        Args:
            returns_data: DataFrame with asset returns
            method: Method for covariance calculation (sample, shrinkage, exponential)
            
        Returns:
            Covariance matrix
        """
        if method == "sample":
            return returns_data.cov().values
        elif method == "shrinkage":
            # Ledoit-Wolf shrinkage estimator
            sample_cov = returns_data.cov().values
            n = len(returns_data.columns)
            T = len(returns_data)
            
            # Shrinkage target (identity matrix scaled by average variance)
            avg_var = np.trace(sample_cov) / n
            target = np.eye(n) * avg_var
            
            # Shrinkage intensity
            shrinkage_intensity = min(1, max(0, (T - n - 2) / (T - 1)))
            
            return (1 - shrinkage_intensity) * sample_cov + shrinkage_intensity * target
        else:
            return returns_data.cov().values
    
    def markowitz_optimization(
        self, 
        expected_returns: np.ndarray, 
        cov_matrix: np.ndarray,
        target_return: Optional[float] = None,
        risk_aversion: float = 1.0
    ) -> Tuple[np.ndarray, float, float]:
        """
        Markowitz mean-variance optimization.
        
        Args:
            expected_returns: Expected returns vector
            cov_matrix: Covariance matrix
            target_return: Target portfolio return (if None, maximizes Sharpe ratio)
            risk_aversion: Risk aversion parameter
            
        Returns:
            Tuple of (weights, expected_return, volatility)
        """
        n = len(expected_returns)
        
        if target_return is not None:
            # Minimize variance for given return
            def objective(weights):
                return np.dot(weights, np.dot(cov_matrix, weights))
            
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # weights sum to 1
                {'type': 'eq', 'fun': lambda w: np.dot(w, expected_returns) - target_return}  # target return
            ]
            
            bounds = [(0, 1) for _ in range(n)]  # long-only constraints
            
        else:
            # Maximize Sharpe ratio
            def objective(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                return -(portfolio_return - self.risk_free_rate) / portfolio_vol
            
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # weights sum to 1
            ]
            
            bounds = [(0, 1) for _ in range(n)]  # long-only constraints
        
        # Initial guess
        x0 = np.ones(n) / n
        
        # Optimize
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            logger.warning("Optimization failed, using equal weights")
            weights = np.ones(n) / n
        else:
            weights = result.x
        
        # Calculate portfolio metrics
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        
        return weights, portfolio_return, portfolio_vol
    
    def efficient_frontier(
        self, 
        expected_returns: np.ndarray, 
        cov_matrix: np.ndarray,
        num_portfolios: int = 100
    ) -> Tuple[List[float], List[float], List[np.ndarray]]:
        """
        Generate efficient frontier.
        
        Args:
            expected_returns: Expected returns vector
            cov_matrix: Covariance matrix
            num_portfolios: Number of portfolios to generate
            
        Returns:
            Tuple of (returns, volatilities, weights_list)
        """
        min_ret = expected_returns.min()
        max_ret = expected_returns.max()
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        returns = []
        volatilities = []
        weights_list = []
        
        for target_ret in target_returns:
            try:
                weights, port_ret, port_vol = self.markowitz_optimization(
                    expected_returns, cov_matrix, target_return=target_ret
                )
                returns.append(port_ret)
                volatilities.append(port_vol)
                weights_list.append(weights)
            except:
                continue
        
        return returns, volatilities, weights_list
    
    def black_litterman_optimization(
        self, 
        market_caps: np.ndarray,
        cov_matrix: np.ndarray,
        risk_aversion: float = 3.0,
        views: Optional[Dict] = None,
        confidence: Optional[Dict] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Black-Litterman optimization.
        
        Args:
            market_caps: Market capitalizations
            cov_matrix: Covariance matrix
            risk_aversion: Risk aversion parameter
            views: Dictionary of views (optional)
            confidence: Dictionary of confidence levels (optional)
            
        Returns:
            Tuple of (expected_returns, weights)
        """
        n = len(market_caps)
        
        # Market portfolio weights
        market_weights = market_caps / market_caps.sum()
        
        # Implied equilibrium returns
        implied_returns = risk_aversion * np.dot(cov_matrix, market_weights)
        
        if views is None:
            # No views - return market portfolio
            return implied_returns, market_weights
        
        # Black-Litterman with views
        # This is a simplified implementation
        # In practice, you'd need more sophisticated view specification
        
        # For now, return market portfolio
        return implied_returns, market_weights
    
    def risk_parity_optimization(
        self, 
        cov_matrix: np.ndarray,
        target_risk: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Risk parity optimization.
        
        Args:
            cov_matrix: Covariance matrix
            target_risk: Target risk contributions (if None, equal risk)
            
        Returns:
            Portfolio weights
        """
        n = cov_matrix.shape[0]
        
        if target_risk is None:
            target_risk = np.ones(n) / n
        
        def risk_contributions(weights):
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            return contrib / contrib.sum()
        
        def objective(weights):
            contrib = risk_contributions(weights)
            return np.sum((contrib - target_risk) ** 2)
        
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]
        
        bounds = [(0, 1) for _ in range(n)]
        x0 = np.ones(n) / n
        
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if not result.success:
            logger.warning("Risk parity optimization failed, using equal weights")
            return np.ones(n) / n
        
        return result.x
    
    def optimize_portfolio(
        self, 
        returns_data: pd.DataFrame,
        method: str = "markowitz",
        **kwargs
    ) -> Dict:
        """
        Main portfolio optimization method.
        
        Args:
            returns_data: DataFrame with asset returns
            method: Optimization method (markowitz, risk_parity, black_litterman)
            **kwargs: Additional parameters for specific methods
            
        Returns:
            Dictionary with optimization results
        """
        # Calculate expected returns and covariance matrix
        expected_returns = self.calculate_expected_returns(returns_data)
        cov_matrix = self.calculate_covariance_matrix(returns_data)
        
        if method == "markowitz":
            weights, portfolio_return, portfolio_vol = self.markowitz_optimization(
                expected_returns, cov_matrix, **kwargs
            )
            
        elif method == "risk_parity":
            weights = self.risk_parity_optimization(cov_matrix, **kwargs)
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            
        elif method == "black_litterman":
            # This would need market cap data in practice
            market_caps = np.ones(len(expected_returns))  # Placeholder
            expected_returns, weights = self.black_litterman_optimization(
                market_caps, cov_matrix, **kwargs
            )
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            
        else:
            raise ValueError(f"Unknown optimization method: {method}")
        
        # Calculate additional metrics
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        
        # Create results dictionary
        results = {
            'weights': dict(zip(returns_data.columns, weights)),
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'method': method,
            'assets': list(returns_data.columns)
        }
        
        return results
