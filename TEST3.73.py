#Reddit Reply Bot
#----------------
#This bot is capable of scanning reddit comments if they contain specific words. If so, the bot will automatically reply to this comment.
#It scans up to 100 posts at a time which is the limit of PRAW. It only scans new posts.
#Reddit Reply Bot is capable of scanning multiple subreddits.
#It's also capable of searching for multiple phrases.
#
#Bot base from /u/GoldenSights, I just improved this bot and added some try/except blocks for more stable using and some other improvements.
#
#(c) /u/GoldenSights and me, Maximilian Krause aka. Spaaze
#Follow me on Twitter for updates: @spaazede

import traceback
import praw #Reddit API. Install through 'pip praw' (for help on how to use pip, ask Google!)
import time
import sqlite3
import sys
import colorama #Color API. Install through 'pip colorama'
from random import randrange
from random import randint

#Your part! Configure the bot.
USER         = "[REDACTED]" #insert your reddit username here
PASS         = "[REDACTED]" #and the pass
AGENT        = "responds to comments with S.H.I.E.L.D. facts. Credit to M. Krause, /u/GoldenSights, /u/mathleet, /u/Beacon114 :)" #an useragent describing your bot
SUBR         = "shield" #the subreddit(s) to scan
SEARCHSTRING = ["/u/AgentKoenigLMD", "SHIELD Fact"] #the phrases the bot should look for
SECRETCODE   = ["[REDACTED]"]
HACKCODE     = ["[REDACTED]", "[REDACTED]"]
HACKREP      = "\n\n *Hello, Skye.* I've upgraded the mainframe since you last hacked it - *I won't be fooled again!*\n\n ----- \n\n *Congratulations! You've found Skye's special response! Well done!*\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"
SIMMONSCODE  = ["A0956307", "A 0956307", "0956307"]
SIMMONSREP   = "**SIMMONS**, Jemma.\n\n Known aliases: N/A\n\n Designation: **HEAD OF SCIENCE AND TECHNOLOGY DIVISION**.\n\n Specialities: **BIOCHEMISTRY, XENOBIOLOGY, ADVANCED FIRST AID AND LIFE SUPPORT TRAINING**.\n\n Access: **SCI_TECH_DATABASES, UNDERCOVER_MISSION_FILES, PROJECT_INDEX**.\n\n Status: **ACTIVE**.\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"
FITZCODE     = ["A0947329", "A 0947329", "0947329"]
FITZREP      = "**FITZ**, Leopold.\n\n Known aliases: N/A\n\n Designation: **ENGINEER.** ~~**SCIENCE AND TECHNOLOGY DIVISION**~~.\n\n Specialities: **MECHANICS, ROBOTICS, AVIONICS**.\n\n Access: **WITHDRAWN**.\n\n Status: **AT LARGE**.\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"
WARDCODE     = ["A0849329", "A 0849329", "0849329"]
WARDREP      = "**WARD**, Grant D.\n\n Known aliases: Dan Filch; Zack\n\n Designation: **FUGITIVE**.\n\n Specialities: **ESPIONAGE, IEDD, SNIPER**.\n\n Access: **NONE**\n\n Status: **AT LARGE**.\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"
MAYCODE      = ["A078634", "A 078634", "078634"]
MAYREP       = "**MAY**, Melinda Q.\n\n Known aliases: The Cavalry; Dr. Roum; Heidi Martin\n\n Designation: **SENIOR FIELD SPECIALIST**, **S.H.I.E.L.D. BOARD MEMBER**.\n\n Specialities: **CLOSE COMBAT, ASSET AND CIVILIAN EXFIL, PILOT**.\n\n Access: **FULL**.\n\n Status: **ACTIVE**.\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"
COULSONCODE  = ["SKJ08U7342", "SKJ 08U7342", "08U7342"]
COULSONREP   = "**COULSON**, Phillip J.\n\n Known aliases: Phillip, Son of Coul; Pablo Jimenez; Theo Tittle; Charles Martin\n\n Designation: ~~**DIRECTOR**~~ **FUGITIVE**.\n\n Specialities: **OPERATIONS, INDEX EVALUATION AND UPTAKE, NEGOTIATION, THREAT ANALYSIS**.\n\n Access: ~~**FULL**~~ **DENIED** by order of **GONZALES**, Robert.\n\n Status: **AT LARGE**.\n\n Enter authorization code for encrypted inbox access.\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"
POSTC        = 10 #the post count the bot should get at a time. maximum: 100
WAITSEC      = 20 #how long the bot should wait until it searches again (seconds)
#retired as of v2.173 - leave in just in case
IMGONNADOIT  = ["Cavalry"]
SONJUSTDONT  = "Don't *ever* call her that.\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"
WHATIFISAY   = ["Calvary"]
NOJUSTNO     = "I know what you mean. And *she* knows what you mean. Don't *ever* call her that.\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)"

from colorama import init
init()                                  #initializing colorama
from colorama import Fore, Back, Style  #and importing the color stuff

#setting the colored status codes for further use
FAIL = Fore.RED + '[FAIL] ' + Fore.WHITE
OK = Fore.GREEN + '[OK]   ' + Fore.WHITE
WAIT = Fore.MAGENTA + '[WAIT] ' + Fore.WHITE
WARN = Fore.YELLOW + '[WARN] ' + Fore.WHITE

