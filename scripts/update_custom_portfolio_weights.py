#!/usr/bin/env python3
"""
Script to update custom portfolio weights with more realistic allocations.
"""

import sys
import os
import json

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Change to project root directory
os.chdir(project_root)

from src.data_access.portfolio_management_service import PortfolioManagementService

def update_custom_portfolio_weights():
    """Update custom portfolios with realistic weight distributions."""
    service = PortfolioManagementService()
    
    # Define realistic custom portfolio allocations
    custom_portfolio_updates = {
        "High Risk High Reward": {
            "weights": [0.4, 0.3, 0.2, 0.1],  # TSLA: 40%, NVDA: 30%, AMD: 20%, NFLX: 10%
            "description": "An aggressive portfolio targeting highly volatile stocks for maximum returns."
        },
        "ESG Focused Portfolio": {
            "weights": [0.35, 0.25, 0.2, 0.15, 0.05],  # TSLA: 35%, NVDA: 25%, MSFT: 20%, GOOGL: 15%, AAPL: 5%
            "description": "Investments in companies with strong Environmental, Social, and Governance practices."
        },
        "Momentum Strategy Portfolio": {
            "weights": [0.3, 0.25, 0.2, 0.15, 0.1],  # NVDA: 30%, TSLA: 25%, META: 20%, AMZN: 15%, NFLX: 10%
            "description": "Invests in stocks showing strong upward price trends."
        },
        "Momentum Strat edit": {
            "weights": [0.5, 0.3, 0.2],  # AAPL: 50%, GOOGL: 30%, MSFT: 20%
            "description": "Updated Momentum Strat edit portfolio with realistic allocations."
        },
        "customport": {
            "weights": [0.4, 0.35, 0.25],  # AAPL: 40%, GOOGL: 35%, MSFT: 25%
            "description": "Custom portfolio with diversified tech allocations."
        }
    }
    
    print("Updating custom portfolio weights with realistic allocations...\n")
    
    try:
        # Get all portfolios from database
        all_portfolios = service.get_all_portfolios()
        
        updated_count = 0
        for portfolio in all_portfolios:
            portfolio_name = portfolio["name"]
            
            # Check if this is a custom portfolio that needs updating
            if portfolio_name in custom_portfolio_updates and portfolio["strategy"] == "Custom":
                update_data = custom_portfolio_updates[portfolio_name]
                
                # Update the portfolio with new weights and description
                success = service.update_portfolio(
                    portfolio_id=portfolio["id"],
                    weights=update_data["weights"],
                    description=update_data["description"]
                )
                
                if success:
                    print(f"✅ Updated '{portfolio_name}' with weights: {update_data['weights']}")
                    print(f"   Description: {update_data['description']}")
                    
                    # Calculate and display the dollar amounts for $100,000 portfolio
                    total_value = 100000
                    print(f"   Dollar allocations for ${total_value:,} portfolio:")
                    for i, symbol in enumerate(portfolio["symbols"]):
                        if i < len(update_data["weights"]):
                            amount = int(total_value * update_data["weights"][i])
                            print(f"     {symbol}: ${amount:,} ({update_data['weights'][i]:.1%})")
                    print()
                    updated_count += 1
                else:
                    print(f"❌ Failed to update '{portfolio_name}'")
            elif portfolio["strategy"] == "Custom":
                print(f"ℹ️  Custom portfolio '{portfolio_name}' not in update list - keeping existing weights")
        
        print("=" * 80)
        print("CUSTOM PORTFOLIO WEIGHT UPDATES COMPLETED")
        print("=" * 80)
        print(f"✅ Successfully updated {updated_count} custom portfolios")
        
        # Verify the updates
        print("\nVerifying updated portfolios:")
        updated_portfolios = service.get_all_portfolios()
        for portfolio in updated_portfolios:
            if portfolio["strategy"] == "Custom":
                print(f"\n📊 {portfolio['name']}:")
                print(f"   Strategy: {portfolio['strategy']}")
                print(f"   Assets: {', '.join(portfolio['symbols'])}")
                print(f"   Weights: {portfolio['weights']}")
                print(f"   Description: {portfolio.get('description', 'N/A')}")
                
                # Show dollar amounts
                total_value = 100000
                print(f"   Dollar allocations for ${total_value:,}:")
                for i, symbol in enumerate(portfolio["symbols"]):
                    if i < len(portfolio["weights"]):
                        amount = int(total_value * portfolio["weights"][i])
                        print(f"     {symbol}: ${amount:,} ({portfolio['weights'][i]:.1%})")
        
    except Exception as e:
        print(f"❌ Error updating custom portfolio weights: {e}")
        return False
    
    return True

if __name__ == "__main__":
    update_custom_portfolio_weights()
