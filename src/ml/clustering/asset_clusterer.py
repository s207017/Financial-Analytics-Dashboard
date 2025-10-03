"""
Clustering models for grouping correlated assets.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class AssetClusterer:
    """Clustering models for grouping correlated assets."""
    
    def __init__(self):
        """Initialize asset clusterer."""
        self.models = {}
        self.scalers = {}
        self.cluster_labels = {}
        self.feature_importance = {}
    
    def prepare_clustering_features(
        self, 
        returns_data: pd.DataFrame,
        price_data: Optional[pd.DataFrame] = None,
        include_technical: bool = True,
        include_volatility: bool = True,
        include_correlation: bool = True
    ) -> pd.DataFrame:
        """
        Prepare features for clustering.
        
        Args:
            returns_data: DataFrame with asset returns
            price_data: DataFrame with price data (optional)
            include_technical: Whether to include technical indicators
            include_volatility: Whether to include volatility features
            include_correlation: Whether to include correlation features
            
        Returns:
            DataFrame with clustering features
        """
        features_df = pd.DataFrame(index=returns_data.columns)
        
        # Basic return statistics
        features_df['mean_return'] = returns_data.mean()
        features_df['volatility'] = returns_data.std()
        features_df['skewness'] = returns_data.skew()
        features_df['kurtosis'] = returns_data.kurtosis()
        features_df['sharpe_ratio'] = returns_data.mean() / returns_data.std()
        
        # Volatility features
        if include_volatility:
            features_df['vol_5d'] = returns_data.rolling(window=5).std().mean()
            features_df['vol_20d'] = returns_data.rolling(window=20).std().mean()
            features_df['vol_60d'] = returns_data.rolling(window=60).std().mean()
            
            # Volatility of volatility
            vol_series = returns_data.rolling(window=20).std()
            features_df['vol_of_vol'] = vol_series.std()
        
        # Technical indicators (if price data available)
        if include_technical and price_data is not None:
            for symbol in returns_data.columns:
                if symbol in price_data.columns:
                    price_series = price_data[symbol].dropna()
                    
                    # Moving averages
                    sma_20 = price_series.rolling(window=20).mean()
                    sma_50 = price_series.rolling(window=50).mean()
                    
                    # Price ratios
                    features_df.loc[symbol, 'price_sma20_ratio'] = (price_series.iloc[-1] / sma_20.iloc[-1]) if not sma_20.empty else 1
                    features_df.loc[symbol, 'price_sma50_ratio'] = (price_series.iloc[-1] / sma_50.iloc[-1]) if not sma_50.empty else 1
                    
                    # RSI
                    delta = price_series.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    features_df.loc[symbol, 'rsi'] = rsi.iloc[-1] if not rsi.empty else 50
        
        # Correlation features
        if include_correlation:
            corr_matrix = returns_data.corr()
            
            for symbol in returns_data.columns:
                # Average correlation with other assets
                other_corrs = corr_matrix[symbol].drop(symbol)
                features_df.loc[symbol, 'avg_correlation'] = other_corrs.mean()
                features_df.loc[symbol, 'max_correlation'] = other_corrs.max()
                features_df.loc[symbol, 'min_correlation'] = other_corrs.min()
                
                # Number of high correlations
                features_df.loc[symbol, 'high_corr_count'] = (other_corrs > 0.7).sum()
        
        # Remove any remaining NaN values
        features_df = features_df.fillna(features_df.median())
        
        return features_df
    
    def perform_clustering(
        self, 
        features: pd.DataFrame,
        method: str = "kmeans",
        n_clusters: Optional[int] = None,
        random_state: int = 42
    ) -> Dict:
        """
        Perform clustering on asset features.
        
        Args:
            features: Feature matrix
            method: Clustering method (kmeans, hierarchical, dbscan)
            n_clusters: Number of clusters (if None, will be determined)
            random_state: Random state for reproducibility
            
        Returns:
            Dictionary with clustering results
        """
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Determine optimal number of clusters if not specified
        if n_clusters is None:
            n_clusters = self._find_optimal_clusters(features_scaled, method)
        
        # Perform clustering
        if method == "kmeans":
            model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        elif method == "hierarchical":
            model = AgglomerativeClustering(n_clusters=n_clusters)
        elif method == "dbscan":
            model = DBSCAN(eps=0.5, min_samples=2)
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
        cluster_labels = model.fit_predict(features_scaled)
        
        # Calculate clustering metrics
        if method != "dbscan" and len(set(cluster_labels)) > 1:
            silhouette = silhouette_score(features_scaled, cluster_labels)
            calinski_harabasz = calinski_harabasz_score(features_scaled, cluster_labels)
        else:
            silhouette = None
            calinski_harabasz = None
        
        # Store results
        self.models[method] = model
        self.scalers[method] = scaler
        self.cluster_labels[method] = cluster_labels
        
        # Create cluster assignments DataFrame
        cluster_df = pd.DataFrame({
            'asset': features.index,
            'cluster': cluster_labels
        })
        
        results = {
            'method': method,
            'n_clusters': len(set(cluster_labels)),
            'cluster_labels': cluster_labels,
            'cluster_df': cluster_df,
            'silhouette_score': silhouette,
            'calinski_harabasz_score': calinski_harabasz,
            'features': features,
            'features_scaled': features_scaled
        }
        
        logger.info(f"Clustering completed - Method: {method}, Clusters: {len(set(cluster_labels))}")
        if silhouette is not None:
            logger.info(f"Silhouette Score: {silhouette:.4f}")
        
        return results
    
    def _find_optimal_clusters(
        self, 
        features_scaled: np.ndarray, 
        method: str,
        max_clusters: int = 10
    ) -> int:
        """
        Find optimal number of clusters using elbow method and silhouette analysis.
        
        Args:
            features_scaled: Scaled feature matrix
            method: Clustering method
            max_clusters: Maximum number of clusters to test
            
        Returns:
            Optimal number of clusters
        """
        if method == "dbscan":
            return 2  # DBSCAN doesn't require n_clusters
        
        silhouette_scores = []
        inertias = []
        k_range = range(2, min(max_clusters + 1, len(features_scaled)))
        
        for k in k_range:
            if method == "kmeans":
                model = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = model.fit_predict(features_scaled)
                inertias.append(model.inertia_)
            elif method == "hierarchical":
                model = AgglomerativeClustering(n_clusters=k)
                labels = model.fit_predict(features_scaled)
                inertias.append(0)  # Not applicable for hierarchical
            
            if len(set(labels)) > 1:
                silhouette_scores.append(silhouette_score(features_scaled, labels))
            else:
                silhouette_scores.append(0)
        
        # Choose k with highest silhouette score
        optimal_k = k_range[np.argmax(silhouette_scores)]
        
        logger.info(f"Optimal number of clusters: {optimal_k}")
        
        return optimal_k
    
    def analyze_clusters(
        self, 
        features: pd.DataFrame,
        cluster_labels: np.ndarray,
        method: str = "kmeans"
    ) -> Dict:
        """
        Analyze cluster characteristics.
        
        Args:
            features: Feature matrix
            cluster_labels: Cluster assignments
            method: Clustering method used
            
        Returns:
            Dictionary with cluster analysis
        """
        cluster_df = pd.DataFrame({
            'asset': features.index,
            'cluster': cluster_labels
        })
        
        # Cluster statistics
        cluster_stats = {}
        for cluster_id in sorted(set(cluster_labels)):
            cluster_assets = cluster_df[cluster_df['cluster'] == cluster_id]['asset'].tolist()
            cluster_features = features.loc[cluster_assets]
            
            cluster_stats[cluster_id] = {
                'assets': cluster_assets,
                'size': len(cluster_assets),
                'mean_features': cluster_features.mean().to_dict(),
                'std_features': cluster_features.std().to_dict()
            }
        
        # Feature importance for clustering
        if method == "kmeans" and method in self.models:
            # For K-means, we can look at cluster centers
            centers = self.models[method].cluster_centers_
            feature_names = features.columns
            
            feature_importance = {}
            for i, feature in enumerate(feature_names):
                feature_importance[feature] = np.std(centers[:, i])
            
            self.feature_importance[method] = feature_importance
        
        analysis = {
            'cluster_stats': cluster_stats,
            'cluster_df': cluster_df,
            'feature_importance': self.feature_importance.get(method, {}),
            'total_clusters': len(set(cluster_labels)),
            'cluster_sizes': [len(cluster_df[cluster_df['cluster'] == c]) for c in sorted(set(cluster_labels))]
        }
        
        return analysis
    
    def get_cluster_portfolio_weights(
        self, 
        cluster_labels: np.ndarray,
        assets: List[str],
        method: str = "equal_weight"
    ) -> Dict[int, Dict[str, float]]:
        """
        Generate portfolio weights based on clusters.
        
        Args:
            cluster_labels: Cluster assignments
            assets: List of asset names
            method: Weighting method (equal_weight, risk_parity, market_cap)
            
        Returns:
            Dictionary with cluster portfolio weights
        """
        cluster_weights = {}
        
        for cluster_id in sorted(set(cluster_labels)):
            cluster_assets = [assets[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
            
            if method == "equal_weight":
                weights = {asset: 1.0 / len(cluster_assets) for asset in cluster_assets}
            elif method == "risk_parity":
                # Simplified risk parity - equal risk contribution
                weights = {asset: 1.0 / len(cluster_assets) for asset in cluster_assets}
            else:
                weights = {asset: 1.0 / len(cluster_assets) for asset in cluster_assets}
            
            cluster_weights[cluster_id] = weights
        
        return cluster_weights
    
    def visualize_clusters(
        self, 
        features: pd.DataFrame,
        cluster_labels: np.ndarray,
        method: str = "pca",
        save_path: Optional[str] = None
    ) -> None:
        """
        Visualize clusters using dimensionality reduction.
        
        Args:
            features: Feature matrix
            cluster_labels: Cluster assignments
            method: Visualization method (pca, tsne)
            save_path: Path to save plot (optional)
        """
        if method == "pca":
            # PCA for visualization
            pca = PCA(n_components=2)
            features_2d = pca.fit_transform(features)
            
            plt.figure(figsize=(10, 8))
            scatter = plt.scatter(features_2d[:, 0], features_2d[:, 1], c=cluster_labels, cmap='viridis', alpha=0.7)
            plt.colorbar(scatter)
            plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
            plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
            plt.title('Asset Clusters (PCA Visualization)')
            
            # Add asset labels
            for i, asset in enumerate(features.index):
                plt.annotate(asset, (features_2d[i, 0], features_2d[i, 1]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        elif method == "dendrogram":
            # Hierarchical clustering dendrogram
            linkage_matrix = linkage(features, method='ward')
            
            plt.figure(figsize=(12, 8))
            dendrogram(linkage_matrix, labels=features.index, leaf_rotation=90)
            plt.title('Asset Clustering Dendrogram')
            plt.xlabel('Assets')
            plt.ylabel('Distance')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
