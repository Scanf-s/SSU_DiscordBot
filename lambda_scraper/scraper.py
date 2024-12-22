import time
from typing import Any, Dict, List
import boto3
import logging

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime

from lambda_database import DynamoDBConnector

logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def fetch_user_list(table) -> List[str]:
    try:
        logger.info("Fetch user list from DynamoDB")
        response = table.scan(
            FilterExpression="begins_with(#pk, :prefix) AND #sk = :profile",
            ExpressionAttributeNames={
                "#pk": "PK",
                "#sk": "SK"
            },
            ExpressionAttributeValues={
                ":prefix": "USER#",
                ":profile": "PROFILE"
            }
        )
        if "Items" not in response:
            logger.info("There are no users in DynamoDB")
            return []

        users = [item["boj_name"] for item in response["Items"]]
        logger.info(f"Found {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return []


async def fetch_user_data(session, username: str, base_url: str) -> List[Dict[str, Any]]:
    request_url: str = base_url + f"/status?user_id={username}"
    data: List = []

    try:
        logger.info("Fetching acmicpc data")
        async with session.get(
                url=request_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                }) as resp:

            if resp.status != 200:
                print(f"request error {resp.status}")
                return []

            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", id="status-table")

            if not table:  # 테이블이 없는 경우 처리
                logger.info(f"사용자 {username}의 데이터를 찾을 수 없습니다.")
                return data

            for row in table.find_all("tr"):
                submitted_result = row.find('span', attrs={'class': 'result-text result-ac'})
                if submitted_result is not None:
                    submitted_time = row.find('a', class_='real-time-update')['title']
                    submitted_datetime = datetime.strptime(submitted_time, "%Y-%m-%d %H:%M:%S")
                    submitted_timestamp = submitted_datetime.timestamp()
                    if submitted_time is not None and time.time() - submitted_timestamp < 60 * 60 * 24:
                        logger.info(f"사용자: {username}")
                        logger.info(f"제출 번호 : {row.find('td').text}")
                        logger.info(f"문제 번호 : {row.find('a', class_='problem_title').text}")
                        logger.info(f"문제 링크 : {base_url + row.find('a', attrs={'class': 'problem_title'}).get('href')}")
                        logger.info(f"제출 시간: {submitted_time}")
                        logger.info(f"메모리 : {row.find('td', class_='memory').text}KB")
                        logger.info(f"시간 : {row.find('td', class_='time').text}ms")

                        scrap_data = {
                            "PK": f"USER#{username}",  # 파티션 키
                            "SK": f"SUBMIT#{row.find('td').text}",  # 정렬 키
                            "username": username,
                            "submission_id": row.find('td').text,
                            "problem_id": row.find('a', class_='problem_title').text,
                            "problem_url": base_url + row.find('a', attrs={'class': 'problem_title'}).get('href'),
                            "submitted_time": submitted_time,
                            "memory": row.find('td', class_='memory').text,
                            "time": row.find('td', class_='time').text
                        }
                        data.append(scrap_data)

        return data

    except Exception as e:
        logger.error(f"Exception : {str(e)}")


async def save_db(db: boto3.resource, submissions: List[Dict[str, Any]]) -> None:
    if db.service_name == 'dynamodb':
        table = db.algorithm_table
        with table.batch_writer() as writer:
            for submission in submissions:
                writer.put_item(Item=submission)

    print(f"Saved {len(submissions)} submissions to DynamoDB")


async def scrap_data():
    try:
        database = DynamoDBConnector()
        users = await fetch_user_list(table=database.user_table)
        logger.info(f"Fetched users : {users}")
        base_url = "https://www.acmicpc.net"
        submissions = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for user in users:
                task = asyncio.create_task(fetch_user_data(session, user, base_url))
                tasks.append(task)

            # 모든 태스크 동시 실행
            result = await asyncio.gather(*tasks)
            for data in result:
                submissions.extend(data)

        # DB에 저장
        await save_db(db=database, submissions=submissions)
        return submissions
    except Exception as e:
        print(f"An error occurred: {str(e)}")

