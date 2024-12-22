import re
import time
import requests
import boto3
from bs4 import BeautifulSoup
from datetime import datetime

if __name__ == "__main__":
    # 여기에 스크래핑 구현
    username: str = "sullung2yo"
    base_url: str = "https://www.acmicpc.net"
    request_url : str = base_url + f"/status?user_id={username}"
    response = requests.get(
        request_url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    )
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="status-table")
    for row in table.find_all("tr"):
        submitted_result = row.find('span', attrs={'class': 'result-text result-ac'})  # 맞았습니다!! 항목만 가져오기
        if submitted_result is not None:
            print(f"제출번호 : {row.find("td").text}")
            print(f"문제번호 : {row.find("a", attrs={'class': 'problem_title'}).text}")
            print(f"문제링크 : {base_url + row.find('a', attrs={'class': 'problem_title'}).get('href')}")
            print(f"제출 시간 : {row.find('a', attrs={'class': 'real-time-update'}).text}")
            print()

