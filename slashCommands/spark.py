import asyncio
import discord
import random
from discord import ButtonStyle, ui
from dataBase import *
from config import BotID
from discord.ext import commands
from discord import app_commands
from dataBase import *
from Methoden import *
from config import connection



class Spark(commands.Cog):
    @app_commands.command(name="spark", description="Mache einer Person ein anonymes Kompliment")
    @app_commands.describe(person="Wähle eine Person aus", kompliment="Wähle ein Kompliment aus der Liste")
    async def spark(self, interaction: discord.Interaction, person: discord.Member, kompliment: str, reveal: bool):
        await interaction.response.defer(ephemeral=True)
        userID = str(interaction.user.id)
        userName = interaction.user.display_name
        targetID = str(person.id)
        targetName = person.display_name
        guildID = str(interaction.guild.id)
        guildName = interaction.guild.name
        now = datetime.now()
        channel = interaction.channel
        channelID = str(channel.id)
        
        UserExists(connection, userID)
        await BanStuff(connection, guildID, targetID, userID, interaction)

        Premium = getPremium(connection, userID)
        cooldown = getCooldown(connection, userID)
        date = datetime.now().date().isoformat()
        SparkUses = getSparkUses(connection, userID)

        ResetStreak(connection, userID)
        CheckServerExists(connection, guildID)

        #resettet SparkUses
        if cooldown != date:
            resetSparkUses(connection, userID)
            SparkUses = 0

        await SparkCheck(cooldown, SparkUses, Premium, date, interaction)
        await CheckTarget(targetID, userID, interaction)
        await CheckSparkChannel(connection, guildID, channelID, interaction)

        if SparkUses < 1:
            updateStreak(connection, userID)
            StreakPunkt(connection, userID)

        if reveal == None:
            reveal = False

        if kompliment in compliments:
            updateCooldown(connection, userID)
            updateSparkUses(connection, userID)
            targetCompliments = getCompliments(connection, targetID)

            #seit 25.07.25 wird Compliments Table nicht mehr verwendet sondern die Logs
            #überprüft ob das ausgewählte (kompliment) in der Datenbank ist
            if kompliment in targetCompliments: 
                #nimmt das Kompliment aus der Datenbank (also i guess, weil nur das ausgewählte verändert wird)
                updateCompliment(connection, targetID, kompliment)
            else:
                insertCompliment(connection, targetID, kompliment)

            insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, kompliment, "Compliment", guildID, guildName, reveal)

            embed = discord.Embed(
            title=f"{compliments[kompliment]['name']}",
            description=f"{person.mention} {compliments[kompliment]['text']}",
            color=0x00FF00)

            embed.set_image(url=random.choice(compliments[kompliment].get("link")))
            embed.set_thumbnail(url=person.display_avatar.url)
            embed.set_footer(text=f"Spark ID: {getSparkID(connection)}")

            if getGhostpingSetting(connection, targetID) == True:
                ghostping = await channel.send(f"{person.mention}")
                await ghostping.delete()

            await channel.send(embed=embed)

            if getSparkDM(connection, targetID) == True:
                await asyncio.sleep(2)
                await sendSparkDM(targetID, interaction)
            await interaction.followup.send("Dein Kompliment war erfolgreich :D", ephemeral=True)


        else:
            if Premium:
                CustomSpark = getCustomSparkSetting(connection, targetID)
                if CustomSpark == False:
                    await interaction.followup.send("Diese Person hat ausgestellt, dass man ihr einen custom Spark schicken kann!", ephemeral=True)
                    return
                insertCompliment(connection, targetID, kompliment)
                insertLogs(connection, now.isoformat(), userID, userName, targetID, targetName, kompliment, "Custom", guildID, guildName, reveal)
                updateCooldown(connection, userID)
                updateSparkUses(connection, userID)

                kompliment = replaceEmotes(kompliment, interaction.guild, interaction.client)

                embed = discord.Embed(
                    title=f"{targetName} hier eine Persönliche Nachricht für dich!",
                    description=f"{person.mention} ||| {kompliment}",
                    color=0x008B00
                )
            
                embed.set_footer(text=f"Spark ID: {getSparkID(connection)}")

                await interaction.followup.send("Dein anonymer Text war erfolgreich :D", ephemeral=True)

                if getGhostpingSetting(connection, targetID) == True:
                    ghostping = await channel.send(f"{person.mention}")
                    await ghostping.delete()

                await channel.send(embed=embed)


                if getSparkDM(connection, targetID) == True:
                    await asyncio.sleep(2)
                    await sendSparkDM(targetID, interaction)

            #Wenn nutzer kein Premium hat
            else:
                await interaction.followup.send("Du hast kein Premium! Bitte wähle ein vorhandenes Kompliment aus.", ephemeral=True)


    @spark.autocomplete("kompliment")
    async def kompliment_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = []
        for compliment in compliments:
            choices.append(app_commands.Choice(name=compliment, value=compliment))
        return [choice for choice in choices if current.lower() in choice.name.lower()]


class WhatIsSparkButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Was ist ein Spark?", style=discord.ButtonStyle.secondary, custom_id="whatIsSpark")
    async def what_is_spark(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Ein Spark ist ein **anonymes** Kompliment an dich. Jeder kann **täglich einmal** einer Person einen Spark senden. Wenn du mehr zu bestimmten Befehlen wissen willst, kannst du einfach **/help (CommandName)** eingeben c:", ephemeral=True)

            
async def SparkCheck(cooldown, SparkUses, Premium, date, interaction):

    """prüft ob User heute schon gesparkt hat"""
    if cooldown:
        if Premium:
            #Wenn User Premium hat, dann prüft ob mehr als 2 mal gesparkt wurde
            if SparkUses == 2:
                await interaction.followup.send(f"Du hast Heute bereits 2x gesparkt! Versuchs morgen nochmal.", ephemeral=True)
                raise Exception("2 Uses Premium")
        else:
            if cooldown == date:
                await interaction.followup.send(f"Du kannst den Befehl /spark morgen wieder verwenden.", ephemeral=True)
                raise Exception("Cooldown")



async def sendSparkDM(targetID, interaction):
    channel = interaction.channel

    messages = [msg async for msg in channel.history(limit=1)]
    if messages and messages[0].author.id == BotID:
        target = await interaction.client.fetch_user(int(targetID))
        embed = discord.Embed(title="Du wurdest gesparkt!", description=messages[0].jump_url, color=0x005b96)
        await target.send(embed=embed, view=WhatIsSparkButton())



async def CheckSparkChannel(connection, guildID, channelID, interaction):
    sparkChannel = getChannelSparkID(connection, guildID)
    if sparkChannel != channelID and sparkChannel != None:
        await interaction.followup.send("Du kannst hier keine Befehle nutzen! Nutze den vorgesehenen Channel dafür.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.delete_original_response()
        raise Exception("Wrong Channel")
    

async def setup(bot: commands.Bot):
    await bot.add_cog(Spark(bot))
    print("Spark geladen ✅")