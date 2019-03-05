'''
Should handle everything battle related: monsters, parties, and the battle system itself.

Plans:

Single player battle:
    There is no timer. Just pure turn based.

Multiple players:
    Quite a bit more hectic. There will be a timer, potentially settable by the party leader.
    You must send your attack instruction within the time limit. Those that idle will be targeted, and take
    double damage, with some text like "[Player_name] is standing completely still! They are an easy pick for
    [monster_name]. I think I'll turn it off by default. This is only really a necessity when playing with 4+ players.

    The attack instruction will also come with an optional argument, a priority. Attacks with higher priority
    will be executed first. This allows for some strategy and communication.


There seems to be a weird thing that happens when a party leader tries to leave the party whilst other members are in battle.
My code just vomits error messages, but it seems like the invariants have been somehow magically kept.

This will definitely somehow change in the future, as party leaders can be potentially infinitely stalled and prevented from progressing and starting
any more battles, as they cannot leave their own party.
'''

from core import item, client, super_important_token, text_channel

#WELCOME TO PYTHON WHERE ONE DOES NOT SIMPLY COPY INSTANCES OF CLASSES
from copy import deepcopy

import asyncio
import random
import player
import world
from monster import *
#Planned abilities
#Change fight delay
#can only fight when everyone is at the same room

#Battle abilities:
#Flee, leave battle
#Use a skill
#Die

#Usage of invite commands
#!invite <player>
#e.g. !invite @TheEpicCowOfLife#1094
#just use discord autocomplete

#Phases:
#Begin turn:
#Await commands from everyone
#Players can flee at this time.


#Calculate damage
#Players attack first.

#Two skills, normal attack, deals 1x damage
#Then, there's shove, dealing 0.7x damage, but causes the next attack in the same turn to deal 1.5x damage

#Monsters then attack multiple members of the party at once.

#When monster ded, the loot gets split up. You can loot, discard or drop. It will stay in your spare slot until then.



