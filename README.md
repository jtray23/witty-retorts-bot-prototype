# witty-retorts-bot-prototype

A Discord bot (prototype) that allows users to play a chat game called "Witty Retorts", which is inspired by Cards Against Humanity and Evil Apples (with a small twist).

## License & Disclaimer

This project is licensed under the GPLv3 License (see the [LICENSE.md](LICENSE.md) file for details)

Furthermore, this is a PERSONAL PROJECT which includes ADULT THEMES AND LANGUAGE that I made for my friend's Discord server because I wanted an Evil Apples/Cards Against Humanity-style game available to play in chat, but could not find any other Discord bots which offered this functionality. As such, it is a prototype that is VERY quick and dirty, and would need extensive refactoring before being "released" as an open source app, especially when considering the logical requirements of a game where certain responses must be hidden and certain channel IDs accounted for in the code.

## Overview

Let's be honest, the best part about Cards Against Humanity or Evil Apples is the ability to play "custom answer" cards (wildcards) which allow you to demonstrate your superior sense of humor. 

Without these wildcards, the game devolves into a repetitious bore where the same tired cards keep coming up again and again for the same "question" cards. This phenomenon really pisses me off, and is caused by a perverse incentive to withhold custom cards from play; custom cards always "cost money" in the real and/or digital sense, while the boring stock cards are always free. Consequently, the vast majority of players will simply be lazy and pick from the stock cards given to them "randomly". I use air quotes here because on Evil Apples, card distribution is not really "random"; in general, there is a set of "compatible comedy" cards for most "question" cards, and if you are lucky enough to get one of these compatible cards, then your card will generally win the round because of this "compatible comedy angle" which obliges *most* judges to simply go with the flow and select the obviously compatible humor (unless, of course, the judge is clueless or anarchic, and chooses a different card out of spite).

Based on my above experiences, I decided to flip the script and make a variation of the game where **every** card is a "custom answer" card, and the **wildcards** are randomly chosen images from imgur.com! 

As a result, Witty Retorts forces players to rely on their own sense of humor most of the time, which keeps the game fresh, in addition to minimizing the damage that stock cards have on the game when players can't think of anything funny to say. In other words, there are essentially an infinite number of images on imgur.com that we can pull randomly, so my deck of stock cards (named "wildcards") is **very** wild and essentially never repeats itself.

[Play Witty Retorts Test Server](https://discord.gg/CrEYNk3)

**IMPORTANT NOTE: All BrawndoCoin earned in-game is exchangeable at the current exchange rate of 1 BrawndoCoin = $0.0000000000000000000000000000000000000001**

## Gameplay

1. The round begins when **at least 3 players** DM the WittyRetortsBot with: ```!putmeincoach``` (2 players and 1 judge is the smallest game possible; players in "ready" state will be forced to "not ready" state if the game does not start within a couple minutes, forcing "away" players to not accidentally be added to the next starting game)
2. One player is chosen to be the judge for each round (this happens in *sequential* order and not *random* order, just like Evil Apples and Cards Against Humanity)
3. All other players have **60 seconds** to DM the WittyRetortsBot with their funny "answer" (witty retort) to the randomly chosen "question" card.
   1. If any of the players can't think of a witty retort, they can DM the WittyRetortsBot with ```!wildcard``` to choose a random image from imgur.com.
      ![Purchasing a Wildcard](https://cdn.discordapp.com/attachments/439916633784320003/442544257849491457/Screen_Shot_2018-05-05_at_9.31.42_PM.png)
      1. Players *without* an entry on the High Scores roster can play wildcards for free (i.e. the player has never won a round, and therefore has no BrawndoCoin to spend; this encourages new players to try the feature and stay in the game if nothing to say quite yet).
      2. Players *with* an entry on the High Scores roster must spend 1 BrawndoCoin to play 1 wildcard (i.e. the player could have 0 or more BrawndoCoin on the High Scores, and therefore can not use a wildcard if at 0; this encourages experienced players to not rely so much on the random image thing too much, as that could defeats the purpose of Witty Retorts).
   2. If any player forgets to DM a retort or runs out of time, then they will be taken out of the game, and will need to re-join the game to play in the next round.
4. After the timer for sending retorts expires, the judge then has **up to 60 seconds** to DM the WittyRetortsBot with the number of the winning retort (the round ends when time is up or when judge picks the winning retort).
   1. If a winner is chosen, that player is credited with 1 BrawndoCoin on the High Scores roster.
   2. If the judge forgets to DM the winning retort or runs out of time, then **no winner** is chosen, and the judge will be taken out of the game, and will need to re-join the game to play in the next round.
   ![Round Summary](https://im3.ezgif.com/tmp/ezgif-3-f57b0c39ed.gif)

**At any point in the round, if the player count falls below 3, then the round will terminate early and the bot will waits for more players to join the game efore stating a new round.**

## Setup

1. This app uses the wonderful [Discord.py](https://github.com/Rapptz/discord.py) library.
2. You can add/update/remove any "question" cards at the top of the code.
3. One channel ID in the Discord server must be chosen as the "Lobby" general channel, where messaging is allowed for everyone(for checking high score roster with ```!highscores``` and joining the game with ```!putmeincoach``` (although, these can be done via DM as well).
4. A different channel ID in the Discord server must be chosen as the "Game" channel **where sending messages is not allowed, except for messages from WittyRetortsBot** (this forces players to keep their retorts hidden from spectators and other players).

Heroku config vars that need to be created for this app:

```term
$ heroku config
CVAR_TOKEN: ********************
CVAR_GAME_CHANNEL_ID: ************************
CVAR_GENERAL_CHANNEL_ID: *************************
DATABASE_URL:      postgres://************:*******************.compute-*.amazonaws.com:*****/*****************
```

NOTE: Running this app on a Free Heroku dyno comes with the accidental bonus side-effect of announcing the game and high scores roster roughly once per day (when the free dyno restarts).
