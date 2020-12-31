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

bot = commands.Bot(command_prefix="!duel ", help_command=None)

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

    if challengee == ctx.author:

        message = ("You're challenging... yourself? You need to put down "
                   "the liquor, friend.")
        await ctx.channel.send(message)
        return

    if challengee == bot.user:

        message = ("Challenge me? Haha, that's a good joke friend.")
        await ctx.channel.send(message)

        await asyncio.sleep(5)

        message = ("You listen here, pal. I know I played it off in the "
                   "server, but lets get something straight. *You do not "
                   "challenge me*, understand? I coordinate the duels, I do "
                   "not participate in them. You pull somethin' like that "
                   "again, and I'll show you what a *real* duel is like.")
        await ctx.author.send(message)
        return

    if current_duel is not None:

        message = "Hold it, cowpoke. There's already a duel goin' on."
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
               ctx.author.display_name + "` to accept the challenge, or `!duel "
               "decline " + ctx.author.display_name + "` to decline.")

    await ctx.channel.send(message)

@bot.command()
async def accept(ctx: discord.ext.commands.Context,
                 challenger: discord.Member) -> None:

    global current_duel

    if challenger == bot.user:

        message = ("Accept a duel from... me? Ha! I never challenged you, but "
                   "if I did, believe me friend—you would not want to accept.")

        await ctx.channel.send(message)
        return

    if challenger == ctx.author:

        message = ("You want to accept a challenge from... yourself? (*Sighs*) "
                   "Alcohol seems to have its grasp quite firmly around you "
                   "partner.")

        await ctx.channel.send(message)
        return

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
                      "message `!duel ready` when you're ready, and the "
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

    if challenger == bot.user:

        message = ("Well guess what—you don't need to decline friend, because "
                   "I never challenged you.")

        await ctx.channel.send(message)
        return

    if challenger == ctx.author:

        message = ("You want to decline a challenge from... yourself? "
                   "(*Sighs*) You're gonna make the saloon bartender quite the "
                   "rich man someday.")

        await ctx.channel.send(message)
        return

    if current_duel is not None:

        if current_duel.has_member(ctx.author):

            message = "Decline!? You're in the duel friend!"
            await ctx.channel.send(message)

        else:

            message = "Would you quiet down? There's a duel goin' on."
            await ctx.channel.send(message)

        return

    decline_message = (ctx.author.display_name + " declined the offer.\n Well, "
                       "at least we won't have to deal with the mess that "
                       "comes afterwards.")
    nonexistent_message = ("Uhh... " + challenger.display_name + " never "
                           "challenged you to a duel. Are you okay, friend?")

    for challenge in challenges:

        if challenge.get_challenger() == challenger \
                and challenge.get_challengee() == ctx.author:

            await ctx.channel.send(decline_message)
            challenges.remove(challenge)
            return

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
                   "this duel you half-wit piece of trash!")
        await ctx.channel.send(message)
        return

    await current_duel.fire(ctx.author)

    if current_duel.is_over():
        current_duel = None

@bot.command()
async def help(ctx: discord.ext.commands.Context) -> None:

    message = ("Howdy partner! I’m DuelBot, the finest duel coordinating bot "
               "there is this side of the internet. \n\n"
               "Now let me explain to you how this works. Let's say you come "
               "across someone that you have somethin’ to settle with. "
               "Go ahead and challenge them to a duel with the command `!duel "
               "challenge user_name`. If they accept, then you get to face "
               "them in one of America’s proudest and most time-honoured "
               "traditions—a gunslinger’s duel!\n\n"
               "If they accept the duel, I’ll be there to provide you with "
               "further instructions. So that’s really all you need to know. "
               "So, get your guns, strap on your holsters, and get goin’ "
               "cowpoke!\n\n"
               "Note: my profile picture was created by none other than the "
               "fine folks at Freepik: "
               "<https://www.flaticon.com/authors/freepik>")

    await ctx.channel.send(message)

@bot.event
async def on_command_error(ctx: discord.ext.commands.Context,
                           error: discord.ext.commands.CommandError) -> None:

    if isinstance(error, discord.ext.commands.CommandNotFound):

        message = ("I don't reckon that's a valid command, partner. Send the "
                   "message `!duel help` to get some assistance.")
        await ctx.channel.send(message)

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

                if seconds_between(datetime.datetime.now(),
                                   challenge.get_start_time()) >= 40:

                    challenge_message = ("Well, " +
                                         challenge.get_challenger().mention +
                                         ", it seems like " +
                                         challenge.get_challengee().display_name
                                         + " didn't respond. Sorry friend, but "
                                         "we're calling off the challenge.")

                    await challenge.get_channel().send(challenge_message)
                    challenges.remove(challenge)

        await asyncio.sleep(20)


def seconds_between(end: datetime.datetime, start: datetime.datetime) -> int:
    return (end - start).seconds


bot.run(TOKEN)
