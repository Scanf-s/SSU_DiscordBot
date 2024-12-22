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
        if not context.author.nick:
            await context.send("서버 닉네임이 설정되어 있지 않습니다. (백준닉네임 / 실명)")
            return

        user = context.author.nick
        boj_name = user.split("/")[0].strip()
        try:
            response = self.bot.database.user_table.get_item(
                Key={
                    "PK": "USER#" + boj_name,
                    "SK": "PROFILE",
                }
            )
            if "Item" in response:
                await context.send(f"이미 등록된 사용자 입니다!")
                return

            self.bot.database.user_table.put_item(
                Item={
                    "PK": "USER#" + boj_name,
                    "SK": "PROFILE",
                    "discord_id": context.author.id,
                    "boj_name": user.split("/")[0].strip(),
                }
            )
            self.bot.logger.info(f"Registered : {context.author.nick}")
            await context.send(f"성공적으로 등록되었습니다. 환영합니다 {context.author.nick}!")
        except Exception as e:
            self.bot.logger.error(f"Registration error occurs : {str(e)}")
            await context.send("사용자 등록 중 오류가 발생했습니다. 관리자에게 문의해주세요.")

    @commands.hybrid_command(
        name="unregister",
        description="SAS봇에서 등록 해제하는 명령어",
    )
    async def unregister(self, context: Context) -> None:
        if not context.author.nick:
            await context.send("서버 닉네임이 설정되어 있지 않습니다. (백준닉네임 / 실명)")
            return

        try:
            user = context.author.nick
            boj_name = user.split("/")[0].strip()

            response = self.bot.database.user_table.get_item(
                Key={
                    "PK": "USER#" + boj_name,
                    "SK": "PROFILE",
                }
            )
            if "Item" not in response:
                await context.send(f"등록되지 않은 사용자 입니다!")
                return

            self.bot.database.user_table.delete_item(
                Key={
                    "PK": "USER#" + boj_name,
                    "SK": "PROFILE",
                }
            )
            self.bot.logger.info(f"Unregistered : {context.author.nick}")
            await context.send(f"성공적으로 등록 해제되었습니다: {context.author.nick}")

        except Exception as e:
            self.bot.logger.error(f"Unregister error: {str(e)}")
            await context.send("등록 해제 중 오류가 발생했습니다. 다시 시도해주세요.")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Register(bot))
