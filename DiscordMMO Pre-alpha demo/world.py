'''
Handles all the logic for every room

So basically, each room has two important booleans, whether or not it has a monster to fight,
and whether or not that monster must be deleted at least once in order to proceed further.

Once a player defeats the monster in a required fight, the room "remembers" the player using the
players_fought dictionary.

What state the player is in will also change the flavour text of the room.

The flavour text, what monsters are in it, what the initial state of each room is, will be stored in this module,
under the rl array, standing for "room_list".

This module also includes the template instances of items under il, which will basically be copied all over the world, and into player's
inventories.

'''

from copy import deepcopy
from core import item, client

class room:
    def __init__(self,id):
        #go away python bugs. Iti s just a simple unique id for each room to stop python from
        #linking different instances of classes.
        self.id = id

        #name of room.
        self.name = ""

        #Description as you are in the room, but you haven't fought the monster yet
        self.fight_txt = ""

        #Description as you are in the room, with no monsters required to fight.
        self.peace_txt = ""

        #Description if you attempt to move forward before slaying the monster.
        self.fight_error = ""

        #Description of this room as seen when you list the room.
        self.desc = ""

        #The rooms it links to
        self.links = []
        
        #The items in the room
        self.items = []

        #The monster ID of the monster to fight.
        self.mid = ""

        #True if there even exists a fight in this room.
        self.has_fight = False

        #True if a fight is needed in order to progress.
        self.requires_fight = False

        #Dictionary of players who fought the monsters and can progress.
        self.players_fought = {

        }

    #Takes in the lower case of the item, and searches for it.
    #Returns the item if found, removes it from the world, else it returns an item with an empty variable.
    def search_item(self,name):
        for i, t_item in enumerate(self.items):
            if (t_item.name.lower() == name):
                del self.items[i]
                return t_item      
        return item(empty = True)      
    
    #Lists all the items in the room    
    async def list_items(self,channel):
        outstr = "```Items in %s\n\n" % self.name
        for item in self.items:
            outstr += "%s:\n    %s\n\n" % (item.name, item.desc)
        
        await client.send_message(channel, outstr + "You may pick up these items by using !pick up [item name] , e.g. !pick up sTiCk (case insensitive)```")

    #Shows all the information when you do !list room
    async def print_room(self, channel, id, name):
        if (not self.requires_fight or (id in self.players_fought)):
            outstr = "```%s is in: %s\n\n%s\n\nYou may go to the following places using the command !goto:\n\n" % (name, self.name, self.peace_txt)
            for i in self.links:
                outstr += "%d: %s\n    %s\n\n" % (i, rl[i].name, rl[i].desc)
        else:
            outstr = "```%s is in: %s\n\n%s\n\n" % (name, self.name, self.fight_txt)
            outstr += "Again, you may either '!fight', or '!flee'."        
        
        await client.send_message(channel, outstr + "```")

    #Returns whether a character id is able to proceed
    def can_proceed(self,id):
        if self.requires_fight and (id not in self.players_fought):
            return False
        return True


    def find_room(self, name):
        for i in self.links:
            if rl[i].name.lower() == name:
                return i
        
        return -1

#Below, is all the data.

#itemlist, a misnomer.
il = {   

}
il["stick"] = item(name = "Stick", desc = "It's just a big stick. You may like to hit things with it. Increases atk by 3, though it doesn't do anything for you at the moment since equipping items haven't been implemented yet.", str_add = 10, empty = False)

il["pants"] = item(name = "Pants",
 desc = "These don't exactly offer very much protection, but at least you won't be running around naked now, though, equipping items hasn't been implemented yet. Increases HP by 5", 
 hp_add = 5)

il["soothing gel"] = item(name = "Soothing Gel",
 desc = "This gel feels really good when you rub it on wounds by using '!use soothing gel' in battle. Heals you for 25 hp.",
  heal = 25,
  usable = True)

il["bat leather"] = item(name = "Bat Leather", 
desc = "This leather is extremely light, yet it astounds you how tough it is to rip apart. Perhaps you may someday incorporate it into armour.")

il["dwarven tonic"] = item(name = "Dwarven Tonic",
desc = "This small vial contains a strange, blood-red liquid with a pungent medicinal smell. What could go wrong if you tested it wounded while battling? Heals you for 60 hp",
heal = 60,
usable = True
)

il["win note"] = item(name = "YoU'rE WiNeR",
desc = "http://bitly.com/98K8eH")


rl = []
#roomlist
for i in range(5):
    rl.append(room(i))

rl[0].peace_txt = ("Before you stands the gaping entrace to massive cave system, rumoured to be home to horrors unimaginable. "
    "You will be greeted with this screen again if you type '!show rooms'. "
    "If you wish to see the items before you in any place, type !list items. "
    "\n\nBelow are the rooms that you may visit. You can reach them by typing !goto [room_name] (case insensitive).")

rl[0].desc = ("This is just outside the entrance to the cave, where you started your adventure.")

rl[0].name = "Cave Entrance"

