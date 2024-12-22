import boto3
import os

class DynamoDBConnector:
    def __init__(self, logger=None):
        self.logger = logger
        self.service_name='dynamodb'
        self.dynamodb = boto3.resource(
            service_name=self.service_name
        )
        self.user_table = self.dynamodb.Table(os.environ.get("USER_TABLE_NAME"))
        self.algorithm_table = self.dynamodb.Table(os.environ.get("ALGORITHM_TABLE_NAME"))

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