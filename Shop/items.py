from dataclasses import dataclass
from enum import Enum
from disableCustomSpark import *
from discord import ui

class PriceType(Enum):
    VotePunkt = "VotePunkte"
    StreakPunkt = "StreakPunkte"


@dataclass
class ShopItem:
    itemID: int
    name: str
    description: str
    price: int
    priceType: PriceType 
    image: str

def checkUserHasItem(connection, userID, itemID):
    userInventar = getUserItems(connection, userID)
    for item, count in userInventar:
        if item == itemID and count > 0:
            return True
    return False



async def useMask(interaction, SparkID = None): #SparkID muss über Modal übergeben werden
    userID = str(interaction.user.id)
    itemID = getItemIDByName(connection, "🎭 Verborgene Maske")
    
    try:
        updateUserInventar(connection, userID, itemID, -1)
        await checkStatCanBeDisabled(SparkID, userID, interaction)
    except Exception as e:
        await interaction.followup.send(f"Fehler: {e}", ephemeral=True)
        print(f"Fehler bei useMask: {e}")


async def useKrone(interaction):
    userID = str(interaction.user.id)
    itemID = getItemIDByName(connection, "👑 Premium-Krone")
    try:
        setPremium(connection, userID)
        updateUserInventar(connection, userID, itemID, -1)
        await interaction.followup.send("Eine unsichtbare Macht setzt dir die Premium-Krone auf. Ihr Licht durchdringt die Dunkelheit und weist dir nun exklusive Wege!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Fehler: {e}", ephemeral=True)
        print(f"Fehler bei useKrone: {e}")


async def useBrille(interaction, SparkID = None):
    userID = str(interaction.user.id)
    itemID = getItemIDByName(connection, "👓 Weisheitsbrille")
    try:
        updateUserInventar(connection, userID, itemID, -1)
        addRevealUses(connection, userID, 1)
        await interaction.followup.send("Die Wahrheitsbrille flackert auf, und ein Funken Klarheit brennt sich in dein Bewusstsein. \nDu erhältst einen Reveal!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Fehler: {e}", ephemeral=True)
        print(f"Fehler bei useBrille: {e}")


class SparkIDModal(ui.Modal, title="SparkID eingeben"):
    def __init__(self, action, itemName):
        super().__init__()
        self.action = action
        self.itemName = itemName

        self.SparkID = ui.TextInput(
            label="SparkID",
            placeholder="Gib hier die SparkID ein",
            required=True,
            min_length=1,
            max_length=6
        )
        self.add_item(self.SparkID)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.action(interaction, self.SparkID.value)
            await interaction.followup.send(f"✅ {self.itemName} wurde erfolgreich benutzt!", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Fehler: {e}", ephemeral=True)


ITEM_ACTIONS = {
    "🎭 Verborgene Maske": {"func": useMask, "needSparkID": True},
    "👑 Premium-Krone": {"func": useKrone, "needSparkID": False},
    "👓 Weisheitsbrille": {"func": useBrille, "needSparkID": False},
}