class party:
    def __init__(self, id):

        #List of all the id's of members in the party
        self.members = [id]
        
        #Id of the leader
        self.leader = id

        #Delay.
        self.delay = -1

        #list of people who requested to join
        self.requests = []

        self.require_request = True
        
        #All the alive members currently battling.
        #This is the array we care about.
        #One may leave this array by fleeing the battle, or dying.
        self.alive = []
        
        #The current turn.
        self.turn = 0

        #Whether or not that party is battling a monster.
        self.in_battle = False

        #A personal copy of the monster to slaughter.
        self.m = ""

        #A dictionary of tuples.
        #The key is the member id, and its values are the attacks along with the priority
        self.attacks = {

        }
        
        #The number of attacks sent in. Will continue the turn once this reaches the number of battling members
        self.attack_num = 0

        #This is true if the battle is accepting attacks
        self.accept_attack = False

    #prints all the members of the party.
    async def print_info(self,channel, id,name):
        outstr = "<@%s>```%s is in the party lead by %s. \n\nHere are the members:" % (id,name,player.char_dict[self.leader].name)
        for person in self.members:
            outstr += "\n\n%s" % player.char_dict[person].name
        await client.send_message(channel,outstr + "```")

    #prints out all the requests to join the party
    async def print_req(self, channel, id, name):
        outstr = "<@%s>```Here are the requests to join the party lead by %s: \n\n" % (id,name)
        for person in self.requests:
            outstr += "\n\n%s" % player.char_dict[person].name
        await client.send_message(channel,outstr + "```")
    
    #Returns if all the party members are in the same room, and prints out the members that are not.
    async def is_same_room(self, channel, room):
        
        members_outside_room = []
        flag = True
        for person in self.members:
            if player.char_dict[person].room != room:
                members_outside_room.append(player.char_dict[person].name)
                flag = False

        if not flag:
            outstr = "<@%s>```Error! The following members are not in the same area:\n" %self.leader
            for mem in members_outside_room:
                outstr += "\n%s" % mem
            await client.send_message(channel, outstr + "```")

        return flag

    #Sets everything in motion and initiates the battle
    #must be leader to use this
    async def init_battle(self, channel):
        room = player.char_dict[self.leader].room
        #Check if there even is a fight to begin with
        if not world.rl[room].has_fight:
            await client.send_message(channel, "<@%s>```Error! There isn't a fight here```" % self.leader)
            return
        #Check if it isn't already in battle
        if self.in_battle:
            await client.send_message(channel, "<@%s>```Error! Your party is already in battle!```" % self.leader)
            return
        #Check if everyone is on the same page, about to fight the monster...
        #(is_same_room prints an error if not)
        if not await  self.is_same_room(channel,room):
            return
        
        #No more errors to catch? WE'RE READY TO RUMBLE!!!!!!!!!!11
        self.in_battle = True
        
        #Mark everyone as alive.
        self.alive = deepcopy(self.members)


        
        #Remove requests from everyone so they don't randomly join parties mid-battle.
        #Also heal everyone, because I said so and I like my game to be like that.
        #Still bothers me how this is O(n^2)
        #Maybe if we get parties of 1000 members this entire module will be reworked.

        for mem in self.members:
            player.char_dict[mem].cur_hp = player.char_dict[mem].hp_s 
            if len(player.char_dict[mem].preq) > 0:
                remove_request(mem)

        #Clone a monster to fight.

        mid = world.rl[room].mid
        print("Mid: %s, room: %d" % (mid,room)) #WTF? I need this line otherwise it won't work? Python!??????
        self.m = deepcopy(md[mid])
        self.turn = 1
        
        #Tell everyone that the battle is about to start with maybe some help...
        await client.send_message(channel, "<@%s>```%s's party is about to go into battle... type '!help battle' in order to learn about commands you can use to fight monsters!```" %(self.leader, player.char_dict[self.leader].name))

        #LET THE GAMES BEGIN!!!!!!!!!!!!
        await self.player_turn(1,channel)

    
    #Note: If a player leaves the party while battling, make sure to 

    async def player_turn(self, turn, channel):
        #Clears the dictionary, make room!
        self.attacks.clear()
        self.attack_num = 0

        #Send in your attacks! Go wild!
        self.accept_attack = True
        await client.send_message(channel, "```It is now %s's party's turn to send in their attacks!!!!```" % player.char_dict[self.leader].name)
        if self.delay > 0:
            #If there is an automatic delay set, then wait for that.
            #It also uses its self.turn property to make sure that the next turn hasn't already been executed
            await asyncio.sleep(self.delay)
            if turn != self.turn:
                return
            await self.monster_turn(turn,channel)

    #Itis meant to be a guarantee that skill is either an item, or a skill   
    async def add_attack(self,id,priority,skill, channel):
        #So many checks....
        if not self.in_battle:
            await client.send_message(channel, "<@%s>```Error! Your party isn't in battle!```" % id)
            return
        if id not in self.alive:
            await client.send_message(channel, "<@%s>```Error! You are not currently fighting with your party!```" % id)
            return
        if not self.accept_attack:
            await client.send_message(channel, "<@%s>```Error! You may not attack now!```" % id)
            return
        if id in self.attacks:
            await client.send_message(channel, "<@%s>```Error! You have already sent in your attack!```" %id)
            return

        #Increment the number of attacks
        self.attack_num += 1
        
        self.attacks[id] = (priority, skill, id)
        
        #Continue to the monster turn if and only if everyone has sent in an attack.
        if self.attack_num == len(self.alive):
            await self.monster_turn(self.turn,channel)
        
    async def monster_turn(self,turn,channel):
        #Calculate damage taken by monster and if it died, player damage, and check if people died.
        #Incrememnt the turn to make sure this function doesn't get called twice when it is meant to be called once.
        self.turn += 1
        self.accept_attack = False

        #list of attacks
        alist = []
        for key in self.attacks:
            alist.append(self.attacks[key])
    
        #Sorting by priority, thanks stack overflow for this. Python is weird.
        alist.sort(key = lambda tup : tup[0], reverse = True)

        #UNLEASHHH THE ATTACKSSS
        for att in alist:
            print(att[1])
            #att[1] is skill
            id = att[2]
            stat = player.char_dict[id].att
            r = player.char_dict[id].att_r
            #calculate the damage based on the character's stats
            damage = random.randint(stat-r,stat+r)

            await self.m.receive_attack(id,att[1],damage,channel)
            print (self.m.hp)
            if self.m.hp <= 0:
                self.in_battle = False
                await self.battle_end(True,channel)
                return
        
        #If we got to here, then the monster has enough juice left to launch some attacks
        #Here, I want to introduce the following rule: "A cornered fox is more dangerous than a wolf"
        #For every player fighting the mob, it has increased 15% attack.
        #However, damage is distributed evenly between player, so what ends up happening is that the damage
        #you take asymptotes to 15%

        #monster damage
        m_d = (1 + 0.15 * (len(self.alive)-1)) * self.m.att / float(len(self.alive))

        #sprinkle in some variability
        m_d += random.uniform(-self.m.att_range, self.m.att_range) * m_d

        #aaaanddd clamp to int
        m_d = int(m_d)

        await client.send_message(channel,"```%s is dealing %d damage to everyone in %s's party!```" % (self.m.name, m_d, player.char_dict[self.leader].name))
        
        #Check if everyone survived that devastating blow
        for mem in self.alive:
            player.char_dict[mem].cur_hp -= m_d
            if player.char_dict[mem].cur_hp <= 0:
                #Well, that character died, lets let them know.
                await client.send_message(channel,"<@%s>```%s has succumbed to their wounds, and left the battle to rest and recover their hp.```" % (mem,player.char_dict[mem].name))
                
                #lets casually refill their hp and...
                player.char_dict[mem].cur_hp = player.char_dict[mem].hp_s
                
                #begone
                self.alive.remove(mem)
        
        if len(self.alive) == 0:
            #good job, you all died.
            await client.send_message(channel,"```Unfortunately, everyone is now dead in %s's party.```" % player.char_dict[self.leader].name)
            await self.battle_end(False,channel)
            return

        
        self.m.decrement_stacks()

        #I hope we don't get infinite loops
        await self.player_turn(self.turn,channel)

    #Remove yourself from battle, or return to previous room.
    #Check: If accept_attack, make sure that leaving the room will not cause the game to infinitely stall
    async def flee(self,id, channel):
        if self.in_battle:
            self.alive.remove(id)
            await client.send_message(channel, "<@%s>```You have successfully fled the battle```" % id)
            #Everyone has fled. Whoops. Gotta end the battle
            if len(self.alive) == 0:
                print("Battle ended, everyone left :(") #Debugging sanity check
                await self.battle_end(False,channel)
                return
            
            if self.accept_attack:
                #If the member flees, we may not ever see this condition get checked and succeeded, and the battle may halt.
                if self.attack_num == len(self.alive):
                    await self.monster_turn(self.turn,channel)
                    return
            
        else:
            #Oh, so in this case, we need to move the player back to a previous room. We got a function to handle that
            await player.char_dict[id].go_back(channel)
            return
        pass

    #function gets called when battle ends to reset the party and every invariant.
    #has_won is true when party members manage to beat the monster.
    async def battle_end(self,has_won,channel):
        self.in_battle = False
        
        
        if has_won:
            
            await client.send_message(channel,"```Congratulations! The battle has been won! Everyone %s's party gains %d xp!\nIf you couldn't already, everyone alive at the end of this battle can proceed deeper into the cave.```"% (player.char_dict[self.leader].name, self.m.xp_drop))
            
            #Makes sure that players can proceed.
            room = player.char_dict[self.leader].room
            for mem in self.alive:
                if mem not in world.rl[room].players_fought:
                    print("put %s in room %d" % (self.leader, room))
                    world.rl[room].players_fought[mem] = True

                
            #Hook everyone on the sweet feeling of euphoria of gaining xp and levelling up
            await asyncio.wait([player.char_dict[mem].inc_xp(self.m.xp_drop,channel) for mem in self.alive])

            #Make everyone alive pick up the sweet loot
            await asyncio.wait([player.char_dict[mem].pick_up_item(deepcopy(self.m.drop),channel) for mem in self.alive])
   
   
        #Clear the alive list to make sure not everyone is still listed as in battle
        self.alive.clear()









