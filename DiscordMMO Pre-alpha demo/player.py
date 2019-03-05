'''
Basically handles everything related to players, stats, xp, creation and inventory

This is a huge spaghettified mess of me figuring out the best practices in using this discord bot.
'''

from core import client, text_channel, super_important_token, item

#Hehe, just casually importing a world
import world

class character:
    def __init__(self, id, name):
        #Id is a unique identifier for each person.
        self.id = id
        #name is username
        self.name = name

        #pid is the id of the party the character is in
        self.pid = id

        #id of the party the character is currently requesting for.
        self.preq = ""
                
        #current state
        self.xp = 0
        self.lvl = 1
        self.cur_hp = 50
        self.room = 0
        self.last_room = 0

        #behold! All the stats

        self.hp_s = 50 #max hp

        #base attack stat
        self.att_s = 10

        #actual attack when you add on future effects like weapons.
        self.att = 10

        #how random the attack is, i.e. for att = 10 and att_r = 2, the player can deal between 8 and 12 damage
        self.att_r = 2

        self.next_lvl = 20

        #maybe we'll have an adjustable inventory size
        self.inventory_size = 50
        self.inven = [item(empty = True)] * self.inventory_size    

        #equip slots
        #0 is helm
        #1 is chest
        #2 is pants
        #3 is boots
        #4 is weapon
        self.es = [item(empty = True)] * 5

    

    async def lvl_up(self, channel):
        
        self.lvl += 1
        #I'm going to make the level curve fully exponential, for the extra euphoria of exponential growth
        #oh no! The xp curve grows faster than thes stats >:D
        #Time to get everyone addicted!
        self.next_lvl = int(1.3 ** (self.lvl-1) *20)
        self.att_s = int(1.2 ** (self.lvl-1) * 10)
        self.hp_s = int (1.2 ** (self.lvl-1) * 50)
        self.cur_hp = self.hp_s
        self.xp = 0
        self.upd_stats()
        await client.send_message(channel, "%s has levelled to level %d!" % (self.name, self.lvl))
    
    #Should be called every time the base stats change. This is helpful for future systems like equips
    def upd_stats(self):
        self.att = self.att_s
        #the randomness of attack is gonna be +-20%, just because I can set it to be.
        self.att_r = int(self.att_s * 0.2)

    #Increases character's xp by amount, and deals with all the level up logic.
    async def inc_xp(self,amount,channel):
        while amount > 0:
            if (amount >= self.next_lvl - self.xp):
                amount -= self.next_lvl - self.xp
                await self.lvl_up(channel)
            else:
                self.xp += amount
                amount = 0

    #Prints out contents of inventory
    async def view_inventory(self,channel):
        outstr = "```||====%s's inventory====||\n\n" % self.name
        for i,item in enumerate(self.inven):
            if (not item.empty):
                outstr += "%d. %s:\n    %s\n\n" % (i+1, item.name, item.desc)
        await client.send_message(channel,outstr + "```")
    
    #Returns whether or not there's an empty slot in the inventory
    def inventory_empty(self):
        for item in self.inven:
            if (item.empty):
                return True
        return False

    #Player must have an empty inventory slot
    async def pick_up_item(self,item,channel):
        flag = False
        for i in range(self.inventory_size):
            if self.inven[i].empty:
                self.inven[i] = item
                flag = True
                break
        if flag:
            await client.send_message(channel,"<@%s>```%s successfully picked up %s.```" % (self.id,self.name,item.name))
        else:
            #Never meant to reach here
            await client.send_message(channel,"<@%s>```Wait %s, you have a full inventory already!```" % (self.id,self.name))
        return flag
    
    #Removes item from inventory, returns whether or not it is successful
    def remove_item(self,item_name):
        for i, item in enumerate(self.inven):
            if (not item.empty and item.name.lower() ==  item_name):
                del self.inven[i]
                return True
        return False
    
    #Returns whether or not there is a 'usable' item with the item_name
    def item_exists(self,item_name):
        for item in self.inven:
            if (not item.empty and item.name.lower() ==  item_name and item.usable):
                return True
        return False
    async def drop_item(self, item_name, channel):
        for i, item in enumerate(self.inven):
            if (not item.empty and item.name.lower() ==  item_name):
                world.rl[self.room].items.append(item)
                del self.inven[i]
                await client.send_message(channel,"Successfully dropped %s" % item_name)
                return
        await client.send_message(channel, "Could not find %s" % item_name)
        return

    async def show_room(self, channel):
        await world.rl[self.room].print_room(channel,self.id, self.name)

    
    async def goto_room(self, channel, room):
        #Steps:
        #0: Check if player can even progress.
        #1: Search for room, send messages if can't find it
        #2: actually move the player, update last_room
        if world.rl[self.room].can_proceed(self.id):
            a = 0

            #Handles both scenarios, whether or not the room name
            #passed into the function is the index of the room,
            #or the name of the room
            try:
                a = int(room)
            except:
                a = world.rl[self.room].find_room(room)
            
            if a in world.rl[self.room].links:
                self.last_room = self.room
                self.room = a
                await client.send_message(channel, "```%s has successfully moved to '%s'```" % (self.name, room))
                await self.show_room(channel)
            else:
                await client.send_message(channel, "<@%s>: ```Error! Room '%s' does not exist!```" % (self.id, room))
            
        else:
            await client.send_message(channel, "<@%s>:```%s```" % (self.id,world.rl[self.room].fight_error))

    async def go_back(self,channel):
        temp = self.room
        self.room = self.last_room
        self.last_room = temp
        #Just go back to the last room you've been in, making sure to update the last_room property.
        await client.send_message(channel, "%s has fled back to: %s" % (self.name,world.rl[self.room].name))
        


#This is like the all-important dictionary that contains all the data of everyone who has every played.
char_dict = {
    "dummy": character("-69","haha lol")
}

#Returns whether or not there exists a character with that ID
def character_exists(id):
    if id in char_dict:
        return True
    else:
        return False

#Creates a new character under the user id. The character should not yet exist.
def create_character(id, name):
    char_dict[id] = character(id, name)

#4 days later Quang here: WHY DID I EVER DECIDE THIS WAS A GOOD IDEA???
#Returns a string containing all the formatted stats of character id
def view_stats(id, name):
    c = char_dict[id] #Don't mind me, just gonna use this variable as a macro
    
    #multi line strings to the rescue at making things nice and readable!
    return '''
    ```||====%s's Stats====||

    
    LVL: %d
    XP: %d/%d
    HP: %d/%d

    ATK: %d-%d
```''' % (name, c.lvl,c.xp,c.next_lvl,c.cur_hp,c.hp_s,c.att - c.att_r, c.att + c.att_r)        
    
#increases XP, for debugging purposes.
async def hax(id,channel):
    await char_dict[id].inc_xp(100,channel)

#Attempts to pick up an item
async def pick_up_item_request(id,channel,name):
    if char_dict[id].inventory_empty():
        a = world.rl[char_dict[id].room].search_item(name)
        if (a.empty):
            await client.send_message(channel, "Sorry %s, could not find the item you were looking for." % char_dict[id].name)
        else:
            await char_dict[id].pick_up_item(a,channel)

    else:
        await client.send_message(channel, "Sorry %s, your inventory is too full. Please empty a slot and try again" % char_dict[id].name)

def getroom(id):
    return char_dict[id].room
