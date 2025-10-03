#!/usr/bin/env python3
"""
Script to create sample portfolios in the database for testing and demonstration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.data_access.portfolio_management_service import PortfolioManagementService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_portfolios():
    """Create sample portfolios for demonstration."""
    
    try:
        portfolio_service = PortfolioManagementService()
        
        # Sample portfolios with different strategies and asset allocations
        sample_portfolios = [
            {
                "name": "Tech Growth Portfolio",
                "description": "High-growth technology stocks with equal weighting for diversification",
                "symbols": ["AAPL", "GOOGL", "MSFT", "NVDA", "META"],
                "weights": [0.2, 0.2, 0.2, 0.2, 0.2],  # Equal weight
                "strategy": "Equal Weight"
            },
            {
                "name": "Conservative Income Portfolio",
                "description": "Stable dividend-paying stocks with market cap weighting",
                "symbols": ["JNJ", "PG", "KO", "PEP", "WMT"],
                "weights": [0.3, 0.25, 0.2, 0.15, 0.1],  # Market cap weighted
                "strategy": "Market Cap"
            },
            {
                "name": "High Risk High Reward",
                "description": "Volatile growth stocks for aggressive investors",
                "symbols": ["TSLA", "NVDA", "AMD", "NFLX", "AMZN"],
                "weights": [0.3, 0.25, 0.2, 0.15, 0.1],  # Custom allocation
                "strategy": "Custom"
            },
            {
                "name": "Balanced Growth Portfolio",
                "description": "Mix of growth and value stocks for moderate risk",
                "symbols": ["AAPL", "JNJ", "GOOGL", "PG", "MSFT"],
                "weights": [0.25, 0.2, 0.2, 0.2, 0.15],  # Balanced allocation
                "strategy": "Risk Parity"
            },
            {
                "name": "ESG Focused Portfolio",
                "description": "Environmentally and socially responsible investments",
                "symbols": ["TSLA", "NVDA", "MSFT", "GOOGL", "AAPL"],
                "weights": [0.25, 0.2, 0.2, 0.2, 0.15],  # ESG weighted
                "strategy": "Custom"
            },
            {
                "name": "Dividend Aristocrats",
                "description": "Companies with consistent dividend growth over 25+ years",
                "symbols": ["JNJ", "PG", "KO", "PEP", "WMT", "MCD"],
                "weights": [0.2, 0.2, 0.15, 0.15, 0.15, 0.15],  # Equal weight
                "strategy": "Equal Weight"
            },
            {
                "name": "Sector Rotation Portfolio",
                "description": "Diversified across major sectors with dynamic allocation",
                "symbols": ["AAPL", "JPM", "JNJ", "XOM", "GOOGL", "PG"],
                "weights": [0.2, 0.15, 0.15, 0.15, 0.2, 0.15],  # Sector balanced
                "strategy": "Market Cap"
            },
            {
                "name": "Momentum Strategy Portfolio",
                "description": "Stocks with strong recent performance and momentum",
                "symbols": ["NVDA", "TSLA", "META", "AMZN", "NFLX"],
                "weights": [0.3, 0.25, 0.2, 0.15, 0.1],  # Momentum weighted
                "strategy": "Custom"
            }
        ]
        
        created_count = 0
        for portfolio_data in sample_portfolios:
            try:
                # Check if portfolio already exists
                existing_portfolios = portfolio_service.get_all_portfolios()
                existing_names = [p["name"] for p in existing_portfolios]
                
                if portfolio_data["name"] not in existing_names:
                    result = portfolio_service.create_portfolio(
                        name=portfolio_data["name"],
                        description=portfolio_data["description"],
                        symbols=portfolio_data["symbols"],
                        weights=portfolio_data["weights"],
                        strategy=portfolio_data["strategy"]
                    )
                    logger.info(f"Created portfolio: {portfolio_data['name']} with ID {result.get('id', 'unknown')}")
                    created_count += 1
                else:
                    logger.info(f"Portfolio '{portfolio_data['name']}' already exists, skipping...")
                    
            except Exception as e:
                logger.error(f"Error creating portfolio '{portfolio_data['name']}': {e}")
        
        logger.info(f"Successfully created {created_count} new sample portfolios")
        
        # Display all portfolios
        all_portfolios = portfolio_service.get_all_portfolios()
        logger.info(f"Total portfolios in database: {len(all_portfolios)}")
        
        print("\n" + "="*80)
        print("SAMPLE PORTFOLIOS CREATED SUCCESSFULLY")
        print("="*80)
        for portfolio in all_portfolios:
            print(f"ID: {portfolio['id']}")
            print(f"Name: {portfolio['name']}")
            print(f"Strategy: {portfolio['strategy']}")
            print(f"Assets: {', '.join(portfolio['symbols'])}")
            print(f"Created: {portfolio['created_at']}")
            print("-" * 40)
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample portfolios: {e}")
        return False

if __name__ == "__main__":
    print("Creating sample portfolios in the database...")
    success = create_sample_portfolios()
    
    if success:
        print("\n✅ Sample portfolios created successfully!")
        print("You can now view them in the Portfolio Management tab.")
    else:
        print("\n❌ Failed to create sample portfolios.")
        sys.exit(1)
