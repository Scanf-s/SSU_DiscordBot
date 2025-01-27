# SAS (SSU Algorithm Solver) Bot

이 프로젝트는 [Python Discord Bot Template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template)을 기반으로 개발되었습니다.

## Related repositories
- [Scraper](https://github.com/Scanf-s/BOJ_Scraper)
- [Alarm](https://github.com/Scanf-s/BOJ_Alarm)

## 프로젝트 소개
BOJ(Baekjoon Online Judge) 알고리즘 문제 풀이 현황을 디스코드를 통해 확인할 수 있는 봇입니다.

## 주요 기능
- 매시간 BOJ 제출 현황 자동 수집
- 디스코드를 통한 문제 풀이 현황 확인
- 실시간 문제풀이 성공 알람 송신
- solved.ac 정보 확인

## 아키텍쳐 - V2
![image](https://github.com/user-attachments/assets/a44a0ac7-7e2c-4b53-adaa-5004b4d051c2)

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
├── poetry.lock
├── pyproject.toml
└── response
    ├── __init__.py
    └── bot_response_object.py
```

## 개선 이력

### 2025.01.27
- 실시간 문제풀이 성공 알람 구현
- 스크래핑 로직 수정 -> 중복 데이터 제거
- 클라우드 아키텍쳐 수정 -> 스크래퍼 호출 주기 1분으로 설정

## 라이선스
이 프로젝트는 Apache License 2.0 라이선스를 따르고 있습니다.
자세한 내용은 [LICENSE.md](LICENSE.md) 파일을 참조해주세요.
