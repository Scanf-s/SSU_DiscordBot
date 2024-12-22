import boto3
import os
from dotenv import load_dotenv

class DynamoDBConnector:
    def __init__(self, logger=None):
        load_dotenv()
        self.logger = logger
        self.service_name='dynamodb'
        self.dynamodb = boto3.resource(
            service_name=self.service_name,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        self.user_table = self.dynamodb.Table(os.getenv("USER_TABLE_NAME"))
        self.algorithm_table = self.dynamodb.Table(os.getenv("ALGORITHM_TABLE_NAME"))

    def is_connected(self) -> bool:
        try:
            self.logger.info(f"Connected table number: {len(list(self.dynamodb.tables.all()))}")
            self.logger.info(f"{self.user_table.key_schema}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to DynamoDB: {str(e)}")
            return False

    def register_user(self):
        pass