######################################################
#And below are some functions that operate on parties#
######################################################








    

pd = {} #party dictionary: List of parties
#The key is just the id of the leader of the party. This invariant is supposed to make everything easy, but makes everything a pain.

#arguments are the id's of the promoter, promotee, and the message channel.
async def promote(pmter, pmtee, channel):
    if pd[pmter].in_battle:
        await client.send_message(channel, "<@%s>```Error! You cannot promote someone awhile you are mid-battle!```" % pmter)
        return

    if (pd[pmter].leader != pmter):
        await client.send_message(channel, "<@%s>```Error! You cannot promote someone as you are not the leader of your own party.```" % pmter)
        return 
    
    if (pmtee not in pd[pmter].members):
        await client.send_message(channel, "<@%s>```Error! Could not find %s in your party.```" % (pmter,player.char_dict[pmtee].name))
        return

    pd[pmter].leader = pmtee
    pd[pmtee] = deepcopy(pd[pmter])
    #del pd[pmter] //Actually, this line will cause the whole thing to bug out if you promote yourself. Leaving the dummy parties behind is just fine.

    for mem in pd[pmtee].members:
        #Update everyone's pid to be mem.
        player.char_dict[mem].pid = pmtee

    for mem in pd[pmtee].requests:
        #Update's everyone's preq. So many invariants to maintain just for this party system...
        player.char_dict[mem].preq = pmtee
    
    await client.send_message(channel, "<@%s>```Successfully promoted %s to party leader.```" % (pmter,player.char_dict[pmtee].name))
    
