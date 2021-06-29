from __future__ import print_function
import discord
from discord.ext import commands
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

with open('token.txt') as fin:
    TOKEN = fin.read()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

"""Shows basic usage of the Sheets API.
Prints values from a sample spreadsheet.
"""
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('sheets', 'v4', credentials=creds)

@bot.event
async def on_ready():
    print('working')

@bot.command(name='test')
async def test(ctx):
    await ctx.send("Testing")

@bot.command(name='potato')
async def potato(ctx):
    await ctx.send("https://www.food.com/recipe/dauphine-potatoes-310154")

@bot.command(name='points')
async def points(ctx, person=None):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId='1EEeck6LYRV31bpjvFLBkgz9ifOFpsHHq7tOfiFUQ7x0',
                                range='Points').execute()
    values = result.get('values', [])
    
    if person is None:
        person = ctx.author.display_name
    
    for row in values:
        if row[1].lower() == person.lower():
            await ctx.send(f'{row[1]} has {row[2]} total points for Team Ninji.')
            break
    else:
        await ctx.send(f"Couldn't find a discord user in the spreadsheet named {person}.")

    beginner = ctx.guild.get_role(858718970789625876)
    intermediate = ctx.guild.get_role(858718987105992726)
    expert = ctx.guild.get_role(858719008593149992)
    legend = ctx.guild.get_role(858719023565897748)
    roles = [beginner, intermediate, expert, legend]

    beginnerPoints = 20
    intermediatePoints = 100
    expertPoints = 300
    legendPoints = 600
    
    for row in values:
        for member in ctx.guild.members:
            if row[1].lower() == member.display_name.lower():
                points = int(row[2])
                print(points)
                await clear(member, *roles)
                if points < beginnerPoints:
                    print("No role")
                    break
                elif points < intermediatePoints:
                    print("Beginner")
                    await member.add_roles(beginner)
                    break
                elif points < expertPoints:
                    print("Intermediate")
                    await member.add_roles(intermediate)
                    break
                elif points < legendPoints:
                    print("Expert")
                    await member.add_roles(expert)
                    break
                elif points >= legendPoints:
                    print("Legend")
                    await member.add_roles(legend)
                    break

async def clear(member, *roles):
    for role in roles:
        if role in member.roles:
            await member.remove_roles(role)


bot.run(TOKEN)