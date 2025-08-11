import discord
import textwrap
from discord import app_commands

cmdDescription = textwrap.dedent(
        "**/spark (Person) (Kompliment) (reveal)**\n"
        "Damit kannst du einer Person ein Anonymes kompliment machen.\n\n"
        "**/stats (Person)**\n"
        "Zeige alle Komplimente an, die diese Person bisher bekommen hat\n\n"
        "**/topserver**\n"
        "Zeigt die 5 meistgenutzten Server an\n\n"
        "**/hug (Person)**\n"
        "Umarme diese Person Anonym\n\n"
        "**/pat (Person)**\n"
        "gib der Person ein Anonymes pat\n\n"
        "**/cooldown**\n"
        "Schaue nach, wann du wieder /spark verwenden kannst\n\n"
        "**/feedback**\n"
        "Öffnet ein Formular in dem du Feedback für den Bot eingeben kannst\n\n"
        "**/settings**\n"
        "Stell einige Dinge ein, zb. ob du private Nachrichten möchtest\n\n"
        "**/streak**\n"
        "Schaue dir alle relevanten Dinge zu deiner Streak an\n\n"
        "**/profil**\n"
        "Zeigt dir Infos über dich an\n\n"
        "**/reveal**\n"
        "Lasse dir anzeigen von wem ein Spark gesendet wurde\n\n")

async def helpSpark(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent( "\n\n Du kannst täglich **einer** Person ein anonymes Kompliment geben. \n\n"
                            "**Mit Premium** kannst du täglich **2 Sparks** verwenden und hast zusätzlich die Möglichkeit diese Sparks **custom** zu gestalten. "
                            "\n\n**/spark (Person) (Kompliment)**\nDamit kannst du einer Person ein Anonymes kompliment machen. \n"
                            "Um einen **custom Spark** zu senden, einfach beim Feld 'Kompliment' deine Nachricht reinsenden.\n"
                            "Wenn du möchtest, dass man **nachschauen** kann **wer** den **Spark versendet** hat, kannst du noch **reveal True** angeben. "
                            "Wenn es **anonym** bleiben soll, dann gib False an.\n")
    embed.add_field(
        name="Hilfe zu /spark: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)



async def helpStreak(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent("Hier siehst du alle relevanten Infos zu deiner Streak. \n"
                           "Jedes mal wenn deine Streak durch 3 teilbar ist, gibt es einen Streakpunkt."
                           "Mit Streakpunkten kannst du dir in Zukunft im Shop unterschiedliche Dinge kaufen, wie zb. Premium")
    embed.add_field(
        name="Hilfe zu /streak: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)

async def helpSettings(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent("Hier kannst du deine Einstellungen anpassen. \n"
                           "Je nachdem ob du Premium hast oder nicht, werden dir andere Buttons angezeigt."
                           "Es wird dir angezeigt was deine aktuellen Einstellungen sind."
                           "Wenn du kein Premium hast, wird dir noch gesagt, was man mit Premium zusätzlich einstellen kann.")
    embed.add_field(
        name="Hilfe zu /settings: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)

async def helpHug(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent("Du kannst taglich einer Person **einen Hug oder Pat** geben. \n"
                           "**Mit Premium** sind Hug/Pats **3x taglich** verwendbar.")
    embed.add_field(
        name="Hilfe zu /hug: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)

async def helpPat(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent("Du kannst täglich einer Person **einen Hug oder Pat** geben. \n"
                           " **Mit Premium** sind Hug/Pats **3x täglich** verwendbar.")
    embed.add_field(
        name="Hilfe zu /pat: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)

async def helpStats(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent("Um deine **eigenen Stats** anzusehen, kannst du **/stats** eingeben. \n"
                           "Der Befehl zeigt dir alle Komplimente (auch custom Nachrichten) an und wie oft du diese bekommen hast."
                           "\n\n **Mit Premium** kannst du mit dem Befehl **/spark_ausblenden** custom Nachrichten ausblenden wenn du die SparkID angibst."
                           "Die SparkID findest du bei deinen Stats neben der custom Nachricht in Klammern. ")
    embed.add_field(
        name="Hilfe zu /stats: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)


async def helpReveal(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent( "Wenn jemand einen Spark macht, kann am Ende noch reveal als True angegeben werden.\n\n"
                            "Mit dem Befehl **/reveal** kannst du sehen, **welche Sparks** du aufdecken kannst.\n"
                            "Mit **/reveal (SparkID)** verwendest du einen Reveal und erfährst, von wem der Spark stammt.\n"
                            "Du brauchst dazu einen Reveal (wie viele du hast, siehst du mit /profil).\n\n"
                            "**Preise:**\n"
                            "2 Reveals = 3€\n"
                            "([3€ über Freunde&Familie senden und deine DiscordID oder Namen angeben](https://www.paypal.com/paypalme/KuroPixel?country.x=DE&locale.x=de_DE))\n"
                            "1 Reveal = 20 Streakpunkte (WIP)\n"
                            "1 Reveal = 40 Votepunkte (WIP)\n"
                            "\n In Zukunft ist noch geplant, dass man den Sender anfragen kann, ob es revealed werden darf.")
    embed.add_field(
        name="Hilfe zu /reveal: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)


async def helpAdmin(interaction):
    embed = discord.Embed(
         color=0x005b96)
    text = textwrap.dedent("Um einen Channel festzulegen, in dem der Bot verwendet werden darf,"
                            "kannst du den Befehl **!setSparkChannel** in dem gewünschten Kanal eingeben."
                            "Es werden Administrator Berechtigungen dafür benötigt."
                            "Wenn kein Channel festgelegt wurde, funktioniert der Bot überall.\n\n"
                            "Es kann zusätzlich noch **!setNewsletterChannel** "
                            "verwendet werden, um vom Bot alle Update Infos zu bekommen.")
    embed.add_field(
        name="Hilfe zur Einrichtung vom Bot: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)


async def helpVote(interaction):
    embed = discord.Embed(
        color=0x005b96)
    text = textwrap.dedent("Um an VotePunkte zu kommen, kannst du alle 12 Stunden einmal Voten.\n"
                           "Wichtig dabei ist, dass du nach dem Voten nocheinmal /vote eingeben musst, um deinen Votepunkt zu erhalten."
                           "Mit diesen Punkten kannst du aktuell noch nichts machen, bald aber Premium und Reveals kaufen.")
    embed.add_field(
        name="Hilfe zu /vote: ",
        value=text,
        inline=False)
    await interaction.response.send_message(embed=embed)