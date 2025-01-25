import asyncio
import time
from typing import Any, Dict, List

import aiohttp
import logging
import os

from bs4 import BeautifulSoup
from datetime import datetime

class Scraper:

    def __init__(self, logger: logging.Logger =None, database: Any = None, semaphore: int = 5):
        self.logger = logger
        self.database = database
        self.semaphore = asyncio.Semaphore(semaphore)

    async def scrap(self):
        try:
            users = await self.fetch_user_list(table=self.database.user_table)
            self.logger.info(f"Fetched users : {users}")
            base_url = os.getenv("SCRAP_TARGET_BASE_URL")
            submissions = []

            async with aiohttp.ClientSession() as session:
                tasks = []
                for user in users:
                    task = asyncio.create_task(self.fetch_user_data(session, user, base_url))
                    tasks.append(task)

                # 모든 태스크 동시 실행
                result = await asyncio.gather(*tasks)
                for data in result:
                    submissions.extend(data)

            # DB에 저장
            await self.save_db(db=self.database, submissions=submissions)
            return submissions
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")

    async def fetch_user_list(self, table) -> List[str]:
        try:
            self.logger.info("Fetch user list from DynamoDB")
            response = await table.scan(
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
                self.logger.info("There are no users in DynamoDB")
                return []

            users = [item["boj_name"] for item in response["Items"]]
            self.logger.info(f"Found {len(users)} users")
            return users
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            return []

    async def parse_html(self, html: str, username: str, base_url: str, data: List) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="status-table")

        if not table:  # 테이블이 없는 경우 처리
            self.logger.info(f"사용자 {username}의 데이터를 찾을 수 없습니다.")
            return data

        problem_id_set = set()
        for row in table.find_all("tr"):
            submitted_result = row.find('span', attrs={'class': 'result-text result-ac'})
            if submitted_result is not None:
                submitted_time = row.find('a', class_='real-time-update')['title']
                submitted_datetime = datetime.strptime(submitted_time, "%Y-%m-%d %H:%M:%S")
                submitted_timestamp = submitted_datetime.timestamp()
                if submitted_time is not None and time.time() - submitted_timestamp < 60 * 60 * 24:
                    self.logger.info(f"사용자: {username}")
                    self.logger.info(f"제출 번호 : {row.find('td').text}")
                    self.logger.info(f"문제 번호 : {row.find('a', class_='problem_title').text}")
                    self.logger.info(
                        f"문제 링크 : {base_url + row.find('a', attrs={'class': 'problem_title'}).get('href')}")
                    self.logger.info(f"제출 시간: {submitted_time}")
                    self.logger.info(f"메모리 : {row.find('td', class_='memory').text}KB")
                    self.logger.info(f"시간 : {row.find('td', class_='time').text}ms")

                    problem_id = row.find('a', class_='problem_title').text
                    if problem_id not in problem_id_set:
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
                        problem_id_set.add(problem_id)

    async def fetch_user_data(self, session, username: str, base_url: str) -> List[Dict[str, Any]]:
        request_url: str = base_url + f"/status?user_id={username}"
        request_user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        data: List = []

        try:
            self.logger.info("Fetching ACMICPC data")
            async with session.get(url=request_url, headers={"User-Agent": request_user_agent}) as resp:
                if resp.status != 200:
                    self.logger.error(f"request error {resp.status}")
                    return data

                html: str = await resp.text()
                await self.parse_html(html=html, username=username, base_url=base_url, data=data)

            return data
        except Exception as e:
            self.logger.error(f"Exception : {str(e)}")

    async def save_db(self, db, submissions: List[Dict[str, Any]]) -> None:
        if db.service_name == 'dynamodb':
            table = db.algorithm_table
            async with table.batch_writer() as writer:
                for submission in submissions:
                    await writer.put_item(Item=submission)

        self.logger.info(f"Saved {len(submissions)} submissions into DynamoDB")
