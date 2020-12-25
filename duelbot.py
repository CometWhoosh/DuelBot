import os
import discord
from typing import Union
from duel import Duel
from duel import Challenge
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!duel ")


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


duel = None
challenges = []
current_duel = None

@bot.command()
async def challenge(ctx: discord.ext.commands.Context,
                    challengee: discord.Member):

    print('INSIDE FUNCTION')

    for challenge in challenges:
        if challenge.get_challenger() == challengee \
            and challenge.get_challengee() == ctx.author:

            message = ("Are you dumb, friend? " + challengee + "'s already "
                       "challenged you to a duel.")
            await ctx.channel.send(message)

    challenges.append(Challenge(ctx.author, challengee))

    message = ("It appears " + ctx.author.display_name + " has challenged "
               + challengee.display_name + " to a good ol’ fashion duel!\n"
               + challengee.display_name + ", reply with \"!duel accept "
               "@" + ctx.author.display_name + "\" to accept the challenge.")

    await ctx.channel.send(message)

@bot.command()
async def accept(ctx: discord.ext.commands.Context, challenger: discord.Member):
    challenge_exists = False
    accept_message = ("Well alright then. A duel it is.\n\nNow here's how "
                      "this’ll work. I’m gonna countdown by sayin’ \"One! Two! "
                      "Three! Draw!\"\n\nThen, each gunslinger will draw their "
                      "gun by writing “!duel draw”, and then fire said gun "
                      "with \"!duel fire\". The first gunslinger to fire their "
                      "pistol will win, and the other gunslinger... well, "
                      "they'll be on their way to meet their maker. Understand?"
                      "\n\nNow, " + ctx.author.display_name + ", " +
                      challenger.display_name +", if you will, please send the "
                      "message \"!duel ready\" when you're ready, and the "
                      "countdown will begin.")

    nonexistent_message = ("Are you drunk, partner? " +
                           challenger.display_name + " never challenged you to "
                           "a duel.")

    for challenge in challenges:

        if challenge.get_challenger() == challenger \
                and challenge.get_challengee() == ctx.author:

            await ctx.channel.send(accept_message)
            current_duel = Duel(ctx.author, challenger, ctx.channel)

            return

    await ctx.channel.send(nonexistent_message)

@bot.command()
async def ready(ctx):

    if current_duel is None:

        message = ("Hold your horses there, trigger finger! There ain't no"
                   "no duel goin' on. You need to sober up friend.")
        await ctx.channel.send(message)
        return

    current_duel.ready_up_gunslinger(ctx.author)

bot.run(TOKEN)
