
import discord
import psycopg2
import urllib.parse as urlparse
import random
import asyncio
import aiohttp
from discord.ext.commands import Bot
import os
import re

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

con = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
cur = con.cursor()
cur.execute("""SELECT name, score from high_scores order by 2 desc;""")

high_score_roster = {}
for row in cur.fetchall():
    high_score_roster[row[0]] = row[1]

cur.close()
con.close()


BOT_PREFIX = ("!")

TOKEN = os.environ['CVAR_TOKEN'] 

game_channel_id = os.environ['CVAR_GAME_CHANNEL_ID'] #I chose to have the game "happen" in a public channel, so spectators can watch (but just as easily could refactor it all to happen in DMs)
general_channel_id = os.environ['CVAR_GENERAL_CHANNEL_ID'] #Bot needs to know about messages posted in the general channel, and ignore everything else (Witty Retorts REQUIRES hidden responses for the game to make sense) 

client = Bot(command_prefix=BOT_PREFIX)

judged_statements = [
    "`_______`. Betchya can't have just one.",
    "That guy is such a PUBG noob, he still thinks you can `_______` on the live server!",
    "It's pretty easy to give rando streamers your money all day if `_______`",
    "I saw Tommy Wiseau in person the other day and `_______`",
    "Why is shroud not a hacker? `_______`",
    "`_______` just gets better with age.",
    "Dude, I'm telling you, `_______` is going to a PUBG killer, dude.",
    "Trust me, it's not polite to talk about `_______` on first dates.",
    "Why is Windows 10 the best Windows ever? `_______`",
    "Coming to Broadway this season, `_______`: The Musical.",
    "`_______` will *always* get you laid, bro.",
    "My waifu and I are really into `_______`",
    "Fortnite is the *best* BR game ever because `_______`",
    "They said I could become anything...So I became `_______`",
    "The most fucked up subreddit I've ever seen is /r/`_______`",
    "During sex, I can't help but think about `_______`",
    "The *one* new thing that PUBG needs is `_______`",
    "`_______`? There's a app for that.",
    "Why are my balls so sore? `_______`",
    "Back in my day we had to `_______`! And you know what? We liked it!",
    "The worst thing I did as a certified BullyHunter was `_______`",
    "BILLY MAYS HERE, AND `_______`",
    "Did you hear?! Nvidia just announced `_______`!!",
    "I once dated a guy who `_______`",
    "`_______` is my anti-drug.",
    "Dude! Why is this part all sticky? `_______`",
    "I drink to forget `_______`",
    "PLAYERUNKNOWN's next game: `_______`",
    "People believe in Jesus because he's the only one who can `_______`",
    "For my money, the best stand-up comedian ever is `_______`",
    "I once dated a chick who `_______`",
    "White people seem to be really good at `_______`",
    "If I was the President of the United States, I would ban `_______` on my first day in office.",
    "Welp...I hope they serve `_______` in hell, then.",
    "`_______` is the only way Batman can get off, now.",
    "Studies have shown mice can navigate mazes twice as fast if you give them `_______`",
]

random.shuffle(judged_statements)

is_playing_game = False

is_statement_announced = False
is_players_45_second_warning_announced = False
is_players_30_second_warning_announced = False
is_players_15_second_warning_announced = False

is_retorts_announced = False
is_judges_45_second_warning_announced = False
is_judges_30_second_warning_announced = False
is_judges_15_second_warning_announced = False

current_player_roster = []
current_judge = ""
player_retorts = {}
current_statement = ""
current_retort_index = 0

auto_snooze_countdown = 12 #4 per minute, 3 minutes total

async def reset_game():
    global is_playing_game
    global is_statement_announced
    global is_players_45_second_warning_announced
    global is_players_30_second_warning_announced
    global is_players_15_second_warning_announced

    global is_retorts_announced
    global is_judges_45_second_warning_announced
    global is_judges_30_second_warning_announced
    global is_judges_15_second_warning_announced

    global current_player_roster
    global current_judge
    global player_retorts
    global current_statement
    global current_retort_index

    is_playing_game = False

    is_statement_announced = False
    is_players_45_second_warning_announced = False
    is_players_30_second_warning_announced = False
    is_players_15_second_warning_announced = False

    is_retorts_announced = False
    is_judges_45_second_warning_announced = False
    is_judges_30_second_warning_announced = False
    is_judges_15_second_warning_announced = False

    is_judge_found = False
    for player in current_player_roster:
        if player == current_judge:
            is_judge_found = True

            if player == current_player_roster[-1]:
                current_judge = current_player_roster[0]
                break
        elif is_judge_found:
            current_judge = player
            break

    if not is_judge_found:
        current_judge = current_player_roster[0]

    player_retorts = {}
    current_statement = ""
    current_retort_index = 0


