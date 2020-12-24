import os
import discord
from typing import Union
from duel import Duel
from duel import Challenge
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot("!duel ")


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


duel = None
challenges = []


@bot.command()
async def challenge(ctx: discord.ext.commands.Context,
                    challengee: discord.Member):
    
    # TODO: Check if the challengee has already challenged the challenger

    challenges.append(Challenge(ctx.author, challengee))


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
                      "\n\nNow, " + ctx.author.nick + ", " + challenger.nick +
                      ", if you will, please send the message \"!duel ready\" "
                      "when you're ready, and the countdown will begin.")

    nonexistent_message = ("Are you drunk, partner? " + challenger.nick +
                           " never challenged you to a duel.")

    for challenge in challenges:

        if challenge.get_challenger() == challenger \
                and challenge.get_challengee() == ctx.author:
            ctx.channel.send(accept_message)
            return

    ctx.channel.send(nonexistent_message)


def get_challenge(message: discord.Member) -> Union[discord.Member, None]:
    if message.content.startswith("!duel @"):

        challenged_user = None
        if len(message.mentions) == 1:
            challenged_user = message.mentions[0]

        if (challenged_user is not None
                and challenged_user.name == message.content[7:]):
            return challenged_user


'''
@bot.event
async def on_message(message: discord.Member):

    global duel

    # Challenging someone to a duel
    challenged_user = get_challenge(message)
    if challenged_user is not None:

        challenges.append((message.author, challenged_user))

        message = "It appears " + message.author.name + " has challenged " + \
                  challenged_user.name + " to a good ol' fashioned duel! " \
                  "Say, " + challenged_user.mention + ", do you accept this " \
                  "challenge?"

        message.channel.send(message)

    # Accept a duel
    if duel is None:

        duel = get_accepted_duel(message)
        if duel is not None:

            members = duel.get_members()
            message = "Well alright then. A duel it is. \n \n Please, " + \
                      members[0].name + ", " + members[1].name + ", take " + \
                      "your positions. \n \n Now, everyone, here's how this" + \
                      " will work: a countdown from 3 will start when both " + \
                      "gunslingers are ready. Then, each gunslingers will " + \
                      "draw their gun by sending the message \"!duel draw\"" + \
                      " in the chat. After that, they'll each fire their " + \
                      "gun by sending the message \"!duel fire\" in the " + \
                      "chat. The first gunslinger to fire off their gun" + \
                      " will win, and the other gunslinger... well, they'll" + \
                      " be sent to meet their maker. Understood? Now, " + \
                      members[0].name + ", " + members[1].name + ", if you " + \
                      "will, please send the message \"!duel ready\" when " + \
                      "you're ready, and the countdown will begin."

            message.channel.send("")

    else:

        if message.content == "!duel ready" \
                and message.author in duel.get_members():

            duel.ready_up_gunslinger(message.author)

        if message.content == "!duel draw" \
                and message.author in duel.get_members():

            duel.draw(message.author)

        if message.content == "!duel fire" \
                and message.author in duel.get_members():

            duel.fire(message.author)

        if duel.is_over():

            members = duel.get_members()

            if members in challenges:
                challenges.remove(members)
            elif (members[1], members[0]) in challenges:
                challenges.remove((members[1], members[0]))

            duel = None


def get_accepted_duel(message: discord.Member) -> Union[Duel, None]:

    if message.content.startswith("!duel accept @"):

        challenging_user = None
        if len(message.mentions) == 1:
            challenging_user = message.mentions[0]

        if (challenging_user is not None
                and challenging_user.name == message.content[14:]
                and (challenging_user, message.author) in challenges):

            return Duel(challenging_user, message.author, message.channel)

    return None


def get_challenge(message: discord.Member) -> Union[discord.Member, None]:

    if message.content.startswith("!duel @"):

        challenged_user = None
        if len(message.mentions) == 1:
            challenged_user = message.mentions[0]

        if (challenged_user is not None
                and challenged_user.name == message.content[7:]):
            return challenged_user

'''
bot.run(TOKEN)
