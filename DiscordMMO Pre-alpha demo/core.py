'''
Stores the things that every single module needs, like the discord client itself, and the basic item class
'''


import discord
import asyncio


'''
OK, so basically, if you want to get my bot to work, you need to follow a couple of steps.
First, make an account on discord, and follow along the first part of the tutorial on 
https://www.devdungeon.com/content/make-discord-bot-python which is what I used.

Then, you need to replace the two lower variables with your own.

The super_important_token is basically the bot token that you create when you follow the above tutorial.

Replacing the text channel with your own is optional, especially if you use the link https://discord.gg/cMCSc8S,
which is the discord server I ran my bot on.

The text_channel can be found in the server you create. If you enable developer mode by clicking on
user settings -> appearance -> enable developer mode (scoll down a bit), and then right click on the text channel
(not the server), you should see an option to "Copy ID". This is the string you want to put in text_channel.

######################################################################################
Finally, to launch the bot, simply run bot.py, and it will set into motion everything.
######################################################################################
'''

#You must replace this with your own token for this to work. I'm not sharing mine.
super_important_token = ''

#This is the text channel you want the bot to run in. Adds a bit of functionality, for new joiners to
#let them know what the heck they're meant to do to start off.
text_channel = ''

client = discord.Client()


#probs will need to split this up into subclasses, items and equips, and maybe resources.
class item:
    def __init__(self,name = "",desc = "", int_add = 0, str_add = 0, dex_add = 0, hp_add = 0, empty = False, heal = 0, usable = False):
        self.name = name
        self.desc = desc

        #Behold, ancient planned features of long past, which I am too lazy to deprecate.
        self.equipable = False
        
        
        self.int_add = int_add
        self.str_add = str_add
        self.dex_add = dex_add
        self.hp_add = hp_add

        #here are the actually useful ones.
        self.usable = usable

        self.heal = heal
        

        self.empty = empty


#(my todo list is below. I need to setup a less rudimentary way to do this)
'''
List of things to do:

balancing Stats, equipping items

Rework item system...

Revamp in how messages are worked, your player moves around discord text channels itself to avoid spam.
'''

'''
Things that are done:

Map and item system

party system!!!

Battle system, and ability to use items!

Player character initialisation

Full demo with flavour text for 5 maps

Communication with bot using commands.

'''
