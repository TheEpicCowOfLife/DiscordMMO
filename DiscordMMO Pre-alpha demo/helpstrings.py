'''
Documentation for every single command related to the game, that has been implemented. You can access these ingame by using !help
'''

helpstr = '''
```
If you haven't already, type !start to start the game.

This command list is divided into several sections.

!help items
    Displays information about how to manage your items

!help rooms
    Displays information about how to navigate the world

!help party
    Displays information about parties, necessary things to participate in multi-player battles.

!help battle
    Displays information about the ways you can fight.
```
'''


item_help_str = '''
```
*******
*ITEMS*
*******

Warning! You may not have more than 50 items on you at a time.
If you do, then you will not be able to pick up monster loot

!list items
    Lists all the items in the room that you can pick up.

!inven
    Displays your inventory.

!pick up [item]
    Picks up the item specified, not case sensitive. 
    Item must be in the same room as the player. 
    Use !list items to see what items you can pick up.
    
    Example usage: !pick up StIcK

!drop [item]
    Drops the item from your inventory into the room.

*!equip [item]
    To be implemented.

*!use [item]
    To be implemented.
```
'''

room_help_str = '''
```
*******
*ROOMS*
*******

!list room
    Displays the room you are currently in, along with the rooms you can reach.

!goto [room]
    Moves you to the room you specify with either it's id, or its name.
    The id of a room is the number next to the room when it is listed using !list room.

    Example usage:
    !goto 0
    !goto cAvE eNtRance

    (case insensitive, make sure to leave no trailing whitespace)```
'''
party_help_str = '''```
*********
*Parties*
*********

You default to be in a party consisting only of you, the leader.

NOTE: You WANT to be in a party to fight monsters. Monsters distribute their damage evenly across all members
However, as a cornered fox is more dangerous than a wolf, each additional party member you have fighting will
cause the monster to deal an extra 15%% base damage. 

This implies that as the number of members in your party
gets very large, the monster will deal 15%% of its original damage

!party leave
    Leaves the party you're in, given that you're in a party of 2 or more people
    WARNING: If you're the leader of the party, the leader will be randomly reassigned to someone else.

!party join [user]
    Requests to join the party the user belongs to.
    
    Usage: !party join @TheEpicCowOfLife#6969 (not my actual discord tag, use discord's autocomplete)

!party list members [user]
    Lists all the members of the party the user is in

!party list requests
    Lists all requests for your party.

!party accept [user]
    If that player has requested to join your party, then accept the request.
    You must be the leader to do this.

!party decline [user]
    Decline the join request for user.
    You must be the leader to do this.

!party kick [user]
    Kicks the user from your party.
    You must be the leader to do this.

!party promote [user]
    Attempts to promote the user to leader
    You must be the ledaer to do this```'''

battle_help_str = '''
```
********
*Battle*
********

!stats
    Checks out your stats!

!fight
    Initiates a fight with the monster in the room. You must be the leader of your party to use this command.
    Use this command in the text channel you want all your battle messages to arrive in.

    NOTE: This command will remove all join requests from your party.

!flee
    Run from battle, or return to the previous room.

*To be implemented
!set delay [value]
    If you want the battle to automatically continue after [value] seconds regardless of whether or not everybody
    fighting has issued a command yet. Useful if you have large parties and you don't want idle players holding you up.

    Set value to be a negative number to turn it off
    
    Usage: !set delay 10

!use [skill] [priority]
    Attempts to use [skill] to fight monsters when in battle. In parties, skills with higher priorities will be executed first.
    Priority will default to 0

    In this alpha stage, you only have access to two skills:
    !use strike
        Hit the monster till it dies.
        Deals 1x damage. Your stock standard skill

    !use shove    
        Shove the monster really hard.
        Deals 0.7x damage, but it adds a stack of stagger, which causes the very next attack to deal 1.5x damage
        Stacks of stagger decrement at the start of the players' turn.

    Example:
    !use shove 99999
    !use strike -1

    !use [item] [priority]
        This command can only be used in battle, an will attempt to consume [item] from your inventory.
        Right now, the only think you can do is heal
```
    '''