rl[0].items.append(deepcopy(il["stick"]))
rl[0].items.append(deepcopy(il["pants"]))
rl[0].items.append(deepcopy(il["stick"]))
rl[0].items.append(deepcopy(il["stick"]))
rl[0].items.append(deepcopy(il["pants"]))

rl[0].links.append(1)

rl[1].name = ("Slime Chamber")

rl[1].mid = "slime"

rl[1].fight_txt = ("As you step inside, you are greeted with a cool, dimly lit chamber. Moisture drips from the stalactites, "
"coalescing into some sort of slimy being! It seems to be fully sentient, yet it seems to be locked in a state of incredible agony."
"As it writhes and spazzes on the cave floor, you decide that ending its miserable life using '!fight' can improve your fighting ability, "
"yet a part of you wishes to '!flee', as that slime very well could've once been an adventurer like you."
)

rl[1].requires_fight = True
rl[1].has_fight = True
rl[1].fight_error = ("As you attempt to advance further, the suicidal slime nibbles at your feet, begging to die. You can't possibly leave it behind. "
"Type '!fight' to euthanise it, or taunt it by leaving the cave by typing '!flee'")

rl[1].peace_txt = ("You notice more slimy beings forming in the corner of the cave. "
"You can still choose to refight some to gain xp using '!fight', or you may progress, using '!list rooms', and '!goto'. "
"Remember you can type '!help' if you're not sure how to use these commands.")

rl[1].desc = ("This is the outermost chamber of the cave system.")

rl[1].links.append(0)
rl[1].links.append(2)
rl[1].links.append(3)
for i  in range(3):
    rl[1].items.append(deepcopy(il["soothing gel"]))


rl[2].name = "Bat Roost"
rl[2].desc = "You can hear from outside the feverish squeaking and flapping of thousands of bats inside."

rl[2].requires_fight = False
rl[2].has_fight = True
rl[2].mid=  "bat"

rl[2].peace_txt = ("You tread cautiously around the walls of the chamber, but this seems to yield no further openings. "
"However, what really catches your attention are several humungous bats stationed around the centre of the chamber where countless bats swarm, guarding some "
"sort of nest. Perhaps, you may like to tease one or two of these bats and battle them with !fight, honing your fighting skills...")

rl[2].links.append(1)


rl[3].name = "Guards' Hallway"
rl[3].desc = "This tunnel appears to eventually open up into a wider hallway... Perhaps there could be something of interest if you keep going far enough"

rl[3].requires_fight = True
rl[3].has_fight = True
rl[3].mid = "guard"

rl[3].fight_txt = ("Just as you expected, this tunnel expands into a hallway with massive, decorated stone pillars "
"stretching towards the ceiling. Suddenly, a rather short, almost humanoid creature appears in your path, effortlessly wielding a spear "
"made of metal and stone. He (you can tell by its rope-like beard) then abruptly performs a flurry of slashes, too fast for you to track, "
"and before you know it he stops his spear mid-lunge, pointed straight at your chest.\n\n"
"You consider taking the hint by using !flee, but you consider that whatever is at the end of the hallway must be worthwhile if it takes a highly skilled "
"guard to train, but you know you cannot win this fight alone. Perhaps you might consider forming a party. You can learn to do that using !help party")

rl[3].fight_error = ("You try to step forward. The Dwarf Warrior won't have any of that.")
rl[3].peace_txt = ("With the guard out of the way, you can proceed and find what's at the end of the hallway. You can also choose to relive your experiences and somehow acquire some more dwarven tonics using !fight.")

rl[3].links = [2,4]


rl[4].name = "Dwarf King's Throne"
rl[4].desc = "The end of the hallway isn't a massive wall, it's a door! What riches could possibly lie behind it?"

rl[4].fight_txt = ("The doors, despite their enormous weight, glide open effortlessly. Mountains of gold and gem glisten in the corners, as a "
"very unamused dwarf sits unamused on a lavish throne. He is clearly not very happy that you murdered one of his guards and barged straight into his "
"bedroom. Nevertheless, he pushes some button somewhere on his arm rest, and his throne roars into life, with blades and maces swinging everywhere! "
"The king seems more alive like ever! He is clearly enjoying piloting the throne! \n\n"
"You can accept his challenge with !fight, or you can run away and gather support with !flee.")

rl[4].fight_error = ("You can't go anywhere else! Don't leave the dwarf king hanging!")

rl[4].peace_txt = (    
    "Uhm, congratulations, if you killed the thing that dropped this note, "
    "you've pretty much experienced the extent of this project's content. "
    "I mean, good job for sticking around for long enough to beat this thing. "
    "Anyways, if you wanna see more content get developed... maybe during the holidays I can muster some "
    "willpower to clean up this code and make it more functional.\n\n"
    "Also, if you really want to, have fun re-fighting the boss using !fight. I am not stopping you")


rl[4].requires_fight = True
rl[4].has_fight = True
rl[4].mid = "king"
rl[4].links = [3]