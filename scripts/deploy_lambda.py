"""
Deploy Lambda function for automated pipeline execution.
"""
import boto3
import zipfile
import os
import logging
from pathlib import Path
from config.config import AWS_CONFIG

logger = logging.getLogger(__name__)


class LambdaDeployer:
    """Deployer for AWS Lambda function."""
    
    def __init__(self):
        """Initialize Lambda deployer."""
        self.lambda_client = boto3.client(
            'lambda',
            aws_access_key_id=AWS_CONFIG['access_key_id'],
            aws_secret_access_key=AWS_CONFIG['secret_access_key'],
            region_name=AWS_CONFIG['region']
        )
        self.iam_client = boto3.client(
            'iam',
            aws_access_key_id=AWS_CONFIG['access_key_id'],
            aws_secret_access_key=AWS_CONFIG['secret_access_key'],
            region_name=AWS_CONFIG['region']
        )
    
    def create_iam_role(self, role_name: str):
        """
        Create IAM role for Lambda function.
        
        Args:
            role_name: IAM role name
            
        Returns:
            Role ARN
        """
        try:
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for Quant Finance Pipeline Lambda function'
            )
            
            # Attach basic execution policy
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Attach additional policies for S3, RDS, etc.
            additional_policies = [
                'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                'arn:aws:iam::aws:policy/AmazonRDSFullAccess',
                'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess'
            ]
            
            for policy_arn in additional_policies:
                try:
                    self.iam_client.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                except Exception as e:
                    logger.warning(f"Could not attach policy {policy_arn}: {str(e)}")
            
            logger.info(f"Created IAM role: {role_name}")
            return response['Role']['Arn']
            
        except Exception as e:
            logger.error(f"Error creating IAM role: {str(e)}")
            return None
    
    def create_deployment_package(self, source_dir: str, output_file: str):
        """
        Create deployment package for Lambda function.
        
        Args:
            source_dir: Source directory
            output_file: Output ZIP file path
        """
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Created deployment package: {output_file}")
            
        except Exception as e:
            logger.error(f"Error creating deployment package: {str(e)}")
            raise
    
    def deploy_function(
        self, 
        function_name: str, 
        deployment_package: str, 
        role_arn: str,
        handler: str = 'lambda_function.lambda_handler'
    ):
        """
        Deploy Lambda function.
        
        Args:
            function_name: Function name
            deployment_package: Path to deployment package
            role_arn: IAM role ARN
            handler: Function handler
        """
        try:
            # Read deployment package
            with open(deployment_package, 'rb') as f:
                zip_content = f.read()
            
            # Check if function exists
            try:
                self.lambda_client.get_function(FunctionName=function_name)
                # Function exists, update it
                response = self.lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=zip_content
                )
                logger.info(f"Updated Lambda function: {function_name}")
                
            except self.lambda_client.exceptions.ResourceNotFoundException:
                # Function doesn't exist, create it
                response = self.lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python3.11',
                    Role=role_arn,
                    Handler=handler,
                    Code={'ZipFile': zip_content},
                    Description='Quantitative Finance Pipeline Lambda function',
                    Timeout=900,  # 15 minutes
                    MemorySize=1024,
                    Environment={
                        'Variables': {
                            'DATABASE_URL': os.getenv('DATABASE_URL', ''),
                            'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
                            'QUANDL_API_KEY': os.getenv('QUANDL_API_KEY', ''),
                            'FRED_API_KEY': os.getenv('FRED_API_KEY', ''),
                            'AWS_ACCESS_KEY_ID': AWS_CONFIG['access_key_id'],
                            'AWS_SECRET_ACCESS_KEY': AWS_CONFIG['secret_access_key']
                        }
                    }
                )
                logger.info(f"Created Lambda function: {function_name}")
            
            return response['FunctionArn']
            
        except Exception as e:
            logger.error(f"Error deploying Lambda function: {str(e)}")
            return None
    
    def deploy(self, function_name: str = 'quant-finance-pipeline'):
        """
        Deploy the complete Lambda function.
        
        Args:
            function_name: Lambda function name
        """
        try:
            # Create IAM role
            role_name = f'{function_name}-role'
            role_arn = self.create_iam_role(role_name)
            
            if not role_arn:
                raise Exception("Failed to create IAM role")
            
            # Wait for role to be available
            import time
            time.sleep(10)
            
            # Create deployment package
            deployment_package = 'lambda_deployment.zip'
            self.create_deployment_package('.', deployment_package)
            
            # Deploy function
            function_arn = self.deploy_function(function_name, deployment_package, role_arn)
            
            if function_arn:
                logger.info(f"Successfully deployed Lambda function: {function_arn}")
                return function_arn
            else:
                raise Exception("Failed to deploy Lambda function")
                
        except Exception as e:
            logger.error(f"Error in deployment: {str(e)}")
            raise
        finally:
            # Clean up deployment package
            if os.path.exists('lambda_deployment.zip'):
                os.remove('lambda_deployment.zip')


def main():
    """Main function to deploy Lambda function."""
    deployer = LambdaDeployer()
    function_arn = deployer.deploy()
    
    if function_arn:
        print(f"Lambda function deployed successfully: {function_arn}")
    else:
        print("Failed to deploy Lambda function")


if __name__ == "__main__":
    main()
