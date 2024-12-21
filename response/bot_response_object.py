import discord

class BotResponseObject:
    def __init__(self, data: dict):
        self._user_name = data.get("handle")
        self._user_class = data.get("class")
        self._user_tier = data.get("tier")
        self._user_rating = data.get("rating")
        self._user_profile_image = data.get("profileImageUrl")

    def embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Solved.ac 사용자 정보",
            description=f"{self._user_name}님의 Solved.ac 정보",
            color=0x1ABC9C
        )
        embed.set_thumbnail(url=self._user_profile_image)
        embed.add_field(name="Class", value=self._user_class, inline=True)
        embed.add_field(name="Tier", value=self._user_tier, inline=True)
        embed.set_image(url=f"https://static.solved.ac/tier_small/{self._user_tier}.svg")
        embed.add_field(name="Rating", value=self._user_rating, inline=True)

        embed.set_footer(text="Solved.ac")
        return embed