import discord
import calendar
from datetime import datetime
from typing import Optional, Callable, Awaitable

MONTHS = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]

class BirthdayModal(discord.ui.Modal, title="Tag & optionales Jahr eingeben"):
    day = discord.ui.TextInput(
        label="Tag (Zahl)",
        placeholder="1-31",
        required=True,
        min_length=1,
        max_length=2
    )
    year = discord.ui.TextInput(
        label="Jahr (optional)",
        placeholder="z. B. 2004 — wenn leer, wird 2000 genutzt",
        required=False,
        min_length=4,
        max_length=4
    )

    def __init__(self, parent_view: "BirthdayView"):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        # Nur der Owner darf das Modal absenden
        if interaction.user.id != self.parent_view.owner_id:
            await interaction.response.send_message("Nur du kannst hier deinen Geburtstag setzen.", ephemeral=True)
            return

        # parse day
        try:
            day = int(self.day.value.strip())
        except ValueError:
            await interaction.response.send_message("Ungültiger Tag. Bitte eine Zahl eingeben.", ephemeral=True)
            return

        # parse year (optional)
        year_val = None
        yraw = self.year.value.strip()
        if yraw != "":
            try:
                year_val = int(yraw)
                if not (1 <= year_val <= 9999):
                    raise ValueError()
            except ValueError:
                await interaction.response.send_message("Ungültiges Jahr. Bitte ein gültiges Jahr (z.B. 1995) oder leer lassen.", ephemeral=True)
                return

        month = self.parent_view.selected_month

        # Validate day bounds:
        if year_val is not None:
            # validate with exact year (Schaltjahre korrekt)
            _, days_in_month = calendar.monthrange(year_val, month)
            if not (1 <= day <= days_in_month):
                await interaction.response.send_message(f"Ungültiger Tag: {calendar.month_name[month]} {year_val} hat {days_in_month} Tage.", ephemeral=True)
                return
        else:
            # year fehlt: erlauben bis max normale Tage pro Monat (Feb = 29 akzeptieren, aber warnen)
            if month == 2:
                days_in_month = 29  # erlauben 29 (kann Leap-Day sein)
            else:
                days_in_month = 31 if month in {1,3,5,7,8,10,12} else 30
            if not (1 <= day <= days_in_month):
                await interaction.response.send_message(f"Ungültiger Tag: {MONTHS[month-1]} hat max. {days_in_month} Tage (wenn Jahr weggelassen).", ephemeral=True)
                return

        # Call save callback (support async or sync)
        cb = self.parent_view.save_callback
        try:
            if cb:
                # signature: callback(user_id:int, year:Optional[int], month:int, day:int)
                if hasattr(cb, "__await__"):  # async function
                    await cb(interaction.user.id, year_val, month, day)
                else:
                    cb(interaction.user.id, year_val, month, day)
        except Exception as e:
            # Falls DB-Fehler o.ä.
            await interaction.response.send_message(f"Fehler beim Speichern: {e}", ephemeral=True)
            return

        # Bestätigungs-Reply (ephemeral)
        pretty = f"{day:02d}.{month:02d}.{year_val}" if year_val else f"{day:02d}.{month:02d} (Jahr nicht angegeben)"
        await interaction.response.send_message(f"✅ Geburtstag gesetzt: {pretty}", ephemeral=True)

        # Deaktiviere die View-Buttons/Selects in der ursprünglichen Nachricht, falls vorhanden
        try:
            if hasattr(self.parent_view, "message") and self.parent_view.message:
                for child in self.parent_view.children:
                    child.disabled = True
                await self.parent_view.message.edit(content=f"Geburtstag gesetzt: {pretty}", view=self.parent_view)
        except Exception:
            # ignoring edit errors (z. B. wenn original message ephemeral war)
            pass

class MonthSelect(discord.ui.Select):
    def __init__(self, parent_view: "BirthdayView", default_month: int):
        options = [
            discord.SelectOption(label=MONTHS[i], value=str(i+1))
            for i in range(12)
        ]
        super().__init__(placeholder="Monat wählen...", min_values=1, max_values=1, options=options, row=0)
        self.parent_view = parent_view
        # set default
        self.default = [str(default_month)]

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.owner_id:
            await interaction.response.send_message(f"Nur <@{self.parent_view.owner_id}> kann den Kalender steuern.", ephemeral=True)
            return
        chosen = int(self.values[0])
        self.parent_view.selected_month = chosen
        # Update embed to reflect selection
        await interaction.response.edit_message(embed=self.parent_view.build_embed(), view=self.parent_view)



class BirthdayView(discord.ui.View):
    def __init__(
        self,
        owner_id: int,
        save_callback: Optional[Callable[[int, Optional[int], int, int], Awaitable]] = None,
        default_month: Optional[int] = None,
        timeout: float = 300
    ):
        super().__init__(timeout=timeout)
        self.owner_id = owner_id
        self.save_callback = save_callback
        self.selected_month = default_month or datetime.utcnow().month
        self.message: Optional[discord.Message] = None

        # MonthSelect hinzufügen
        self.add_item(MonthSelect(self, default_month=self.selected_month))

    def build_embed(self) -> discord.Embed:
        m = self.selected_month
        emb = discord.Embed(
            title="Geburtstag setzen",
            description=f"Monat: **{MONTHS[m-1]}**\nWähle den Tag und optional das Jahr.",
            color=0x2b90d9
        )
        emb.add_field(
            name="Hinweis",
            value="Klicke auf **Tag & Jahr eingeben**, um ein Formular zu öffnen.",
            inline=False
        )
        return emb

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Nur der Besitzer darf mit der View interagieren"""
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                f"Nur <@{self.owner_id}> kann den Kalender steuern.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Tag & Jahr eingeben", style=discord.ButtonStyle.primary, row=1)
    async def enter_day_year_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Öffnet das Modal für Tag + optionales Jahr"""
        await interaction.response.send_modal(BirthdayModal(self))

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.danger, row=1)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bricht die Eingabe ab"""
        await interaction.response.edit_message(content="❌ Abgebrochen.", embed=None, view=None)

    async def on_timeout(self):
        """View deaktivieren, wenn Zeit abläuft"""
        for child in self.children:
            child.disabled = True
        try:
            if self.message:
                await self.message.edit(view=self)
        except Exception:
            pass

    async def on_error(self, error: Exception, item, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(f"Ein Fehler ist aufgetreten: {error}", ephemeral=True)
        except Exception:
            pass
