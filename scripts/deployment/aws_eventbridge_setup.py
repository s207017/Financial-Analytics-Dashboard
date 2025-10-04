"""
AWS EventBridge setup for automated pipeline execution.
"""
import boto3
import json
import logging
from datetime import datetime, timedelta
from config.config import AWS_CONFIG

logger = logging.getLogger(__name__)


class EventBridgeScheduler:
    """AWS EventBridge scheduler for pipeline automation."""
    
    def __init__(self):
        """Initialize EventBridge scheduler."""
        self.eventbridge = boto3.client(
            'events',
            aws_access_key_id=AWS_CONFIG['access_key_id'],
            aws_secret_access_key=AWS_CONFIG['secret_access_key'],
            region_name=AWS_CONFIG['region']
        )
        self.lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=AWS_CONFIG['access_key_id'],
            aws_secret_access_key=AWS_CONFIG['secret_access_key'],
            region_name=AWS_CONFIG['region']
        )
    
    def create_rule(self, name: str, schedule_expression: str, description: str):
        """
        Create an EventBridge rule.
        
        Args:
            name: Rule name
            schedule_expression: Cron or rate expression
            description: Rule description
        """
        try:
            response = self.eventbridge.put_rule(
                Name=name,
                ScheduleExpression=schedule_expression,
                Description=description,
                State='ENABLED'
            )
            logger.info(f"Created rule: {name}")
            return response['RuleArn']
        except Exception as e:
            logger.error(f"Error creating rule {name}: {str(e)}")
            return None
    
    def add_lambda_target(self, rule_name: str, lambda_arn: str, input_data: dict = None):
        """
        Add Lambda function as target for EventBridge rule.
        
        Args:
            rule_name: EventBridge rule name
            lambda_arn: Lambda function ARN
            input_data: Input data for Lambda function
        """
        try:
            target = {
                'Id': f'{rule_name}-target',
                'Arn': lambda_arn,
            }
            
            if input_data:
                target['Input'] = json.dumps(input_data)
            
            response = self.eventbridge.put_targets(
                Rule=rule_name,
                Targets=[target]
            )
            
            if response['FailedEntryCount'] == 0:
                logger.info(f"Added Lambda target to rule: {rule_name}")
                return True
            else:
                logger.error(f"Failed to add Lambda target: {response['FailedEntries']}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding Lambda target: {str(e)}")
            return False
    
    def add_permission_for_eventbridge(self, lambda_arn: str, rule_name: str):
        """
        Add permission for EventBridge to invoke Lambda function.
        
        Args:
            lambda_arn: Lambda function ARN
            rule_name: EventBridge rule name
        """
        try:
            function_name = lambda_arn.split(':')[-1]
            
            response = self.lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'allow-eventbridge-{rule_name}',
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=f'arn:aws:events:{AWS_CONFIG["region"]}:{AWS_CONFIG["account_id"]}:rule/{rule_name}'
            )
            
            logger.info(f"Added permission for EventBridge to invoke {function_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding permission: {str(e)}")
            return False
    
    def setup_daily_schedule(self, lambda_arn: str):
        """Set up daily data collection schedule."""
        # Daily data collection at 6 PM UTC (after market close)
        rule_arn = self.create_rule(
            name='quant-finance-daily-collection',
            schedule_expression='cron(0 18 * * ? *)',
            description='Daily data collection at 6 PM UTC'
        )
        
        if rule_arn:
            input_data = {
                'action': 'data_collection',
                'symbols': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
            }
            
            self.add_lambda_target('quant-finance-daily-collection', lambda_arn, input_data)
            self.add_permission_for_eventbridge(lambda_arn, 'quant-finance-daily-collection')
    
    def setup_weekly_schedule(self, lambda_arn: str):
        """Set up weekly portfolio optimization schedule."""
        # Weekly optimization on Sundays at 7 PM UTC
        rule_arn = self.create_rule(
            name='quant-finance-weekly-optimization',
            schedule_expression='cron(0 19 ? * SUN *)',
            description='Weekly portfolio optimization on Sundays at 7 PM UTC'
        )
        
        if rule_arn:
            input_data = {
                'action': 'portfolio_optimization',
                'method': 'markowitz'
            }
            
            self.add_lambda_target('quant-finance-weekly-optimization', lambda_arn, input_data)
            self.add_permission_for_eventbridge(lambda_arn, 'quant-finance-weekly-optimization')
    
    def setup_monthly_schedule(self, lambda_arn: str):
        """Set up monthly full analysis schedule."""
        # Monthly analysis on the 1st at 8 PM UTC
        rule_arn = self.create_rule(
            name='quant-finance-monthly-analysis',
            schedule_expression='cron(0 20 1 * ? *)',
            description='Monthly full analysis on the 1st at 8 PM UTC'
        )
        
        if rule_arn:
            input_data = {
                'action': 'full_analysis'
            }
            
            self.add_lambda_target('quant-finance-monthly-analysis', lambda_arn, input_data)
            self.add_permission_for_eventbridge(lambda_arn, 'quant-finance-monthly-analysis')
    
    def setup_all_schedules(self, lambda_arn: str):
        """Set up all scheduled events."""
        logger.info("Setting up EventBridge schedules...")
        
        self.setup_daily_schedule(lambda_arn)
        self.setup_weekly_schedule(lambda_arn)
        self.setup_monthly_schedule(lambda_arn)
        
        logger.info("All EventBridge schedules set up successfully")
    
    def list_rules(self):
        """List all EventBridge rules."""
        try:
            response = self.eventbridge.list_rules()
            rules = response.get('Rules', [])
            
            logger.info("EventBridge Rules:")
            for rule in rules:
                logger.info(f"  - {rule['Name']}: {rule['ScheduleExpression']}")
            
            return rules
            
        except Exception as e:
            logger.error(f"Error listing rules: {str(e)}")
            return []
    
    def delete_rule(self, rule_name: str):
        """Delete an EventBridge rule."""
        try:
            # Remove targets first
            targets = self.eventbridge.list_targets_by_rule(Rule=rule_name)
            if targets['Targets']:
                target_ids = [target['Id'] for target in targets['Targets']]
                self.eventbridge.remove_targets(Rule=rule_name, Ids=target_ids)
            
            # Delete the rule
            self.eventbridge.delete_rule(Name=rule_name)
            logger.info(f"Deleted rule: {rule_name}")
            
        except Exception as e:
            logger.error(f"Error deleting rule {rule_name}: {str(e)}")


def main():
    """Main function to set up EventBridge schedules."""
    scheduler = EventBridgeScheduler()
    
    # Replace with your actual Lambda function ARN
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:quant-finance-pipeline"
    
    # Set up all schedules
    scheduler.setup_all_schedules(lambda_arn)
    
    # List all rules
    scheduler.list_rules()


if __name__ == "__main__":
    main()
