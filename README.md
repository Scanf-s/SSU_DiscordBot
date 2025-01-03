# SAS (SSU Algorithm Solver) Bot

이 프로젝트는 [Python Discord Bot Template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template)을 기반으로 개발되었습니다.

## 프로젝트 소개
BOJ(Baekjoon Online Judge) 알고리즘 문제 풀이 현황을 디스코드를 통해 확인할 수 있는 봇입니다.

## 주요 기능
- 매시간 BOJ 제출 현황 자동 수집
- 디스코드를 통한 문제 풀이 현황 확인
- solved.ac 정보 확인

## 아키텍쳐
![image](https://github.com/user-attachments/assets/cdb4648b-3f6b-4c3c-99d8-e6425fda7eb3)

## 프로젝트 구조
```tree
.
├── LICENSE.md
├── README.md
├── bot.py
├── cogs
│   ├── fun.py
│   ├── general.py
│   ├── information.py
│   ├── moderation.py
│   ├── owner.py
│   ├── register.py
│   ├── template.py
│   └── today.py
├── config.json # 직접 추가해야함
├── database
│   ├── __init__.py
│   ├── __pycache__
│   └── dynamodb.py
├── lambda_scraper
│   ├── __init__.py
│   ├── lambda_database.py
│   ├── lambda_function.py
│   ├── readme.md
│   ├── requirements.txt
│   └── scraper.py
├── poetry.lock
├── pyproject.toml
└── response
    ├── __init__.py
    └── bot_response_object.py
```

## 라이선스
이 프로젝트는 Apache License 2.0 라이선스를 따르고 있습니다.
자세한 내용은 [LICENSE.md](LICENSE.md) 파일을 참조해주세요.