async def get_high_scores():
    global high_score_roster

    high_score_text = ":checkered_flag: **HIGH SCORES!!1** :checkered_flag:\n"
    if len(high_score_roster) == 0:

         high_score_text += "--nobody here yet, breh--"

    else:

        player_count = 1
        for player in high_score_roster:
            if player_count == 1:
                high_score_text += ":first_place: {} - {} BrawndoCoins\n".format(player, high_score_roster[player])
            elif player_count == 2:
                high_score_text += ":second_place: {} - {} BrawndoCoins\n".format(player, high_score_roster[player])
            elif player_count == 3:
                high_score_text += ":third_place: {} - {} BrawndoCoins\n".format(player, high_score_roster[player])
            else:
                high_score_text += ":poop: {} - {} BrawndoCoins\n".format(player, high_score_roster[player])
            player_count += 1

        high_score_text += ":checkered_flag: high scores brought to you by BrawndoCoin :checkered_flag:\n:musical_note: *BrawndoCoin - it's got what gamers crave!* :musical_note:"

        return high_score_text


@client.command(pass_context=True)
async def wildcard(context):
    global is_playing_game
    global is_statement_announced
    global current_player_roster
    global current_judge
    global high_score_roster
    global player_retorts
    global general_channel_id


    if not context.message.channel.id == general_channel_id:

        if is_playing_game:

            if is_statement_announced:

                if context.message.author.name in current_player_roster:

                    if not context.message.author.name == current_judge:

                        if context.message.author.name in high_score_roster:

                            if high_score_roster[context.message.author.name] >= 1:

                                async with aiohttp.head('https://imgur.com/random', allow_redirects=False) as response:

                                    if 'Location' in response.headers:

                                        player_retorts[context.message.author.name] = response.headers['Location']


                                        url = urlparse.urlparse(os.environ['DATABASE_URL'])
                                        dbname = url.path[1:]
                                        user = url.username
                                        password = url.password
                                        host = url.hostname
                                        port = url.port

                                        con2 = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
                                        cur2 = con2.cursor()

                                        
                                        high_score_roster[context.message.author.name] -= 1

                                        cur2.execute("""UPDATE high_scores SET score = %s WHERE name = %s;""", (high_score_roster[context.message.author.name], context.message.author.name))
                                        con2.commit()
                                        cur2.close()
                                        con2.close()

                                        high_score_roster = {k:high_score_roster[k] for k in sorted(high_score_roster, key=high_score_roster.get, reverse=True)}

                                        await client.say(":credit_card: You just purchased a wildcard for 1 BrawndoCoin: " + response.headers['Location'])

                                        await client.say(":warning: BE ADVISED: saying !wildcard again will pick a different wildcard at the nominal fee of 1 additional BrawndoCoin!")

                                    else:

                                        await client.say(":sos: Fatal Error getting a wildcard from imgur.com! But don't worry, I didn't touch your precious BrawndoCoin. Try again, maybe?")

                            else:

                                await client.say(":money_with_wings: You don't even have 1 BrawndoCoin to your name, dude! wildcards always cost 1 BrawndoCoin to play *after* getting back on your feet!")
                        else:

                            await client.say(":syringe: Our records indicate you've *never even owned 1 BrawndoCoin* so I'll let you get this first hit for free, BUT...wildcards WON'T be free after you win a round and get back on your feet, dude.")

                    else:

                        await client.say(":interrobang: Judges can't use wildcards! That wouldn't even make sense!")

                else:

                    await client.say(":no_entry: DUDE! You're not even playing this round, breh! Say !putmeincoach to join the game!")

            else:

                await client.say(":no_entry: You have to wait for the next round to start *before* trying to play a wildcard!")

        else:

            await client.say(":pouting_cat: No game in progress! DM me with !putmeincoach to join and start the game!")

    else:

        await client.say(":interrobang: DUDE, I told you not to call me on this channel! Prank caller! DM me with !putmeincoach to join the game, or your retort, or !wildcard to play a wildcard!")


