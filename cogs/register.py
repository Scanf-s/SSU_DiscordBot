from discord.ext import commands
from discord.ext.commands import Context


class Register(commands.Cog, name="register"):
    """
    디스코드 채널의 사용자를 등록하는 명령어
    반드시 디스코드 채널 닉네임이 "백준닉네임 / 실명" 이어야 함
    """
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="register",
        description="SAS봇에 당신을 등록해주세요",
    )
    async def register(self, context: Context) -> None:
        self.bot.logger.info(f"Registered '{context.author.nick}'")

        # 여기에 DynamoDB 연결 구현
        # DynamoDB 연결, 등록

        await context.send(f"Hello {context.author.nick}")

    @commands.hybrid_command(
        name="unregister",
        description="SAS봇에서 등록 해제하는 명령어",
    )
    async def unregister(self, context: Context) -> None:
        self.bot.logger.info(f"Unregistered '{context.author.nick}'")

        # 여기에 DynamoDB 연결 구현
        # DynamoDB 연결, DB에있는 본인 데이터 삭제
        # bot.py의 DiscordBot에서 dynamodb 인스턴스 초기화 했으니까
        # self.bot.database로 사용

        await context.send(f"Goodbye {context.author.nick}")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Register(bot))
