from __future__ import annotations
import discord
from typing import Tuple
import random
import asyncio
import datetime

class Gunslinger:
    """
    This class represents a gunslinger who is dueling another gunslinger.
    The gunslinger can only fire their gun if they have drawn it, and they can
    only draw it if they are ready to duel.

    Attributes
    ==========

    member: discord.Member
        the discord.Member that controls the gunslinger
    ready:
        True if the gunslinger is ready to duel. False otherwise
    drawn:
        True if the gunslinger has drawn their gun. False otherwise
    fired:
        True if the gunslinger has fired their gun. False otherwise
    alive:
        True if the gunslinger is alive. False otherwise
    """

    def __init__(self, member: discord.Member):

        self.member = member
        self.ready = False
        self.drawn = False
        self.fired = False
        self.alive = True

    def ready_up(self) -> None:
        """Makes the gunslinger ready to duel"""
        self.ready = True

    def draw(self) -> None:
        """
        Makes the gunslinger draw their gun. This can only happen if they are
        ready.
        """
        if self.ready:
            self.drawn = True

    def fire(self) -> None:
        """
        Makes the gunslinger fire their gun. This can only happen if they
        have drawn their gun.
        """
        if self.drawn:
            self.fired = True

    def die(self) -> None:
        """Makes the gunslinger die"""
        self.alive = False

    def get_member(self) -> discord.Member:
        return self.member

    def is_ready(self) -> bool:
        """
        Indicates whether or not the gunslinger is ready to duel
        :return: True if the gunslinger is ready, or False otherwise.
        """
        return self.ready

    def has_drawn(self) -> bool:
        """
        Indicates whether or not the gunslinger has drawn their gun
        :return: True if the gunslinger has drawn, or False otherwise.
        """
        return self.drawn

    def has_fired(self) -> bool:
        """
        Indicates whether or not the gunslinger has fired their gun
        :return: True if the gunslinger has fired, or False otherwise.
        """
        return self.fired

    def is_alive(self) -> bool:
        """
        Indicates whether or not the gunslinger is dead
        :return: True if the gunslinger is dead, or False otherwise.
        """
        return self.alive

    def is_member(self, member: discord.Member) -> bool:
        return self.member == member


class Challenge:
    """
    This class represents a challenge that one gunslinger made to another. Each
    challenge contains the time that it was issued, as well as the two members
    involved.

    Attributes
    ==========

    challenger:
        the member that issued the challenge
    challengee:
        the member that was challenged
    time:
        the time that the challenge was issued
    """

    def __init__(self, challenger: discord.Member, challengee: discord.Member):

        self.challenger = challenger
        self.challengee = challengee
        self.time = datetime.datetime.now()

    def get_challenger(self) -> discord.Member:
        return self.challenger

    def get_challengee(self) -> discord.Member:
        return self.challengee

    def get_time(self) -> datetime.datetime:
        return self.time

    def __eq__(self, other: Challenge) -> bool:

        if not isinstance(other, Challenge):
            return NotImplemented

        return self.challenger == other.challenger \
               and self.challengee == other.challengee