@client.command(pass_context=True)
async def highscores(context):

    high_score_text = await get_high_scores()
    await client.say(high_score_text)



@client.command(pass_context=True)
async def putmeincoach(context):
    global current_player_roster
    global is_retorts_announced
    global auto_snooze_countdown
    global game_channel_id
    game_channel = client.get_channel(id=game_channel_id)

    if context.message.author.name in current_player_roster:

        await client.say(":smile_cat: You are *already* in the game, dumbass...")

    elif is_retorts_announced:

        await client.say(":no_entry: The judge is already reviewing the retorts for this round! Wait until the next round starts *before* trying to join.")

    else:
        auto_snooze_countdown += 12 #every time a player joins, add 3 minutes to start a game before all players are auto-snoozed

        current_player_roster.append(context.message.author.name)
        await client.say(":game_die: **Welcome to Witty Retorts,** " + context.message.author.mention + " - now you can DM me with your retort every round, !wildcard to use a wildcard, or your number choice for wittiest retort (if you are the judge for that round).")

        if len(current_player_roster) == 1:

            await client.send_message(game_channel, ":wave: " + context.message.author.mention + " **has joined the game!** 2 more players needed to start...")

        elif len(current_player_roster) == 2:

            await client.send_message(game_channel, ":wave: " + context.message.author.mention + " **has joined the game!** 1 more player needed to start...")

        elif len(current_player_roster) == 3:

            await client.send_message(game_channel, ":wave: " + context.message.author.mention + " **has joined the game!** Waiting for next round to start...")

        else:

            await client.send_message(game_channel, ":wave: " + context.message.author.mention + " **has joined the game!**")


@client.event
async def on_message(message):
    global is_playing_game
    global current_retort_index
    global current_player_roster
    global current_judge
    global is_retorts_announced
    global is_statement_announced
    global player_retorts
    global general_channel_id

    global is_judges_15_second_warning_announced

    if message.author == client.user or message.content.startswith(BOT_PREFIX + "putmeincoach") or message.content.startswith(BOT_PREFIX + "wildcard") or message.content.startswith(BOT_PREFIX + "highscores"):

        pass

    elif message.channel.id == general_channel_id and message.content.startswith(BOT_PREFIX):

        await client.send_message(message.channel, ":interrobang: DUDE, I told you not to call me on this channel! Prank caller! DM me with !putmeincoach to join the game, or your retort, or !wildcard to play a wildcard!")

    elif not is_playing_game and message.content.startswith(BOT_PREFIX):

        await client.send_message(message.channel, ":pouting_cat: No game in progress! DM me with !putmeincoach to join and start the game!")

    elif is_playing_game:

        if is_retorts_announced:

            if message.author.name == current_judge:

                try:
                    if int(message.content) > 0 and int(message.content) <= len(player_retorts):
                        current_retort_index = int(message.content)
                        await client.send_message(message.channel, ":white_check_mark: The verdict is in!!! BUT, you can update your choice if you change your mind before the timer runs out!")
                        is_judges_15_second_warning_announced = True #give judge grace period of whatever seconds are left, but end the round early
                    else:
                        raise ValueError

                except ValueError:

                    await client.send_message(message.channel, ":interrobang: DUDE, put down the joint so i can unnerstnd wut u r tryin 2 say 2 me rn...PICK A VALID NUMBER CHOICE, BREH.")

            elif message.author.name in current_player_roster:

                await client.send_message(message.channel, ":no_entry: You had your chance, Chance! You must wait for the next round to start *before* retorting wittily once more.")

            else:

                await client.send_message(message.channel, ":no_entry: Shh! The judge is reaching a verdict soon; you must wait for the next round to start *before* saying !putmeincoach")

        elif is_statement_announced:

            if message.author.name == current_judge:

                await client.send_message(message.channel, ":no_entry: You are the judge this round; you must wait for all players to submit their evidence *before* choosing a number option.")

            elif message.author.name in current_player_roster:

                player_retorts[message.author.name] = message.content
                await client.send_message(message.channel, ":white_check_mark: OMG, you are so witty!!! BUT, you can send me an updated witty retort, or say !wildcard to play a wildcard instead - if you change your mind before the timer runs out!")

            else:

                await client.send_message(message.channel, ":interrobang: DUDE, I'm busy managing a game here! BY MYSELF! I said use !putmeincoach if you want in on this game, breh!")

    await client.process_commands(message)


