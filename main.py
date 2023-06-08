import sheets
import discord
import enum
import os

bot = discord.Bot()
guild_ids = [1044711937956651089, 1049530135914762240]
authorized_users = [497930397985013781, 898734231486869565]


@bot.listen()
async def on_connect():
    sheets.init()
    print("bot is connected")


@bot.event
async def on_ready():
    print("Bot is online")


class quota_type_(enum.Enum):
    EVENTS = "B"
    INVITE_RECRUITMENT = "C"
    DIVISIONAL_RECRUITMENT = "D"
    GAME_RECRUITMENT = "E"
    SEA_LOGGING = "F"
    RAIDS = "G"


@bot.slash_command(name="add_quota", description="Add quota to a user in the spreadsheet", guild_ids=guild_ids)
async def add_quota(ctx, user, quota_type: discord.Option(quota_type_)):
    await ctx.defer()  # defer call
    if ctx.author.id in authorized_users:  # check if the user is authorized
        response = sheets.add_quota(user, str(quota_type.value))  # add quota using the helper function in sheets
        if response == "Not Found":
            await ctx.respond("User not found", ephemeral=True)
        elif response == "Too many users":
            await ctx.respond("Many users found.", ephemeral=True)
        else:
            await ctx.respond(f"Added quota to user {response}")
    else:
        await ctx.respond("You are not authorized to use this command", ephemeral=True)


@bot.slash_command(name="get_users", description="Get a list of the users in the sheet", guild_ids=guild_ids)
async def get_users(ctx):  # get users from the spreadsheet
    if ctx.author.id in authorized_users:
        await ctx.defer()  # defer the response
        users = sheets.get_users()  # call helper function in sheets py
        embed = discord.Embed(
            title="List of users and their quotas",
            description="".join([i[0] + " **" + i[1] + "** \n" for i in users.items() if i[0] != ""]),  # format in proper description
            color=discord.Color.random()  # set color to random
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("You are not authorized to use this command", ephemeral=True)

# @bot.slash_command(name='link_account', description="Link your account to the spreadsheet")
# async def link_account(ctx, name:discord.Option(discord.User), guild_ids=guild_ids):
#     if ctx.id in authorized_users:
#
#     else:
#         ctx.respond("You are not authorized to use this command!", ephemeral=True)

bot.run(os.environ['token'])
