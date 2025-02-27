from typing import List, Callable
from discord import ButtonStyle, Interaction
from discord.ui import View, Button, button
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
from discord import Embed


class PaginatedEmbedView(View):
    def __init__(self, embeds: List[Embed], context: Context):
        super().__init__(timeout=180)  # 3분 제한
        self.embeds: List[Embed] = embeds  # embed 리스트
        self.context: Context = context
        self.current_page: int = 0
        self.total_pages: int = len(embeds)
        self.message = None

    async def start_message(self):
        self.message = await self.context.send(embed=self.embeds[0], view=self)

    @button(label="◀", style=ButtonStyle.secondary)
    async def previous_button(self, interaction: Interaction, _button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page],
                view=self
            )

    @button(label="▶", style=ButtonStyle.secondary)
    async def next_button(self, interaction: Interaction, _button: Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page],
                view=self
            )

    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)


class Today(commands.Cog, name="today"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def get_time(self) -> List[str]:
        self.bot.logger.info("Calculate time range")
        now = datetime.now()
        if 0 <= now.hour < 6:  # 새벽 0시에서 6시 사이에 호출하는 경우, 전날 새벽 6시 ~ 오늘 새벽 5시 59분 59초 범위를 탐색
            start_time = (now - timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=5, minute=59, second=59, microsecond=999999)
        else:
            start_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
            end_time = (start_time + timedelta(days=1)).replace(hour=5, minute=59, second=59, microsecond=999999)

        # submitted_time 형식 확인!
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

        return [start_time, end_time]

    @commands.hybrid_command(
        name="today",
        description="오늘 문제를 풀었는지 안풀었는지 확인하는 명령어",
    )
    async def today(self, context: Context, boj_name: str = None) -> None:
        if not boj_name:
            boj_name = context.author.nick.split("/")[0].strip()

        """
        오늘에 해당하는 범위 : x월 x일 오전 06시 00분 ~ x월 x + 1일 오전 06시 00분 
        """
        start_time, end_time = await self.get_time()

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
        self.bot.logger.info(data)
        solved_count = len(data)
        solved_data = [item["problem_id"] for item in data]
        solved_data.sort()

        embed = Embed(
            title=f"{boj_name}님이 오늘 푼 문제",
            color=0x00ff00
        )

        embed.add_field(
            name="푼 문제 수",
            value=f"**{solved_count}**개",
            inline=False
        )

        problem_list = ', '.join(map(str, solved_data))
        if len(problem_list) > 1024:  # Discord 메세지 길이 제한
            problem_list = problem_list[:1021] + "..."

        embed.add_field(
            name="푼 문제 목록",
            value=problem_list if solved_data else "아직 푼 문제가 없습니다.",
            inline=False
        )

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="todayall",
        description="오늘 문제를 푼 사람들에 대해서만 문제풀이 정보를 가져옵니다.",
    )
    @commands.has_permissions(administrator=True)
    async def todayall(self, context: Context) -> None:
        response = self.bot.database.user_table.scan(
            FilterExpression="begins_with(PK, :prefix) AND SK = :profile",
            ExpressionAttributeValues={
                ":prefix": "USER#",
                ":profile": "PROFILE"
            }
        )

        if "Items" not in response:
            embed = Embed(
                title="오류!",
                description="등록된 사용자가 한 명도 없습니다.",
                color=0xff0000
            )
            await context.send(embed=embed)
            return

        user_list = response.get("Items")
        embed_list = []
        start_time, end_time = await self.get_time()

        for index, user in enumerate(user_list):
            boj_name = user.get("boj_name")
            if not boj_name:
                continue

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

            data = response.get("Items", [])
            solved_count = len(data)
            solved_data = sorted([item["problem_id"] for item in data])

            embed = Embed(
                title=f"{boj_name}님이 오늘 푼 문제",
                description=f"기준: {start_time[:10]} 06:00 ~ {end_time[:10]} 06:00",
                color=0x00ff00 if solved_count > 0 else 0xff9900
            )

            embed.add_field(
                name="푼 문제 수",
                value=f"**{solved_count}**개",
                inline=False
            )

            problem_list = ', '.join(map(str, solved_data))
            if len(problem_list) > 1024:
                problem_list = problem_list[:1021] + "..."

            embed.add_field(
                name="푼 문제 목록",
                value=problem_list if solved_data else "아직 푼 문제가 없습니다.",
                inline=False
            )

            embed.set_footer(text=f"{index + 1} / {len(user_list)}")
            embed_list.append(embed)

        if not embed_list:
            await context.send("데이터를 가져오는 중 오류가 발생했습니다. 관리자에게 문의해주세요")
            return

        view = PaginatedEmbedView(embed_list, context)
        await context.send(embed=embed_list[0], view=view)


async def setup(bot) -> None:
    await bot.add_cog(Today(bot))
