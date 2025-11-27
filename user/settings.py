from dataBase import *
import discord
import emotes as E
from discord import ButtonStyle, ui

connection = createConnection()

#secondary, grey, gray = grau
#primary, blurple = blau
#danger, red = rot
#green, success = grün
#link = link benötigt
#premium = sku_id benötigt

class newSettings(discord.ui.View):
    def __init__(self, premium: bool, userID: int):
        super().__init__(timeout=60)
        self.userID = userID
        self.premium = premium

        # Daten laden
        self.settingStuff(userID)

    # ---- Format-Helfer ----
    @staticmethod
    def format_privacy(val): 
        return "Privat 🔒" if val == 1 else "Öffentlich 🌐"

    @staticmethod
    def format_toggle(val): 
        return "Aktiv ✅" if val == 1 else "Deaktiv ❌"

    # ---- Daten laden (normal) ----
    def settingStuff(self, userID):
        self.streakPrivate = self.format_privacy(getStreakPrivate(connection, userID))
        self.statsPrivate = self.format_privacy(getStatsPrivate(connection, userID))
        self.profilPrivate = self.format_privacy(getProfilPrivateSetting(connection, userID))
        self.newsletter = self.format_toggle(getNewsletter(connection, userID))
        self.sparkDM = self.format_toggle(getSparkDM(connection, userID))
        self.ghostPing = self.format_toggle(getGhostpingSetting(connection, userID))
        self.customSpark = self.format_toggle(getCustomSparkSetting(connection, userID))
        self.premiumDM = self.format_toggle(getPremiumDMSetting(connection, userID))

    def settingEmbed(self):
        embed = discord.Embed(title="Einstellungen", color=0x005b96)

        embed.add_field(
            name="🔒 Privatsphären Einstellungen",
            value=f">>> `Streak` → {self.streakPrivate}\n"
                  f"`Profil` → {self.profilPrivate}",
            inline=False
        )

        embed.add_field(
            name="⚙️ Allgemeine Einstellungen",
            value=f">>> `Ghostping` → {self.ghostPing}",
            inline=False
        )

        embed.add_field(
            name="💎 Premium Einstellungen",
            value=f">>> `Newsletter` → {self.newsletter}\n"
                  f"`SparkDM` → {self.sparkDM}\n"
                  f"`Stats` → {self.statsPrivate}\n"
                  f"`Custom Sparks` → {self.customSpark}\n"
                  f"`PremiumDM` → {self.premiumDM}",
            inline=False
        )

        return embed

    # Premium-Embed (Platzhalter)
    def settingEmbedPremium(self):
        embed = discord.Embed(title="Einstellungen", color=0x005b96)
        embed.add_field(
            name="🔒 Privatsphären Einstellungen",
            value=f">>> `Streak` → {self.streakPrivate}\n"
                f"`Profil` → {self.profilPrivate}\n"
                f"`Stats` → {self.statsPrivate}",
            inline=False
        )
        embed.add_field(
            name="⚙️ Allgemeine Einstellungen",
            value=f">>> `Ghostping` → {self.ghostPing}\n"
                f"`Newsletter` → {self.newsletter}\n"
                f"`SparkDM` → {self.sparkDM}\n"
                f"`PremiumDM` → {self.premiumDM}\n"
                f"`Custom Sparks` → {self.customSpark}",
            inline=False
        )
        return embed
    
    def getEmbed(self):
        if self.premium:
            return self.settingEmbedPremium()
        else:
            return self.settingEmbed()



