from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands
from discord import Embed
import aiohttp


class Information(commands.Cog, name="info"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="info",
        description="Solved.ac 에서 사용자 정보를 획득하는 명령어",
    )
    @app_commands.describe(username="Solved.ac의 유저 이름(handle)")
    async def info(self, context: Context, username: str = None) -> None:
        # 그냥 !info만 사용한경우, username을 명령 호출자로 설정
        if username is None:
            nickname = context.author.nick
            self.bot.logger.debug(f"Current nickname : {nickname}")
            username = context.author.nick.split("/")[0].strip()
            self.bot.logger.debug(f"!info without username : {username}")

        async with aiohttp.ClientSession() as session:
            self.bot.logger.debug(f"Getting user info from solved.ac for {username}")
            params = {"handle": username}
            async with session.get("https://solved.ac/api/v3/user/show",
                                   params=params) as resp:
                self.bot.logger.info(f"Response status in solved.ac : {resp.status}")
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

                embed = Embed(
                    title="Solved.ac 사용자 정보",
                    description=f"{data.get("handle")}님의 Solved.ac 정보",
                    color=0x1ABC9C
                )
                embed.set_thumbnail(url=data.get("profileImageUrl"))
                embed.add_field(name="Class", value=data.get("class"), inline=True)
                embed.add_field(name="Tier", value=data.get("tier"), inline=True)
                embed.set_image(url=f"https://static.solved.ac/tier_small/{data.get("tier")}.svg")
                embed.add_field(name="Rating", value=data.get("rating"), inline=True)

                embed.set_footer(text="Solved.ac")

                await context.send(embed=embed)


# Setup cog
async def setup(bot) -> None:
    await bot.add_cog(Information(bot))
