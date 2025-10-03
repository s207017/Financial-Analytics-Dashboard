"""
AWS Lambda function for automated pipeline execution.
"""
import json
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append('/opt/python/src')

from main import QuantitativeFinancePipeline

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for pipeline execution.
    
    Args:
        event: Lambda event data
        context: Lambda context
    
    Returns:
        Response dictionary
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Initialize pipeline
        pipeline = QuantitativeFinancePipeline()
        
        # Get action from event
        action = event.get('action', 'data_collection')
        
        if action == 'data_collection':
            symbols = event.get('symbols', ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'])
            pipeline.collect_data(symbols=symbols, days_back=1)
            
        elif action == 'portfolio_optimization':
            method = event.get('method', 'markowitz')
            symbols = event.get('symbols', ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'])
            pipeline.optimize_portfolio(symbols=symbols, method=method)
            
        elif action == 'risk_calculation':
            symbols = event.get('symbols', ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'])
            pipeline.calculate_risk_metrics(symbols=symbols)
            
        elif action == 'full_analysis':
            pipeline.run_full_pipeline()
            
        else:
            raise ValueError(f"Unknown action: {action}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Pipeline {action} completed successfully',
                'timestamp': context.aws_request_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error in Lambda function: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': context.aws_request_id
            })
        }
