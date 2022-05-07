from nextcord import Interaction, slash_command

from Discord.Cogs.Cog import MyCog


class CuratorsCategory(MyCog):

    @MyCog.curators_perm()
    @slash_command(
            name='Curators Category', 
            description='Категория для кураторов'
    )
    async def curators_category(self, inter: Interaction):
        pass