#setting up the random response from the mainframe
def get_fact():
    SHIELD_facts = []
    with open("SHIELD_facts.txt") as f:
        for line in f:
            SHIELD_facts.append(line)
        return "%s\n\n ----- \n\n ^(Can you guess the secret authorization code?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)" % SHIELD_facts[randrange(len(SHIELD_facts))].strip('\n')
        
def secret_fact():
    SECRET_factsv1 = []
    with open("SECRET_factsv1.txt") as f:
        for line in f:
            SECRET_factsv1.append(line)
        return "%s\n\n ----- \n\n *Congratulations! You've guessed the Director's secret authorization code!* \n\n ----- \n\n ^(Can you guess the other secret codes?)\n\n ^(I am an LMD. Please PM me if you have questions, suggestions or facts to submit. Excelsior!)" % SECRET_factsv1[randrange(len(SECRET_factsv1))].strip('\n')

#welcome message
print(Fore.CYAN + 'Welcome to ' + Fore.RED + 'S.H.I.E.L.D. Facts LMD v2.181')

#trying to open the database with already scanned comments
try:
    sql = sqlite3.connect('oldposts.db')
    print(OK + 'Successfully loaded SQL database "oldposts.db"')
    db = sql.cursor()
    db.execute('CREATE TABLE IF NOT EXISTS seenposts(ID TEXT)') #creating a table if it doesn't exist already
    print(OK + 'Loaded/created table "seenposts"')
except Exception as e:
    print(FAIL + 'Database "oldposts.db" couldn\'t be loaded.')
    time.sleep(5)
    sys.exit(0)   #exiting after 5sec if there was a problem with the database
sql.commit()

#log-in process
print('Logging in, please wait...')
r = praw.Reddit(AGENT) #setting the useragent
try:
    r.login(USER, PASS) #logging in
    print('Logged in!') #alright
except Exception as e:
    print(FAIL + 'Couldn\'t login. Please check the credentials.')
    time.sleep(5)
    sys.exit(0)   #exiting after 5sec if there was a problem with the login

#now for the scanning part!

def scan():
    print(WAIT + 'Searching '+ SUBR + '...')
    subr = r.get_subreddit(SUBR) #opening the subreddit
    posts = subr.get_comments(limit=POSTC) #getting the comments from the subreddit(s)
    for post in posts:
        pid = post.id
        try:
            pauthor = post.author.name
            db.execute('SELECT * FROM seenposts WHERE ID=?', [pid])
            if not db.fetchone():                                   #checking if we already scanned that post
                pbody = post.body.lower()
                if any(key.lower() in pbody for key in SEARCHSTRING):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('Target acquired!')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('Accessing S.H.I.E.L.D. mainframe... access granted!\n\n' + get_fact() + '\n\n')
                        print('Mission complete!')
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
                elif any(key.lower() in pbody for key in SECRETCODE):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('Director Coulson is requesting access!')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('Checking code... authorization code accepted!\n\n' + '**COULSON**, Philip J.\n\n' + 'Accessing encrypted inbox...\n\n' + 'One unread message:\n\n' + secret_fact() + '\n\n')
                        print('Access granted!')                       
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
                elif any(key.lower() in pbody for key in HACKCODE):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('Oho, Skye\'s falling into my trap...')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('Accessing S.H.I.E.L.D. mainframe... **ACCESS DENIED**.\n\n' + HACKREP + '\n\n')
                        print('You got her good!!!')
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
                elif any(key.lower() in pbody for key in SIMMONSCODE):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('ID lookup requested.')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('ID lookup...successful.\n\n' + SIMMONSREP + '\n\n')
                        print('ID lookup successful.')
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
                elif any(key.lower() in pbody for key in FITZCODE):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('ID lookup requested.')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('ID lookup...successful.\n\n' + FITZREP + '\n\n')
                        print('ID lookup successful.')
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
                elif any(key.lower() in pbody for key in WARDCODE):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('ID lookup requested.')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('ID lookup...successful.\n\n' + WARDREP + '\n\n')
                        print('ID lookup successful.')
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
                elif any(key.lower() in pbody for key in MAYCODE):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('ID lookup requested.')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('ID lookup...successful.\n\n' + MAYREP + '\n\n')
                        print('ID lookup successful.')
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
                elif any(key.lower() in pbody for key in COULSONCODE):
                    if pauthor.lower() != USER.lower(): #checking if we posted that comment, we won't reply on our own comments
                        print('ID lookup requested.')
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply('ID lookup...successful.\n\n' + COULSONREP + '\n\n')
                        print('ID lookup successful.')
                    else:
                        print(WARN + 'Found post, but was posted by ' + USER)
            db.execute('INSERT INTO seenposts VALUES(?)', [pid])                          
        except AttributeError:
            pass
    sql.commit()
    
#scanning now
while True:
    try:
        scan()
    except Exception as e:
        traceback.print_exc()
    print(OK + 'Found no new posts containing codewords.')
    print(WAIT + 'Taking a breather... waiting %d seconds... \n' % WAITSEC)
    sql.commit()
    time.sleep(WAITSEC) #waiting some time until we scan again