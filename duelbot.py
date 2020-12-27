import os
import discord
from typing import Union
from duel import Duel
from duel import Challenge
from discord.ext import commands
from dotenv import load_dotenv
import datetime
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!duel ")

duel_expiration_message = ("What the hell are you two doin'? Do you even plan "
                           "on killin' each other, or are you just gonna stand "
                           "there like some yellow bellied cowards? Please, "
                           "don't waste this server's time.\n\nSorry folks, "
                           "the duel's off.")


@bot.event
async def on_ready() -> None:
    print(f'{bot.user} has connected to Discord!')
    await check_expirations()


duel = None
challenges = []
current_duel = None

@bot.command()
async def challenge(ctx: discord.ext.commands.Context,
                    challengee: discord.Member) -> None:

    if current_duel is not None:

        message = "Hold it, cowpoke. There's already a duel goin' on."
        await ctx.channel.send(message)
        return

    if challengee == ctx.author:

        message = ("You're challenging... yourself? You need to put down "
                   "the liquor, friend.")
        await ctx.channel.send(message)
        return

    for challenge in challenges:

        if challenge.get_challenger() == challengee \
            and challenge.get_challengee() == ctx.author:

            message = ("Are you dumb, friend? " + challengee.display_name +
                       "'s already challenged you to a duel.")
            await ctx.channel.send(message)
            return

        if challenge.get_challenger() == ctx.author \
            and challenge.get_challengee() == challengee:

            message = ("Patience is a virtue that has obviously been lost on "
                       "you, partner. You've already challenged " +
                       challengee.display_name + ". Settle down.")
            await ctx.channel.send(message)
            return

    challenges.append(Challenge(ctx.author, challengee, ctx.channel))

    message = ("It appears " + ctx.author.display_name + " has challenged "
               + challengee.display_name + " to a good ol' fashioned duel!\n"
               + challengee.display_name + ", reply with `!duel accept " +
               ctx.author.display_name + "` to accept the challenge.")

    await ctx.channel.send(message)

@bot.command()
async def accept(ctx: discord.ext.commands.Context,
                 challenger: discord.Member) -> None:

    global current_duel

    if current_duel is not None:

        if current_duel.has_member(ctx.author):

            message = ("Accept!? *You're already dueling " +
                       challenger.display_name + "*!")
            await ctx.channel.send(message)

        else:

            message = "Quiet down! Can't you see there's a duel goin' on?"
            await ctx.channel.send(message)

        return

    accept_message = ("Well alright then. A duel it is.\n\nNow here's how "
                      "this’ll work. I’m gonna countdown by sayin’ \"One! Two! "
                      "Three! Draw!\"\n\nThen, each gunslinger will draw their "
                      "gun by writing `!duel draw`, and then fire said gun "
                      "with `!duel fire`. The first gunslinger to fire their "
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
async def decline(ctx: discord.ext.commands.Context,
                  challenger: discord.Member) -> None:

    if current_duel is not None:

        if current_duel.has_member(ctx.author):

            message = "Decline!? You're in the duel friend!"
            await ctx.channel.send(message)

        else:

            message = "Would you quiet down? There's a duel goin' on."
            await ctx.channel.send(message)

        return

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

    await ctx.channel.send(nonexistent_message)

@bot.command()
async def ready(ctx: discord.ext.commands.Context) -> None:

    if current_duel is None:

        message = ("Haha! I like your enthusiasm partner, but in case you "
                   "can't see, there ain't no duel going on.")
        await ctx.channel.send(message)
        return

    if current_duel.has_member(ctx.author):

        if current_duel.has_begun():

            message = "*Ready* !? **THE DUEL'S HAPPENIN' RIGHT NOW PARTNER!**"
            await ctx.channel.send(message)

        elif not current_duel.get_gunslinger(ctx.author).is_ready():
            await current_duel.ready_up_gunslinger(ctx.author)

    else:

        message = "Ready? You ain't part of this duel, friend!"
        await ctx.channel.send(message)


@bot.command()
async def draw(ctx: discord.ext.commands.Context) -> None:

    if current_duel is None:

        message = ("Put that gun back in your holster you no good maggot! "
                   "There ain't no duel goin' on! Are you *tryin'* to upset "
                   "the peace of this good server?")

        await ctx.channel.send(message)
        return

    if current_duel.has_member(ctx.author):

        if current_duel.has_begun():
            current_duel.draw(ctx.author)
        else:
            message = ("Easy there, cowpoke. It ain't time for you to draw "
                       "yet.")
            await ctx.channel.send(message)

    else:

        message = ("Put that gun away you no good maggot! You ain't part of "
                   "this duel!")
        await ctx.channel.send(message)

@bot.command()
async def fire(ctx: discord.ext.commands.Context) -> None:

    global current_duel

    if current_duel is None:
        return

    if (not current_duel.has_begun()) \
            and current_duel.has_member(ctx.author):

        message = ("Woah there! Take it easy. It ain't time for you fire yet.")
        await ctx.channel.send(message)
        return

    if not current_duel.has_member(ctx.author):

        message = ("What in the hell are you thinkin'!? You ain't a part of "
                   "this duel!")
        await ctx.channel.send(message)
        return

    await current_duel.fire(ctx.author)

    if current_duel.is_over():
        current_duel = None


async def check_expirations() -> None:

    global current_duel

    while True:

        if current_duel is not None:

            if seconds_between(datetime.datetime.now(),
                               current_duel.get_start_time()) >= 90:

                await current_duel.get_channel().send(duel_expiration_message)
                current_duel = None

        else:

            for challenge in challenges:
                print("AAAA")
                if seconds_between(datetime.datetime.now(),
                                   challenge.get_start_time()) >= 40:

                    challenge_message = ("Well, " +
                                         challenge.get_challenger().mention +
                                         " it seems like " +
                                         challenge.get_challengee().display_name
                                         + " didn't respond. Sorry friend, but "
                                         "we're calling off the challenge.")

                    await challenge.get_channel().send(challenge_message)
                    challenges.remove(challenge)

        await asyncio.sleep(20)


def seconds_between(end: datetime.datetime, start: datetime.datetime) -> int:
    return (end - start).seconds


bot.run(TOKEN)
