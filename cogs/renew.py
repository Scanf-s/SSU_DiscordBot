from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed
import boto3
import json

class Renew(commands.Cog, name="renew"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.lambda_client = boto3.client('lambda')

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="renew",
        description="강제로 스크래핑 작업을 요청하는 명령어 입니다.",
    )
    async def renew(self, context: Context) -> None:
        response = self.lambda_client.invoke(
            FunctionName="boj_scraper",
            InvocationType="Event",
            Payload=json.dumps({})
        )
        if response['StatusCode'] != 200:
            embed = Embed(
                title = "오류!",
                description = "스크래핑을 완료하는데 오류가 발생했습니다. 관리자에게 문의해주세요",
                color = 0xE02B2B
            )
            await context.send(embed=embed)
            return

        embed = Embed(
            title = "스크래핑 완료",
            description = "스크래핑을 완료하었습니다.",
            color = 0xBEBEFE
        )
        await context.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Renew(bot))
