# DiscordMMO

So... Uhhhh...

I tried to create a basic MMO in Discord, and basically try and demonstrate multiple individual clients affecting a global world, and MULTIPLAYER CO-OP BATTLE...
which ended up having complexity spiralling out of control, forcing me to implement a super buggy party system...

BUT IT WORKS. MOSTLY.
I said I would come back to this project. That was in Feburary 2019. I'm still sick and tired of asynchronous programming.

In order to run this... monstrosity, you need to have discord.py installed. Should be available through pip, I believe.
Then, you set up your discord bot, get its super secret token, plug it into core.py, and then run bot.py

It should be as simple as that.
Except, Python 3.7 made async a reserved keyword which broke the whole thing, so like run it in 3.6, or maybe some other later version when they fix this.

Either way, time to brush this project off into the mostly-complete-but-not-touching-again lands.