#Takes in an Id, and makes that person leave.
#Also use this to kick people from a party.
#is_joining_new is called if you are about to join a new party.
async def leave_party(id, channel, is_joining_new):
    
    
    user_p = player.char_dict[id].pid

    if id in pd[user_p].alive:
        await client.send_message(channel,"<@%s>```Error! You are currently in battle! You must flee first!```" % id)
        return
    if (len(pd[id].members) == 1):
        if (is_joining_new):
            await client.send_message(channel,"<@%s>```You have successfully left your own party.```" % id)
            return
        #Error! You can't leave a party of just yourself, unless you're about to join another party.
        await client.send_message(channel,"<@%s>```Error! You cannot leave a party consisting of just yourself!```" % id)
        return
    
    if  user_p == id:
        #You are the leader of your party.
        for mem in pd[user_p].members:
            if mem != id:
                #Mem is now the randomly chosen person to become leader.
                await promote(id,mem,channel)
                
                pd[mem].members.remove(id)
                player.char_dict[id].pid = id
                pd[id] = party(id)

                await client.send_message(channel,"<@%s>```You have successfully left the party, and have made %s to be the leader in your absence.```" % (id, player.char_dict[mem].name))
                return
                    #hooo boy that was a long line code
        print("wtf this aint meant to get to here. some invariants have been broken")
        return

    #The last case: you simply leave the party.

    pd[user_p].members.remove(id)
    player.char_dict[id].pid = id
    pd[id] = party(id)
    await client.send_message(channel,"<@%s>```You have successfully left the party.```" % id)
    return

#Actually moves player id to join party pid
async def join(id, pid, channel):
    #Makes sure the player isn't two timing.
    await leave_party(id,channel, True)

    #The person has a new party id, so let's change that.
    player.char_dict[id].pid = pid

    #The person isn't requesting to join a party anymore so lets change that.
    player.char_dict[id].preq = ""

    #Lets make it official by adding it to the party
    pd[pid].members.append(id)
    await client.send_message(channel,"<@%s>```You have sucessfully joined %s's party```"%(id, player.char_dict[pid].name))

#Removes a request from the user's requested party. A necessary step to make sure we don't have multiple requests everywhere.
def remove_request(id):
    pid = player.char_dict[id].preq
    pd[pid].requests.remove(id)
    player.char_dict[id].preq = ""

#Requests to join party pid
async def req_join(id,pid,channel):
    #Wait a second... you're already in the party you're trying to request to join!
    if player.char_dict[id].pid == pid:
        await client.send_message(channel,"<@%s>```Error! You can't request to join your own party!```" % id)
        return

    if pd[pid].require_request:
        #Maintain preq invariant....
        if len(player.char_dict[id].preq) != 0:
            remove_request(id)
        
        pd[pid].requests.append(id)
        player.char_dict[id].preq = pid

        await client.send_message(channel,"<@%s>```You have sucessfully requested to join %s's party```"%( id, player.char_dict[pid].name))
    else:
        if len(player.char_dict[id].preq) != 0:
            remove_request(id)
        await join(id,pid,channel)
    
    

#accept player invitations
#id is the player to accept
#pid is the party to move the player into
async def accept(id, pid, channel):
    for i,mem in enumerate(pd[pid].requests):
        if mem == id:
            await join(id,pid,channel)
            await client.send_message(channel, "<@%s>```Successfully accepted %s to join your party```" % (pid,player.char_dict[id].name))
            
            del pd[pid].requests[i]
            return
    await client.send_message(channel, "<@%s>```Sorry, it appears that %s has not requested to join your party```" % (pid, player.char_dict[id].name))
    pass

#Attempts to decline the request from id.
async def decline(id,pid,channel):
    if id not in pd[pid].requests:
        await client.send_message(channel, "<@%s>```Error! Could not find %s requesting to join your party.```" % (pid,player.char_dict[id].name))
        return
    remove_request(id)
    await client.send_message(channel, "<@%s>```Successfully declined %s's request```" % (pid,player.char_dict[id].name))

