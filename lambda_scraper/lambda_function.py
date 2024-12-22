import asyncio
from scraper import scrap_data
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # 람다 핸들러
    try:
        logger.info("Start lambda function")
        results = asyncio.run(scrap_data())

        if results is None:
            results = []

        logger.info(f"Scrap completed with results : {results}")
        return {
            'statusCode': 200,
            'body': f'Successfully processed {len(results)} submissions'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error occured: {str(e)}'
        }

