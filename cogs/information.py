from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
from response.bot_response_object import BotResponseObject
import aiohttp


class Information(commands.Cog, name="info"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="info",
        description="Solved.ac 에서 사용자 정보를 획득하는 명령어",
    )
    @app_commands.describe(username="Solved.ac의 유저 이름(handle)")
    async def solved(self, context: Context, username: str = None) -> None:
        """
        !solved_ac [username]
        :param context:
        :return:
        """
        # 만약 명령어 사용 시 username이 없는 경우, 안내 메세지를 보낸다.
        if not username:
            self.bot.logger.warning(f"Invalid command used! {context.author.nick}")
            await context.send("Solved.ac 이름을 입력해주세요. 예시) !info 이름")
            return

        async with aiohttp.ClientSession() as session:
            self.bot.logger.debug(f"Getting user info from solved.ac for {username}")
            params = {"handle": username}
            async with session.get("https://solved.ac/api/v3/user/show",
                                   params=params) as resp:
                if resp.status == 404:
                    self.bot.logger.warning(f"Failed to get user info from solved.ac for {username}")
                    await context.send("해당 사용자를 찾을 수 없어요. 닉네임을 다시 확인해주세요.")
                    return
                if resp.status != 200:
                    self.bot.logger.warning(f"Failed to get user info from solved.ac for {username}")
                    await context.send(f"사용자 정보를 가져오는데 오류가 발생했어요. 나중에 다시 시도해주세요.")
                    return

                data = await resp.json()
                self.bot.logger.info(f"Got user info from solved.ac for {username}")
                await context.send(embed=BotResponseObject(data).embed())


# Setup cog
async def setup(bot) -> None:
    await bot.add_cog(Information(bot))
