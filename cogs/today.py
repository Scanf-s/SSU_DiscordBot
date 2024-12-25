from typing import List, Callable
from discord import ButtonStyle, Interaction
from discord.ui import View, Button, button
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime, timedelta
from discord import Embed


class PaginatedEmbedView(View):
    def __init__(self, embeds: List[Embed], interaction: Interaction):
        super().__init__(timeout=180)  # 3분 제한
        self.interaction = interaction
        self.embeds: List[Embed] = embeds  # embed 리스트
        self.current_page: int = 0
        self.total_pages: int = len(embeds)

    @button(label="◀", style=ButtonStyle.secondary)
    async def previous_button(self, interaction: Interaction, _button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @button(label="▶", style=ButtonStyle.secondary)
    async def next_button(self, interaction: Interaction, _button: Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1


class Today(commands.Cog, name="today"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="today",
        description="오늘 문제를 풀었는지 안풀었는지 확인하는 명령어",
    )
    async def today(self, context: Context, boj_name: str = None) -> None:
        if not boj_name:
            boj_name = context.author.nick.split("/")[0].strip()
        now = datetime.now()
        today_6am = now.replace(hour=6, minute=0, second=0, microsecond=0)

        # 만약 오늘이 x월 x일이면
        # "오늘"에 해당하는 범위는 x월 x일 오전 06시 ~ x월 x + 1일 오전 06시
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
        solved_data = [item["problem_id"] for item in data]
        solved_data.sort()

        embed = Embed(
            title="오늘 푼 문제",
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
        description="등록된 모든 사용자의 당일 문제풀이 정보를 가져옵니다.",
    )
    @commands.has_permissions(administrator=True)
    async def todayall(self, interaction: Interaction) -> None:
        response = self.bot.database.user_table.scan()

        if "Items" not in response:
            embed = Embed(
                title="오류!",
                description="등록된 사용자가 한 명도 없습니다.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            return

        user_list = response.get("Items")
        embed_list = []
        now = datetime.now()
        today_6am = now.replace(hour=6, minute=0, second=0, microsecond=0)

        start_time = today_6am.strftime("%Y-%m-%d %H:%M:%S")
        end_time = (today_6am + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

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
            await interaction.response.send_message("데이터를 가져오는 중 오류가 발생했습니다. 관리자에게 문의해주세요")
            return

        view = PaginatedEmbedView(embed_list, interaction)
        await interaction.response.send_message(embed=embed_list[0], view=view)


async def setup(bot) -> None:
    await bot.add_cog(Today(bot))