async def background_game_loop():
    await client.wait_until_ready()
    global judged_statements
    global game_channel_id
    game_channel = client.get_channel(id=game_channel_id)    

    while not client.is_closed:
        await asyncio.sleep(15) # game logic loop runs every 15 seconds
        
        global high_score_roster
        global current_player_roster
        global current_judge

        global is_playing_game
        global is_statement_announced
        global is_players_45_second_warning_announced
        global is_players_30_second_warning_announced
        global is_players_15_second_warning_announced

        global is_retorts_announced
        global is_judges_45_second_warning_announced
        global is_judges_30_second_warning_announced
        global is_judges_15_second_warning_announced
        
        global player_retorts
        global current_statement
        global current_retort_index

        global auto_snooze_countdown

        if not is_playing_game and len(current_player_roster) < 3:

            if auto_snooze_countdown == 0:
                current_player_roster = []
            else:
                auto_snooze_countdown -= 1
            
        elif not is_playing_game and len(current_player_roster) >= 3:
            is_playing_game = True

            current_statement = random.choice(judged_statements)

            if current_judge == "":
                current_judge = random.choice(current_player_roster)
            judge_mention = discord.utils.get(client.get_all_members(), name=current_judge).mention

            await client.send_message(game_channel, ":heart_eyes_cat: :loudspeaker: **at least 3 players @here are ready to start!** Prepare thy anus for another round of Witty Retorts!\n\n:scales: " + judge_mention + " **is the judge** for this round! Judge, please DM me with the number of the wittiest retort when you are ready.\n\n:question: " + current_statement + " :question:\n\n:alarm_clock: Players now have **60 seconds** to DM me with their retorts or !wildcard to play a wildcard! GO, GO, GO!")
            is_statement_announced = True



        elif is_playing_game:


            #BEGIN LOGIC FOR JUDGE CHOICE
            if is_judges_15_second_warning_announced:
                is_retorts_announced = False # make sure judge doesnt pick a retort choice after time is up

                if current_retort_index == 0:
                    current_player_roster.remove(current_judge)
                    await client.send_message(game_channel, ":crying_cat_face: Oh noes! **The Judge was too high** to reach a verdict on the matter of wittiest retort! **Nobody wins!** Judge, you'll need to DM me with !putmeincoach to get back in the game.")
                    
                    if len(current_player_roster) < 3:
                        await client.send_message(game_channel, ":crying_cat_face: Oh noes! **At least 3 players are needed to continue the game**; DM me with !putmeincoach to join now!")

                    await reset_game()

                else:

                    winning_retort_text = ":trophy: "
                    counter = 1
                    for retort in player_retorts:
                        if counter == current_retort_index:

                            url = urlparse.urlparse(os.environ['DATABASE_URL'])
                            dbname = url.path[1:]
                            user = url.username
                            password = url.password
                            host = url.hostname
                            port = url.port

                            con2 = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
                            cur2 = con2.cursor()

                            if retort in high_score_roster:
                                high_score_roster[retort] += 1

                                cur2.execute("""UPDATE high_scores SET score = %s WHERE name = %s;""", (high_score_roster[retort], retort))
                                con2.commit()

                            else:
                                high_score_roster[retort] = 1

                                cur2.execute("""INSERT INTO high_scores VALUES (%s, %s);""", (retort, 1))
                                con2.commit()

                            cur2.close()
                            con2.close()


                            high_score_roster = {k:high_score_roster[k] for k in sorted(high_score_roster, key=high_score_roster.get, reverse=True)}

                            winner_mention = discord.utils.get(client.get_all_members(), name=retort).mention
                            winning_retort_text += winner_mention + " **has won the round** and earned 1 shiny new BrawndoCoin! :trophy:\n\n"
                            
                            url_matches = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', player_retorts[retort])
                            if url_matches:
                                winning_retort_text += "{}\n{}".format(current_statement, player_retorts[retort])
                            else:
                                winning_retort_text += current_statement.replace('`_______`', "__**{}**__".format(player_retorts[retort]))
                            
                        counter += 1
                    
                    winning_message = await client.send_message(game_channel, winning_retort_text)

                    await client.add_reaction(winning_message, '👍')
                    await client.add_reaction(winning_message, '👎')

                    high_score_text = await get_high_scores()
                    await client.send_message(game_channel, "\n\n" + high_score_text)

                    await reset_game()

            elif is_judges_30_second_warning_announced:

                await client.send_message(game_channel, ":alarm_clock: **Judge only has 15 seconds before The Final Answer is locked in!** :warning:")
                is_judges_15_second_warning_announced = True

            elif is_judges_45_second_warning_announced:

                await client.send_message(game_channel, ":alarm_clock: Judge now has **30 seconds** to DM me with the number of the wittiest retort!")
                is_judges_30_second_warning_announced = True

            elif is_retorts_announced:

                await client.send_message(game_channel, ":alarm_clock: Judge now has **45 seconds** to DM me with the number of the wittiest retort!")
                is_judges_45_second_warning_announced = True


            #BEGIN LOGIC FOR PLAYER RETORTS
            elif is_players_15_second_warning_announced:
                is_statement_announced = False #make sure nobody adds a late retort to the list

                snoozed_players = []
                for player in current_player_roster:
                    if player not in player_retorts and player != current_judge:
                        snoozed_players.append(player)

                for player in snoozed_players:
                    current_player_roster.remove(player)

                    snoozer_mention = discord.utils.get(client.get_all_members(), name=player).mention
                    await client.send_message(game_channel, ":sleeping: " + snoozer_mention + " **just snoozed** after hittin' the blunt too hard...DM me with !putmeincoach to get your head back in the game!")

                if len(player_retorts) < 2:

                    await client.send_message(game_channel, ":crying_cat_face: Oh noes! **At least 2 player retorts are needed to continue the game**; DM me with !putmeincoach to join now!")
                    await reset_game()

                else:

                    judge_mention = discord.utils.get(client.get_all_members(), name=current_judge).mention
                    await client.send_message(game_channel, ":octagonal_sign: **Time's up, @here!** All rise...Council of BBRA now in session, **Honorable Judge " + judge_mention + " presiding**...\n\n:question: " + current_statement + " :question:\n\n")

                    counter = 1
                    for retort in player_retorts.values():
                        await client.send_message(game_channel, "#**{}**. {}\n\n".format(counter, retort))
                        counter += 1

                    await client.send_message(game_channel, ":alarm_clock: **The judge now has 60 seconds** to DM me with the number of the wittiest retort.")

                    is_retorts_announced = True

            elif is_players_30_second_warning_announced:

                await client.send_message(game_channel, ":alarm_clock: **Time is running out! Players now have 15 seconds to DM me with a new/updated retort or !wildcard to play a wildcard!** :warning:")
                is_players_15_second_warning_announced = True

            elif is_players_45_second_warning_announced:

                await client.send_message(game_channel, ":alarm_clock: Players now have **30 seconds** to DM me with a new/updated retort or !wildcard to play a wildcard!")
                is_players_30_second_warning_announced = True
         
            elif is_statement_announced:

                await client.send_message(game_channel, ":alarm_clock: Players now have **45 seconds** to DM me with a new/updated retort or !wildcard to play a wildcard!")
                is_players_45_second_warning_announced = True


@client.event
async def on_ready():
    global game_channel_id
    game_channel = client.get_channel(id=game_channel_id)

    await client.change_presence(game=discord.Game(name="Witty Retorts v2.0"))
    print("Logged in as " + client.user.name)

    high_score_text = await get_high_scores()
    await client.send_message(game_channel, ":crying_cat_face: **Nobody is currently playing Witty Retorts**...that sucks - but, you and 2 others can DM me with !putmeincoach to start the game!\n\n" + high_score_text)



client.loop.create_task(background_game_loop())
client.run(TOKEN)