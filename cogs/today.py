from tokenize import endpats

from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta


class Today(commands.Cog, name="today"):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.hybrid_command(
        name="today",
        description="오늘 문제를 풀었는지 안풀었는지 확인하는 명령어",
    )
    async def today(self, context: Context) -> None:
        user = context.author.nick
        boj_name = user.split("/")[0].strip()
        now = datetime.now()
        today_6am = now.replace(hour=6, minute=0, second=0, microsecond=0)

        if now.hour < 6:
            # 만약 오늘이 x월 x일이고
            # 현재 시각이 오전 6시 이전이라면
            # "오늘"에 해당하는 범위는 x월 x-1일 오전 06시 ~ x월 x일 오전 06시
            start_time = (today_6am - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # 만약 오늘이 x월 x일이고
            # 현재 시각이 오전 6시 이후라면
            # "오늘"에 해당하는 범위는 x월 x일 현재시각 ~ x월 x+1일 오전 06시
            start_time = today_6am.strftime("%Y-%m-%d %H:%M:%S")
            end_time = (today_6am + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

        response = self.bot.database.user_table.get_item(
            Key={
                "PK": "USER#" + boj_name,
                "SK": "PROFILE",
            }
        )
        if "Item" not in response:
            await context.send(f"등록되지 않은 사용자 입니다!")
            return

        response = self.bot.database.algorithm_table.query(
            KeyConditionExpression="#pk = :pk AND begins_with(#sk, :sk)",
            FilterExpression="submitted_time BETWEEN :start_time AND :end_time",
            ExpressionAttributeNames={
                "#pk": "PK",
                "#sk": "SK"
            },
            ExpressionAttributeValues={
                ":pk": f"USER#{boj_name}",
                ":sk": "SUBMIT#",
                ":start_time": start_time,
                ":end_time": end_time
            }
        )
        data = response.get("Items")
        solved_count = len(data)
        if solved_count == 0:
            await context.send(f"오늘 아직 문제를 하나도 풀지 않았습니다!")
            return

        solved_data = [item["problem_id"] for item in data]
        solved_data.sort()
        message = (
            f"오늘의 문제 풀이 현황\n"
            f"푼 문제 수: {solved_count}개\n"
            f"문제 목록: {', '.join(map(str, solved_data))}"
        )
        await context.send(message)


async def setup(bot) -> None:
    await bot.add_cog(Today(bot))
