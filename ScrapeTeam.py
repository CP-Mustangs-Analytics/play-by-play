import requests
from bs4 import BeautifulSoup
from ProcessGame import scrape_game

base_url = "https://stats.ncaa.org"

def find_play_by_play_link(game_link):
    resp = requests.get(base_url + game_link)
    soup = BeautifulSoup(resp.content)
    links = soup.find_all("li")
    for l in links:
        if l.text.strip() == "Play by Play":
            link = l.find("a", href=True)["href"]
            return link

def scrape_team_games(team_links):
    if len(team_links) == 0:
        return
    team_id = team_links.pop(0)

    resp = requests.get(base_url + team_id)
    soup = BeautifulSoup(resp.content)
    field = soup.find_all("fieldset")

    '''
    Structure
    field[0] - Overall information?
    field[1] - stadium information
    field[2] - larry table
    field[3] - season to date table
    field[4]
        :
        : - all tables w/in field 3? dumb
        :
    field[9]
    field[10] - actual infomation
    '''

    tr = field[10].find("tbody").find_all("tr")

    for i in range(0, len(tr), 2):
        td = tr[i].find_all("td")
        team = td[1].find("a", href=True)["href"]
        if team not in team_links:
            team_links.append(team)
        game_link = find_play_by_play_link(td[2].find("a", href=True)["href"])
        scrape_game(base_url+game_link)

    scrape_team_games(team_links)

team_links = ["/teams/471251"]
scrape_team_games(team_links)
