'''
Contains the monster class, and the methods and skills for applying damage to them.

Also contains the template instances of different monsters.
'''

from core import item,client
from copy import deepcopy
import world
import player

class monster:
    def __init__(self):
        self.name = ""

        #Its initial hp
        self.hp = 0

        #its average attack
        self.att = 0

        #by how much % its attack varies
        self.att_range = 0.2

        #The item it drops
        self.drop = item(empty = True)

        #Amount of xp is dropped when killed
        self.xp_drop = 0

        #Amount of stacks of stagger, causes critical hit upon next attack
        self.stagger_stacks = 0

    #Called to decrement the monster's effects after its turn has ended
    def decrement_stacks(self):
        self.stagger_stacks = max(0,self.stagger_stacks-1)
    
    async def take_damage(self,id,damage,channel):

        if self.stagger_stacks > 0:
            self.hp -= int(damage * 1.5)
            self.stagger_stacks -= 1
            await client.send_message(channel,"<@%s>```Critical hit! %s dealt %d damage to %s!\n\n%s's hp is now %d.```" % (id,player.char_dict[id].name,int(damage * 1.5),self.name,self.name,self.hp))
            
        else:
            self.hp -= damage
            await client.send_message(channel, "<@%s>```%s dealt %d damage to %s!\n\n%s's hp is now %d.```" % (id,player.char_dict[id].name,int(damage),self.name,self.name,self.hp))
        
    async def receive_attack(self,id,skill,damage, channel):
        #strike, basic, normal boring attack
        sid = -1
        try:
            sid = sd[skill]
        except: 
            player.char_dict[id].cur_hp += world.il[skill].heal
            player.char_dict[id].cur_hp = min(player.char_dict[id].cur_hp,player.char_dict[id].hp_s)
            await client.send_message(channel,"<@%s>```%s used %s, and healed to %d hp.```"% (id, player.char_dict[id].name, skill,  player.char_dict[id].cur_hp))
            player.char_dict[id].remove_item(skill)
        if sid == 0:
            await client.send_message(channel, "<@%s>```%s used Strike.```" % (id,player.char_dict[id].name))
            await self.take_damage(id,damage,channel)
            pass
        
        if sid == 1:
            await client.send_message(channel, "<@%s>```%s used Shove. %s now has %d stacks of stagger.```" % (id, player.char_dict[id].name, self.name, self.stagger_stacks + 1))
            await self.take_damage(id,int (damage * 0.7), channel)
            self.stagger_stacks += 1
        

#Monster dictionary, consists of a copy of all the monsters, ready to be cloned and slaughtered.
md = {

}
#Ok, so this is a really nice and clean way to initialise and tweak the value of different

md["slime"] = monster()
md["slime"].name = "Suicidal Slime"
md["slime"].hp = 20
md["slime"].att = 3
md["slime"].att_range = 0.60
md["slime"].drop = deepcopy(world.il["soothing gel"])
md["slime"].xp_drop = 10

md["bat"] = monster()
md["bat"].name = "Vicious Bat"
md["bat"].hp = 40
md["bat"].att = 12
md["bat"].att_range = 0.20
md["bat"].drop = deepcopy(world.il["bat leather"])
md["bat"].xp_drop = 20

md["guard"] = monster() 
md["guard"].name = "Dwarf Warrior"
md["guard"].hp = 100
md["guard"].att = 23
md["guard"].att_range = 0.20
md["guard"].drop = deepcopy(world.il["dwarven tonic"])
md["guard"].xp_drop = 50

md["king"] = monster()
md["king"].name = "Dwarf King"
md["king"].hp = 300
md["king"].att = 50
md["king"].att_range = 0.20
md["king"].drop = deepcopy(world.il["win note"])
md["king"].xp_drop = 200



#Skills dictionary
sd = {
    "strike" : 0,
    "shove" : 1
}