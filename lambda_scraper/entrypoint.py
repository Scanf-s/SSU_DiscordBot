import asyncio
import logging
from scraper import Scraper
from dto.response import Response
import aioboto3
import os

MAX_SEMAPHORE = 10
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DynamoDBConnector:
    def __init__(self):
        self.service_name='dynamodb'
        self.dynamodb = aioboto3.Session().resource(
            service_name=self.service_name
        )
        self.user_table = self.dynamodb.Table(os.environ.get("USER_TABLE_NAME"))
        self.algorithm_table = self.dynamodb.Table(os.environ.get("ALGORITHM_TABLE_NAME"))

async def lambda_handler(event, context):
    # 람다 핸들러

    try:
        logger.info("Start lambda function")
        logger.info("Initialize Scraper")
        scraper = Scraper(logger=logger, database=DynamoDBConnector(), semaphore=MAX_SEMAPHORE)

        results = await scraper.scrap()

        if results is None:
            results = []

        logger.info(f"Scrap completed with results : {results}")

        return Response(
            status_code=200,
            body=f'Successfully processed {len(results)} submissions'
        ).to_dict()
    except Exception as e:
        return Response(
            status_code=500,
            body=f'Error occured: {str(e)}'
        ).to_dict()
