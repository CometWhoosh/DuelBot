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

    for challenge in challenges:
        if challenge.get_challenger() == challengee \
            and challenge.get_challengee() == ctx.author:

            message = ("Are you dumb, friend? " + challengee.display_name +
                       "'s already challenged you to a duel.")
            await ctx.channel.send(message)

    challenges.append(Challenge(ctx.author, challengee))

    message = ("It appears " + ctx.author.display_name + " has challenged "
               + challengee.display_name + " to a good ol' fashion duel!\n"
               + challengee.display_name + ", reply with \"!duel accept "
               "@" + ctx.author.display_name + "\" to accept the challenge.")

    await ctx.channel.send(message)

@bot.command()
async def accept(ctx: discord.ext.commands.Context, challenger: discord.Member):

    global current_duel

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
            challenges.remove(challenge)

            return

    await ctx.channel.send(nonexistent_message)

@bot.command()
async def decline(ctx, challenger: discord.Member):

    decline_message = (challenger.display_name + " declined the offer.\n Well, "
                       "at least we won't have to deal with the mess that "
                       "comes afterwards.")
    nonexistent_message = ("Uhh... " + challenger.display_name + " never "
                           "challenged you to a duel. Are you okay, friend?")

    for challenge in challenges:

        if challenge.get_challenger() == challenger \
                and challenge.get_challengee() == ctx.author:

            await ctx.channel.send(decline_message)
            challenges.remove(challenge)

    await ctx.send.channel(nonexistent_message)

@bot.command()
async def ready(ctx):

    if current_duel is None:

        message = ("Hold your horses there, trigger finger! There ain't no"
                   "duel goin' on.")
        await ctx.channel.send(message)
        return

    if current_duel.has_member(ctx.author):
        await current_duel.ready_up_gunslinger(ctx.author)

@bot.command()
async def draw(ctx):

    if current_duel is None:

        message = ("Put that gun back in your holster you no good maggot! "
                   "There ain't no duel goin' on! Are you *tryin'* to upset "
                   "the peace of this good server?")

        await ctx.channel.send(message)
        return

    if (not current_duel.is_active()) \
            and current_duel.has_member(ctx.author):

        message = ("Easy there, cowpoke. It ain't time for you to draw yet.")
        await ctx.channel.send(message)
        return

    if current_duel.has_member(ctx.author):
        current_duel.draw(ctx.author)

@bot.command()
async def fire(ctx):

    global current_duel

    if current_duel is None:
        return

    if (not current_duel.is_active()) \
            and current_duel.has_member(ctx.author):

        message = ("Woah there! Take it easy. It ain't time for you fire yet.")
        await ctx.channel.send(message)
        return

    if current_duel.has_member(ctx.author):
        await current_duel.fire(ctx.author)

    if current_duel.is_over():
        current_duel = None

bot.run(TOKEN)