class SettingSelect(discord.ui.Select):
    def __init__(self, hatPremium, userID):
        self.userID = userID
        self.hatPremium = hatPremium
        options = [
                discord.SelectOption(label="Streak", description="Stelle ein, ob deine Streak Privat oder Öffentlich angezeigt werden soll", value="streak", emoji=f"{E.StreakPoint}"),
                discord.SelectOption(label="Profil", description="Stelle ein, ob dein Profil Privat oder Öffentlich angezeigt werden soll", value="profil", emoji="👤")
            ]
        
        if hatPremium:
            options.append(discord.SelectOption(label="Stats", description="Stelle ein, ob deine Stats Privat oder Öffentlich angezeigt werden sollen", value="stats", emoji="📊"))
            options.append(discord.SelectOption(label="Ping", description="Stelle ein, ob du Pings erhalten möchtest, wenn du gesparkt wirst", value="Ping", emoji=f"{E.Ping}"))
            options.append(discord.SelectOption(label="Newsletter", description="Stelle ein, ob du Updates vom Bot in deine DMs erhalten möchtest", value="newsletter", emoji="📰"))
            options.append(discord.SelectOption(label="SparkDM", description="Stelle ein, ob du vom Bot angeschrieben werden willst, wenn du gesparkt wurdest", value="sparkdm", emoji=f"{E.Schaufel}"))
            options.append(discord.SelectOption(label="PremiumDM", description="Stelle ein, ob du vom Bot angeschrieben werden willst, wenn dein Premium abläuft", value="premiumdm", emoji="👑"))
            options.append(discord.SelectOption(label="Custom Sparks", description="Stelle ein, ob du Custom Sparks erhalten möchtest", value="customsparks", emoji="✨"))
        else: #Damit bei Premium alles in richtiger Reihenfolge angezeigt wird
            options.append(discord.SelectOption(label="Ping", description="Stelle ein, ob du Pings erhalten möchtest", value="Ping", emoji=f"{E.Ping}"))
            
        super().__init__(placeholder="Einstellungen ändern", min_values=1, max_values=1, options=options)


    async def callback(self, interaction: discord.Interaction):
        userID = str(interaction.user.id)
        value = self.values[0]  # der ausgewählte Wert

        # ----- Umschalt-Logik -----
        if value == "streak":
            val = getStreakPrivate(connection, userID)
            setStreakPrivate(connection, userID, not val)

        elif value == "profil":
            val = getProfilPrivateSetting(connection, userID)
            setProfilPrivateSetting(connection, userID, not val)

        elif value == "Ping":
            val = getGhostpingSetting(connection, userID)
            setGhostpingSetting(connection, userID, not val)

        elif value == "newsletter":
            val = getNewsletter(connection, userID)
            setNewsletter(connection, userID, not val)

        elif value == "sparkdm":
            val = getSparkDM(connection, userID)
            setSparkDM(connection, userID, not val)

        elif value == "premiumdm":
            val = getPremiumDMSetting(connection, userID)
            setPremiumDMSetting(connection, userID, not val)

        elif value == "stats":
            val = getStatsPrivate(connection, userID)
            setStatsPrivate(connection, userID, not val)

        elif value == "customsparks":
            val = getCustomSparkSetting(connection, userID)
            setCustomSparkSetting(connection, userID, not val)

        # ----- Embed neu aufbauen -----
        settingsObj = newSettings(self.hatPremium, userID)
        await interaction.response.edit_message(embed=settingsObj.getEmbed(), view=self.view)



class SettingsView(discord.ui.View):
    def __init__(self, hatPremium: bool, userID: int):
        super().__init__(timeout=120)
        self.add_item(SettingSelect(hatPremium, userID))










#-------------- SettingStuff for Server ------------------
class ServerSettingSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Hug/Pat", value="hug", emoji=f"{E.StreakPoint}"),
            discord.SelectOption(label="Sparks", value="spark", emoji="👤")
        ]
        super().__init__(placeholder="Einstellungen ändern", min_values=1, max_values=1, options=options)


    async def callback(self, interaction: discord.Interaction):
        serverID = str(interaction.guild.id)
        value = self.values[0]

        if value == "hug":
            val = getServerAnonymHug(connection, serverID)
            setServerAnonymHug(connection, serverID, not val)

        elif value == "spark":
            val = getServerAnonymSpark(connection, serverID)
            setServerAnonymSpark(connection, serverID, not val)

        # ----- Embed neu aufbauen -----
        view = ServerSettingView(serverID)
        embed = view.Embed()
        await interaction.response.edit_message(embed=embed, view=view)



class ServerSettingView(discord.ui.View):
    def __init__(self, serverID: int):
        super().__init__()
        self.serverID = serverID
        self.add_item(ServerSettingSelect())

    def Embed(self):
        embed = discord.Embed(title="Einstellungen", color=0x005b96)
        embed.add_field(
            name="🔒 Anonymität Auswahlmöglichkeiten",
            value=ServerSettingView.embedFormat(self),
            inline=False
        )
        return embed
    
    def embedFormat(self):
        serverID = self.serverID
        if getServerAnonymHug(connection, serverID) == 0 and getServerAnonymSpark(connection, serverID) == 0:
            return ">>> `Hug/Pat` → Ja/Halb/Nein\n`Sparks` → Ja/Halb/Nein"
        elif getServerAnonymHug(connection, serverID) == 0 and getServerAnonymSpark(connection, serverID) == 1:
            return ">>> `Hug/Pat` → Ja/Halb/Nein\n`Sparks` → Ja/Halb"
        elif getServerAnonymHug(connection, serverID) == 1 and getServerAnonymSpark(connection, serverID) == 0:
            return ">>> `Hug/Pat` → Ja/Halb\n`Sparks` → Ja/Halb/Nein"
        else:
            return ">>> `Hug/Pat` → Ja/Halb\n`Sparks` → Ja/Halb"