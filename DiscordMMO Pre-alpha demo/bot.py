'''
Is the python file to run in order to run the bot.

Handles all the bot logic, what it does when it receives a message, and calls all the functions to make things tick.
This module is a little bit like the master switch-puller of the entire program.

Refer to core.py for instructions to get this bot working on your computer.
'''

from core import client, text_channel, super_important_token


import player
import world
import battle
import monster
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


welcomestr = "Type !start to start the game!"
#Offloaded all the help strings to a different file
from helpstrings import *

@client.event
async def on_member_join(member):
    server = member.server.get_channel(text_channel)
    await client.send_message(server, "Welcome, @" + member.name + ". " + welcomestr)

@client.event
async def on_message(message):
    #Makes sure that it ignores all messages coming from itself. We do not want accidental fork bombs.
    if message.author == client.user:
        return

    mstr = message.content #a string containing the message's content
    usr = message.author #some weird user object which is the message's author
    #it seems to have a property called "id" which is a really useful totally unique
    #identifier for each user.

    mstr = mstr.lower()

    #Just a few 'macros'
    #Sends a message.
    async def msg(text):
        await client.send_message(message.channel, text)
    
    #Checks if the user sending the message has started the game
    async def is_created():
        if player.character_exists(usr.id):
            return True
        else:
            await msg("It seems like you haven't created a character yet. Start your adventure by typing '!start'.")
            return False

    #Checks if the player id has started the game. These functions send error messages.
    async def player_exists(id):
        if player.character_exists(id):
            return True
        else:
            await msg("Error! The player you mentioned has not created a character yet!")
            return False
    #Echoes whatever is sent just for debugging purposes.
    
    #await msg(mstr)
    #print(mstr)

    #Sanity checkers, making sure these commands work
    if mstr.startswith("good bot"):
        await msg("*purrrrrrrs :3")


    elif mstr.startswith("bad bot"):
        await msg("*sulks :(")


    #implement some more detailed instructions for each individual function.
    elif mstr.startswith("!help"):
        if len(mstr) <= 6:
            await msg(helpstr)
        else:
            if mstr.startswith("!help item"):
                await msg(item_help_str)

            elif mstr.startswith("!help room"):
                await msg(room_help_str)

            elif mstr.startswith("!help party"):
                await msg(party_help_str)

            elif mstr.startswith("!help battle"):
                await msg(battle_help_str)

    #Get everything initiated for new players
    elif mstr.startswith("!start"):
        
        if player.character_exists(usr.id):
            await msg("Whoops! It looks like you already have have a character. If you would like to restart completely from scratch, type '!reset'.")
        else:
            player.create_character(usr.id, usr.name)
            battle.pd[usr.id] = battle.party(usr.id)

            await msg("<@%s>```Successfully created your new character! You can view a list of commands with !help```" % usr.id)
            await player.char_dict[usr.id].show_room(message.channel)
            #await player.hax(usr.id,message.channel)    
        

    #view your stats.
    #Potential feature: view other people's stats
    elif mstr.startswith("!stats"):
        if (await is_created()):
            await msg(player.view_stats(usr.id, usr.name))


    #Give yourself 100 xp, for debugging    
    elif mstr.startswith("!hax"):
        if (await is_created()):
            await player.hax(usr.id,message.channel)    
    

    #reset character to defaults... Definitely need some "are you sure" prompts.
    elif mstr.startswith("!reset"):
        await msg("Haha, you're stuck with your character, cause I haven't implemented reset yet! >:D")


    #usage: !pick up [item_name]
    #Searches for [item_name] in the room the player is in, and picks one up if it can find one.
    elif mstr.startswith("!pick up"):
        if (await is_created()):
            item_name = mstr[9:]
            item_name = item_name.lower()
            await player.pick_up_item_request(usr.id,message.channel,item_name)


    #usage: !drop [item_name]
    #Searches for [item_name] in the player's inventory, and then drops it into the world.
    elif mstr.startswith("!drop"):
        if (await is_created()):
            item_name = mstr[6:]
            print("Searching for: %s" % item_name)
            item_name = item_name.lower()
            await player.char_dict[usr.id].drop_item(item_name,message.channel)


    #Lists everything in inventory
    elif mstr.startswith("!inven"):
        if (await is_created()):
            await player.char_dict[usr.id].view_inventory(message.channel)


    #Lists every item in the room
    elif mstr.startswith("!list item"):
        if (await is_created()):
            await world.rl[player.getroom(usr.id)].list_items(message.channel)
    

    #Shows the current state of the room, and the rooms you can go to.
    elif mstr.startswith("!list room"):
        if (await is_created()):
            await player.char_dict[usr.id].show_room(message.channel)
    

    #Usage: !goto [room_id/room_name]
    #Attempts to go to room 
    elif mstr.startswith("!goto"):
        if (await is_created()):
            if usr.id in battle.pd[player.char_dict[usr.id].pid].alive:
                await msg("<@%s>```Error! You cannot move rooms while in battle!```" % usr.id)
                return
            await player.char_dict[usr.id].goto_room(message.channel,mstr[6:])

    ###################################################################
    #For party commands, please remember to make sure to check whether or not the person mentioned actually exists.
    #Also documentation exists in helpstr.py
    elif mstr.startswith("!party list members"):
        if (await is_created()):
            await battle.pd[player.char_dict[usr.id].pid].print_info(message.channel,usr.id,usr.name)
    
    elif mstr.startswith("!party list request"):
        if (await is_created()):
            await battle.pd[player.char_dict[usr.id].pid].print_req(message.channel,usr.id,usr.name)

            
    
    elif mstr.startswith("!party leave"):
        if (await is_created()):
            await battle.leave_party(usr.id,message.channel,False)
    
    elif mstr.startswith("!party join"):
        if await is_created():
            mention = mstr[12:]
            id = mention[2:-1]

            #Bots see mentions like @TheEpicCowOfLife#0123 as <@0239123412093120> or some gibberish number, which functions as the ID
            #This code is just fishing the id out of the string.

            if await player_exists(id):
                await battle.req_join(usr.id,player.char_dict[id].pid,message.channel)
                
        #print("%s %s %s" % (id, mention, mstr))

    elif mstr.startswith("!party accept"):
        if await is_created():
            mention = mstr[14:]
            id = mention[2:-1]
            if await player_exists(id):
                if player.char_dict[usr.id].pid == usr.id:
                    await battle.accept(id,usr.id,message.channel)
                    
                else:
                    msg("<@%s>```Error! You must be the party leader to accept requests```" % usr.id)

    elif mstr.startswith("!party decline"):
        if await is_created():
            mention = mstr[15:]
            id = mention[2:-1]
            if await player_exists(id):
                if player.char_dict[usr.id].pid == usr.id:
                    await battle.decline(id,usr.id,message.channel)
                else:
                    await msg("<@%s>```Error! You must be the party leader to decline invitations```" % usr.id)
    
    elif mstr.startswith("!party kick"):
        if await is_created():
            mention = mstr[12:]
            id = mention[2:-1]
            if await player_exists(id):
                if player.char_dict[usr.id].pid == usr.id:
                    await msg("<@%s>```You have been kicked out of %s's party```" % (id,player.pd[usr.id].name))
                    await battle.leave_party(id,message.channel,False)
                    
                else:
                    await msg("<@%s>```Error! You must be the party leader to kick players```" % usr.id)

    elif mstr.startswith("!party promote"):
        if await is_created():
            mention = mstr[15:]
            id = mention[2:-1]
            if await player_exists(id):
                if player.char_dict[usr.id].pid == usr.id:
                    await battle.promote(usr.id, id, message.channel)
                else:
                    await msg("<@%s>```Error! You must be the party leader to promote players```" % usr.id)
    
    #################
    #Battle commands#
    #################

    #dear lord... initiate a fight
    #This innoculous function initiates sooooo much more
    elif mstr.startswith("!fight"):
        if await is_created():
            if player.char_dict[usr.id].pid == usr.id:
                await battle.pd[usr.id].init_battle(message.channel)
            else:
                await msg("<@%s>```Error! You must be the party leader to initiate fights```" % usr.id)
    
    #Run away.
    elif mstr.startswith("!flee"):
        if await is_created():
            pid = player.char_dict[usr.id].pid
            await battle.pd[pid].flee(usr.id,message.channel)


    #Use a skill! More coming soon
    elif mstr.startswith("!use"):
        if await is_created():
            #Only skills without any whitespace are planned.
            arg = mstr[5:]
            a = arg.split(" ")


            priority = 0
            if len(a) > 1:
                try:
                    priority = int(a[-1])
                    skill = " ".join(a[:-1])
                except:
                    #await msg("<@%s>```Warning! You have not submitted a valid integer for your priority. Defaulting to 0```" % usr.id)
                    skill = " ".join(a)
            else:
                skill = " ".join(a)            
            #Ok, so checks related to items are just so much easier to do here.
            #These just guarantee that the item actually exists, and the user can drop it.
            
            
            if skill not in monster.sd:
                #it is not a skill
                if player.char_dict[usr.id].item_exists(skill):
                    #Well, looks like the item exists in the user's inventory
                    await battle.pd[player.char_dict[usr.id].pid].add_attack(usr.id,priority,skill,message.channel)
                    pass

                else:
                    await msg("<@%s>```Error! %s is not a valid skill, and it is not a consumable item in your inventory```" % (usr.id,skill))
                    return
            
            else:
                #We know it is a skill, then
                await battle.pd[player.char_dict[usr.id].pid].add_attack(usr.id,priority,skill,message.channel)


#################################
client.run(super_important_token)
#################################

#PRAISE THE HOLY LINE THAT MAKES EVERYTHING TICK

