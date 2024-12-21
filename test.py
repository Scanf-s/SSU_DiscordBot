import aiohttp
import asyncio

async def solved_ac():
    async with aiohttp.ClientSession() as session:
        params = {"handle": "sullung2yo"}
        async with session.get("https://solved.ac/api/v3/user/show",
                               params=params) as resp:
            print(f"status code : {resp.status}")
            json = await resp.json()
            print("Solved ac class : " + json.get("class")) # 사용자 sovled ac 클래스
            print("Name : " + json.get("handle")) # 사용자 이름
            print("Tier : " + json.get("tier")) # 사용자 티어
            print("Rating : " + json.get("rating")) # 레이팅


asyncio.run(solved_ac())