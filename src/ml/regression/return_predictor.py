"""
Regression models for predicting asset returns.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class ReturnPredictor:
    """Regression models for predicting asset returns."""
    
    def __init__(self):
        """Initialize return predictor."""
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
    
    def prepare_features(
        self, 
        data: pd.DataFrame,
        target_column: str = "returns",
        lag_periods: List[int] = [1, 5, 10, 20],
        technical_indicators: bool = True,
        macro_features: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for regression.
        
        Args:
            data: DataFrame with price/return data
            target_column: Target variable column
            lag_periods: List of lag periods for features
            technical_indicators: Whether to include technical indicators
            macro_features: DataFrame with macroeconomic features
            
        Returns:
            Tuple of (features_df, target_series)
        """
        features_df = pd.DataFrame(index=data.index)
        
        # Lag features
        for lag in lag_periods:
            features_df[f'returns_lag_{lag}'] = data[target_column].shift(lag)
            features_df[f'volatility_lag_{lag}'] = data[target_column].rolling(window=lag).std().shift(1)
        
        # Technical indicators
        if technical_indicators and 'close' in data.columns:
            # Moving averages
            features_df['sma_5'] = data['close'].rolling(window=5).mean()
            features_df['sma_20'] = data['close'].rolling(window=20).mean()
            features_df['sma_50'] = data['close'].rolling(window=50).mean()
            
            # Price ratios
            features_df['price_sma5_ratio'] = data['close'] / features_df['sma_5']
            features_df['price_sma20_ratio'] = data['close'] / features_df['sma_20']
            features_df['price_sma50_ratio'] = data['close'] / features_df['sma_50']
            
            # Volatility
            features_df['volatility_5'] = data[target_column].rolling(window=5).std()
            features_df['volatility_20'] = data[target_column].rolling(window=20).std()
            
            # RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            features_df['rsi'] = 100 - (100 / (1 + rs))
        
        # Macroeconomic features
        if macro_features is not None:
            # Align macro data with price data
            for col in macro_features.columns:
                if col != 'date':
                    features_df[f'macro_{col}'] = macro_features[col]
        
        # Remove rows with NaN values
        features_df = features_df.dropna()
        
        # Align target with features
        target_series = data[target_column].loc[features_df.index]
        
        return features_df, target_series
    
    def train_model(
        self, 
        features: pd.DataFrame, 
        target: pd.Series,
        model_name: str = "linear",
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """
        Train regression model.
        
        Args:
            features: Feature matrix
            target: Target variable
            model_name: Model type (linear, ridge, lasso, elastic, rf, gb, svr)
            test_size: Test set size
            random_state: Random state for reproducibility
            
        Returns:
            Dictionary with model results
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=test_size, random_state=random_state, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Initialize model
        if model_name == "linear":
            model = LinearRegression()
        elif model_name == "ridge":
            model = Ridge(alpha=1.0)
        elif model_name == "lasso":
            model = Lasso(alpha=0.1)
        elif model_name == "elastic":
            model = ElasticNet(alpha=0.1, l1_ratio=0.5)
        elif model_name == "rf":
            model = RandomForestRegressor(n_estimators=100, random_state=random_state)
        elif model_name == "gb":
            model = GradientBoostingRegressor(n_estimators=100, random_state=random_state)
        elif model_name == "svr":
            model = SVR(kernel='rbf', C=1.0, gamma='scale')
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Train model
        if model_name in ["rf", "gb"]:
            # Tree-based models don't need scaling
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        else:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        if model_name in ["rf", "gb"]:
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        else:
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(features.columns, model.feature_importances_))
        elif hasattr(model, 'coef_'):
            importance = dict(zip(features.columns, np.abs(model.coef_)))
        else:
            importance = {}
        
        # Store model and scaler
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        self.feature_importance[model_name] = importance
        
        results = {
            'model_name': model_name,
            'mse': mse,
            'mae': mae,
            'r2': r2,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': importance,
            'predictions': y_pred,
            'actual': y_test
        }
        
        logger.info(f"Trained {model_name} model - R²: {r2:.4f}, CV R²: {cv_scores.mean():.4f}")
        
        return results
    
    def predict_returns(
        self, 
        features: pd.DataFrame, 
        model_name: str = "linear"
    ) -> np.ndarray:
        """
        Predict returns using trained model.
        
        Args:
            features: Feature matrix
            model_name: Model to use for prediction
            
        Returns:
            Predicted returns
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model = self.models[model_name]
        scaler = self.scalers[model_name]
        
        # Scale features if needed
        if model_name in ["rf", "gb"]:
            predictions = model.predict(features)
        else:
            features_scaled = scaler.transform(features)
            predictions = model.predict(features_scaled)
        
        return predictions
    
    def backtest_strategy(
        self, 
        data: pd.DataFrame,
        features: pd.DataFrame,
        model_name: str = "linear",
        rebalance_frequency: int = 5,
        transaction_cost: float = 0.001
    ) -> Dict:
        """
        Backtest trading strategy based on predictions.
        
        Args:
            data: DataFrame with price data
            features: Feature matrix
            model_name: Model to use
            rebalance_frequency: Rebalancing frequency (days)
            transaction_cost: Transaction cost per trade
            
        Returns:
            Dictionary with backtest results
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        # Generate predictions
        predictions = self.predict_returns(features, model_name)
        
        # Create trading signals
        signals = np.where(predictions > 0, 1, -1)  # Simple long/short strategy
        
        # Calculate returns
        returns = data['returns'].loc[features.index]
        strategy_returns = signals * returns
        
        # Apply transaction costs
        position_changes = np.diff(signals, prepend=signals[0])
        transaction_costs = np.abs(position_changes) * transaction_cost
        strategy_returns = strategy_returns - transaction_costs
        
        # Calculate performance metrics
        cumulative_returns = (1 + strategy_returns).cumprod()
        total_return = cumulative_returns.iloc[-1] - 1
        volatility = strategy_returns.std() * np.sqrt(252)
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
        max_drawdown = self._calculate_max_drawdown(cumulative_returns)
        
        results = {
            'total_return': total_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'strategy_returns': strategy_returns,
            'cumulative_returns': cumulative_returns,
            'signals': signals,
            'predictions': predictions
        }
        
        return results
    
    def _calculate_max_drawdown(self, cumulative_returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown.min()
    
    def get_feature_importance(self, model_name: str, top_n: int = 10) -> Dict:
        """
        Get top N most important features.
        
        Args:
            model_name: Model name
            top_n: Number of top features to return
            
        Returns:
            Dictionary with top features
        """
        if model_name not in self.feature_importance:
            return {}
        
        importance = self.feature_importance[model_name]
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return dict(sorted_features[:top_n])
