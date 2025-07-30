import discord
from discord import app_commands

cmdDescription = [
        "**/spark (Person) (Kompliment)**\n   Damit kannst du einer Person ein Anonymes kompliment machen.\n",
        "**/stats (Person)**\n                Zeige alle Komplimente an, die diese Person bisher bekommen hat\n",
        "**/topserver**\n                     Zeigt die 2 meistgenutzten Server an\n",
        "**/hug (Person)**\n                  Umarme diese Person Anonym\n",
        "**/pat (Person)**\n                  gib der Person ein Anonymes pat\n",
        "**/cooldown**\n                      Schaue nach, wann du wieder /spark verwenden kannst\n",
        "**/feedback**\n                      Öffnet ein Formular in dem du Feedback für den Bot eingeben kannst\n",
        "**/settings**\n                      Stell einige Dinge ein, zb. ob du private Nachrichten möchtest\n",
        "**/streak**\n                        Schaue dir alle relevanten Dinge zu deiner Streak an\n"
    ]

async def helpSpark(interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    embed.add_field(
        name="Hilfe zu /spark: ",
        value="""\n\n Du kannst täglich **einer** Person ein Anonymes Kompliment geben. \n\n
                    **Mit Premium** kannst du täglich **2 sparks** verwenden und hast zusätzlich die möglichkeit diese sparks **custom** zu gestalten. 
                    \n\n **/spark (Person) (Kompliment)**\n   Damit kannst du einer Person ein Anonymes kompliment machen. \n
                    Um einen **Custom Spark** zu senden, einfach beim Feld "Kompliment" deine Nachricht reinsenden.\n
                    Wenn du möchtest, dass man in Zukunft **nachschauen** kann **wer** den **Spark versendet** hat, kannst du noch **reveal True** angeben. 
                    Wenn es **Anonym** bleiben soll, kannst du das **Feld einfach weglassen** oder False angeben.\n""",
        inline=False
    )
    await interaction.response.send_message(embed=embed)


async def helpStreak(interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    embed.add_field(
        name="Hilfe zu /streak: ",
        value="""Hier siehst du alle relevanten Infos zu deiner Streak. \n
                    Jedes mal wenn deine Streak durch 3 teilbar ist, gibt es einen Streakpunkt.
                    Mit Streakpunkten kannst du dir in Zukunft im Shop unterschiedliche Dinge kaufen, wie zb. Premium
                    """,
        inline=False
    )
    await interaction.response.send_message(embed=embed)

async def helpSettings(interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    embed.add_field(
        name="Hilfe zu /settings: ",
        value="""Hier kannst du deine Einstellungen anpassen. \n
                    Je nachddem ob du Premium hast oder nicht, werden dir andere Buttons angezeigt. 
                    Um zu wissen was eingestellt war, musst du einmal auf den Button drücken. 
                    Ich arbeite aktuell noch an einer besseren Lösung.
                    """,
        inline=False
    )
    await interaction.response.send_message(embed=embed)

async def helpHug(interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    embed.add_field(
        name="Hilfe zu /hug: ",
        value="""Du kannst täglich einer Person **einen Hug oder Pat** geben. \n
                    **Mit Premium** sind Hug/Pats **3x täglich** verwendbar.
                    """,
        inline=False
    )
    await interaction.response.send_message(embed=embed)

async def helpPat(interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    embed.add_field(
        name="Hilfe zu /pat: ",
        value="""Du kannst täglich einer Person **einen Hug oder Pat** geben. \n
                    **Mit Premium** sind Hug/Pats **3x täglich** verwendbar.
                    """,
        inline=False
    )
    await interaction.response.send_message(embed=embed)

async def helpStats(interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    embed.add_field(
        name="Hilfe zu /stats: ",
        value="""Um deine **eigenen Stats** anzusehen, kannst du **/stats** eingeben. \n
                    Der Befehl zeigt dir alle Komplimente (auch Custom Nachrichten) an und wie oft du diese bekommen hast.
                    \n\n **Mit Premium** kannst du mit dem Befehl **/spark_ausblenden** custom Nachrichten ausblenden wenn du die SparkID angibst.
                    Die SparkID findest du bei deinen Stats neben der custom Nachricht in Klammern. """,
        inline=False
    )
    await interaction.response.send_message(embed=embed)


async def helpReveal(interaction):
    embed = discord.Embed(
        color=0x005b96
    )

    embed.add_field(
        name="Hilfe zu /reveal: ",
        value="""   Wenn jemand einen Spark macht, kann optional am ende noch reveal als True angegeben werden. \n
                    Wenn das der Fall ist, kannst du für 2€ dir anschauen, von wem der Spark kommt. Du musst dabei die SparkID angeben.
                    Diese Funktion ist aktuell noch in Arbeit, reveal kann aber bereits als True angegeben werden.""",
        inline=False
    )
    await interaction.response.send_message(embed=embed)