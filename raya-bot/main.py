import os
import requests

import discord
from discord.ext import commands
from discord import app_commands

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1LY0-ltHIzJvcf1gtWZYTf7FOiRu6X5K_EwFAVR8i07w"
SAMPLE_RANGE_NAME = "'Stock League 24 Dec-25 Dec'!C7:D10"


def get_stock_leaderboard():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      return

    output = ""

    rankings = {}

    for row in values:
        name = row[0]
        amt = row[1][3:]
        if amt[0] == '(':
            amt = "-" + amt[1:len(amt)-1]
        amt = amt.replace(",","")
        total = float(amt)
        rankings.update({name: total})
    
    sorted_by_value = reversed(sorted(rankings.items(), key=lambda item: item[1])) 
    rankings = dict(sorted_by_value)
    x = 1
    winner = 0
    for name, val in rankings.items():
       output += f"{x}. {name}: {val:,}$"
       if x == 1:
          winner = val
       else:
          output += f" **({val - winner:,.2f})**"
       x += 1
       output += "\n"

    return output
  except HttpError as err:
    print(err)



##

class RayaBotClient(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        try:
            #guild=discord.Object(id=1232893663361892373)
            synced = await self.tree.sync()
            print(f'Synced {len(synced)} commands')
        except:
            print("Could not sync commands!")



intents = discord.Intents.default()
intents.message_content = True
client = RayaBotClient(intents=intents, command_prefix="!")

#GUILD_ID=discord.Object(id=1232893663361892373)

@client.tree.command(name="stock", description="Get the latest information on the 2025 Stock Competition")
async def sendStockLeaderboard(interaction: discord.Interaction):
    leaderboard = get_stock_leaderboard()
    await interaction.response.send_message(leaderboard)


def main():
    print("Starting Raya Bot...")
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is None:
        print("Token not provided")
        return
    client.run(TOKEN)


if __name__ == '__main__':
    main()