class Duel:
    """
    This class represents a duel between two gunslingers. Both gunslingers
    must be ready before the duel can begin. To kill their opponent, a
    gunslinger must draw and fire their gun. The first gunslinger to fire their
    gun will win the duel, and the other gunslinger will die.

    Attributes
    ==========

    gunslinger1:
        One of the gunslingers engaged in the duel
    gunslinger2:
        The other gunslinger engaged in the duel
    channel:
        The discord.channel.TextChannel that is being used to play the game
    ready:
        True if both gunslingers are ready, or False otherwise
    active:
        True if the countdown has finished, or False otherwise
    over:
        True if the duel is over, or False otherwise
    """

    def __init__(self, member1: discord.Member,
                 member2: discord.Member,
                 channel: discord.channel.TextChannel):

        self.gunslingers = (Gunslinger(member1), Gunslinger(member2))

        self.channel = channel
        self.ready = False
        self.active = False
        self.over = False

    async def ready_up_gunslinger(self, member: discord.Member) -> None:
        """
        Makes the gunslinger associated with 'member' ready to
        duel.

        :param member: the discord.Member object associated with the gunslinger
                       to be readied
        """
        gunslinger = self._get_gunslinger(member)
        if gunslinger is not None:
            gunslinger.ready_up()
            await self._try_begin()


    async def _try_begin(self) -> None:
        """
        Attempts to begin the duel and make it active. If both gunslingers are
        ready to duel, then the duel will begin. Otherwise, it will stay
        inactive.
        """

        if (self.gunslingers[0].is_ready()
                and self.gunslingers[1].is_ready()
                and not self.active):

            self.ready = True
            message = "Alright everybody! It seems both parties are ready to " \
                      "duel. May the fastest gunslinger win!"
            await self.channel.send(message)

            await asyncio.sleep(3)
            await self._countdown()
            self.active = True


    def draw(self, member: discord.Member) -> None:
        """
        Makes the gunslinger associated with 'member' draw their gun

        :param member: the discord.Member object associated with the gunslinger
                       to have their gun drawn
        """

        gunslinger = self._get_gunslinger(member)

        if gunslinger is not None and gunslinger.is_alive() and self.active:
            gunslinger.draw()

    def fire(self, member: discord.Member) -> None:
        """
        Makes the gunslinger associated with 'member' fire their gun

         :param member: the discord.Member object associated with the gunslinger
                       to fire their gun
        """

        firing_gunslinger = self._get_gunslinger(member)
        dead_gunslinger = None

        if firing_gunslinger is not None and firing_gunslinger.is_alive():

            firing_gunslinger.fire()

            if firing_gunslinger.has_fired():

                if firing_gunslinger == self.gunslingers[0]:
                    dead_gunslinger = self.gunslingers[1]
                else:
                    dead_gunslinger = self.gunslingers[0]

                dead_gunslinger.die()

                message = "Heavens! " + member.name + " killed " + \
                          dead_gunslinger.get_member().name + "with a shot " + \
                          self._get_killing_method() + "\n \n Well, there " \
                                                       "you have it folks. A gunslinger's duel. \n \n " \
                                                       "Now, c'mon, show's over. There ain't nothin' to " \
                                                       "see here. Get on with your business."

                self.channel.send(message)
                self.ready = False
                self.active = False
                self.over = True

    def _get_killing_method(self) -> str:

        common_methods = ["to the chest.",
                          "straight through the chest.",
                          "right through the chest.",
                          "right through the stomach.",
                          "straight through the stomach.",
                          "to the stomach."]

        uncommon_methods = ["straight through the head.",
                            "right through the head.",
                            "to the head."]

        rare_methods = ["straight through the heart.",
                        "right through the heart.",
                        "to the heart.",
                        "straight through the eye!",
                        "right through the eye!",
                        "to the eye!"
                        "right between the eyes.",
                        "straight through the forehead.",
                        "to the forehead.",
                        "right through the forehead.",
                        "straight through the neck!",
                        "through the nose."]

        result = random.randint(0, 100)

        if result <= 60:
            return common_methods[random.randint(0, len(common_methods) - 1)]
        elif result <= 90:
            return uncommon_methods[
                random.randint(0, len(uncommon_methods) - 1)]
        else:
            return rare_methods[random.randint(0, len(rare_methods) - 1)]

    async def _countdown(self):

        await self.channel.send("Three!")
        await asyncio.sleep(1)
        await self.channel.send("Two!")
        await asyncio.sleep(1)
        await self.channel.send("One!")
        await asyncio.sleep(1)
        await self.channel.send("Draw!")

    def _get_gunslinger(self, member: discord.Member) -> Gunslinger:
        """
        Returns the gunslinger associated with 'member'.

        :param member: the discord.Member object associated with the gunslinger
                       to be retrieved
        """

        if self.gunslingers[0].is_member(member):
            return self.gunslingers[0]
        elif self.gunslingers[1].is_member(member):
            return self.gunslingers[1]

    def get_members(self) -> Tuple[discord.Member, discord.Member]:
        """
        Returns a tuple of the two members that control the gunslingers in the
        duel

        :return: A tuple of the two members that control the gunslingers in the
        duel
        """

        return (self.gunslingers[0].get_member(),
                self.gunslingers[1].get_member())

    def is_over(self) -> bool:
        """
        Indicates whether or not the duel is over
        :return: True if the duel is over, or False otherwise.
        """
        return self.over
