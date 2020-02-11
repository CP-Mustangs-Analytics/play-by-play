import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import urllib.request
import requests_html
import os

# Scraping
resp = requests.get('https://stats.ncaa.org/game/play_by_play/4705101')
resp
# Soup
soup = BeautifulSoup(resp.content)
table = soup.find_all("table")

# Structure
'''
len(tables) = 22
tables[0] = runs by inning, r, h, error
tables[1] = weather information, other random stuff I don't know
tables[2] = date, location, attendance
tables[3] = umpires
tables[4] = 1st inning
tables[5] = first inning play by play
tables[6] = second inning
tables[7] = second inning play by play
    .
    .
    .
tables[20] = 9th inning
tables[21] = 9th inning play by play
'''

# Utility Funcitions
def find_basestates(play, first, second, third):
    runs = 0
    if "advanced" in play:
        first, second, third = 0, 0, 0
    actions = [a.strip() for a in play.split(";")]
    for action in reversed(actions):
        if "scored" in action:
            runs += 1
        elif (("wild pitch" in action) or ("passed ball" in action)):
            base = action.split()[-5]
            if "first" in base:
                first = 1
            if "second" in base:
                second = 1
            if "third" in base:
                third = 1
        elif (("advanced" in action) or ("stole" in action)):
            base = action.split()[-1]
            if "first" in base:
                first = 1
            if "second" in base:
                second = 1
            if "third" in base:
                third = 1
        else:
            if (("singled" in action) or ("walked" in action) or ("hit by pitch" in action)):
                first = 1
            if "doubled" in action:
                second = 1
            if "tripled" in action:
                third = 1
            if "homered" in action:
                runs += 1
    return first, second, third, runs

def parse_action(play):
    res = ""
    for word in play:
        if word in ["advanced"]:
            return "advanced on wild pitch"
        if word in ["singled", "doubled", "tripled", "homered"]:
            return word
        if word in ["to"]:
            break
        elif '(' in word:
            break
        elif word in ["stole", "walked"]:
            return word
        elif ',' in word:
            return word.split(',')[0]
        else:
            res += word + " "
    return res.strip()

def batter_action(play):
    batter = ""
    index = 0
    words = play.split()
    for word in words:
        if not word[0].isupper():
            break
        batter += word
        index+=1

    return batter, parse_action(words[index:])

# Building DataFrame
columns = ['team','inning', 'half', 'outs', 'batter', 'action', 'first', 'second', 'third', 'runs_scored', 'home_score', 'visitor_score']
plays = pd.DataFrame(columns=columns)

stopwordsToCheck = ["batting starts", "failed pickoff attempt", "no play", "pinch hit", "to p for", "to dh"]

date = '1-1-2020' # update

home_string = "Oklahoma" # update
visitor_string = "Cal_Poly" # update

home = False

home_score = 0
visitor_score = 0

inning_number = 1
half = "top"

outs = 0

first = 0
second = 0
third = 0

start_index = 4

for inning in table[start_index:]:
    if start_index % 2 == 0:
        start_index+=1
        continue
    for row in inning.find_all("td", "smtext"):
        if row.text == '':
            continue
        team = home_string if home else visitor_string
        half = "bottom" if home else "top"
        play = row.text
        if (any(stop in play.lower() for stop in stopwordsToCheck) or (play.lower()[0].isdigit())):
            continue
        batter, action = batter_action(play)
        outs += (play.lower().count("out") + play.lower().count("popped up") + play.lower().count("double play"))
        first, second, third, runs = find_basestates(play.lower(), first, second, third)
        if home:
            home_score += runs
        else:
            visitor_score += runs
        result = [team, inning_number, half, outs, batter, action, first, second, third, runs, home_score, visitor_score]
        line_dict = dict(zip(columns, result))
        plays = plays.append(line_dict, ignore_index=True)
        if outs >= 3:
            if home:
                home = False
                inning_number += 1
            else:
                home= True
            first = 0
            second = 0
            third = 0
            outs = 0

#Saving and writing to files
home_path = f'{home_string}v{visitor_string}_{date}'
away_path = f'{home_string}v{visitor_string}_{date}'

plays.to_csv(home_path,index=False)
#os.system(f'cp {home_path} {away_path}')

'''
Questions I still have:
    Fielders choice - runners - state is right, do we need to show?
    Wild pitch/passed ball - multiple runners advancing - even double steal
        - also what is the action - should be "advanced on passed ball" or "advanced on wild pitch"
    double plays - esp outfield assists

    These are kinda spaghetti code rn just to make it work,
    would like a more permanant solution - might require some refactoring
'''
