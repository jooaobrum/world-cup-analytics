 
# Imports
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm
import requests
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 



# Functions

def get_page_obj(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')

    return soup

def extract_teams(url, soup, id_table):
    # Extract the table of G group
    table = soup.find('table', id=id_table)
    # Extract all the rows (that contains the teams)
    rows = table.findAll('tr')

    team_dict = {}
    # Fill a dictionary with the team and the link to the squad
    for row in rows:
        cols = row.find_all('td')
        for col in cols:
            if col.find('span') != None:
                team_dict[col.find('span')['title']] = url + col.find('a', href = True)['href']
    return team_dict


def extract_players(url, soup, id_table):

    # Extract the players
    table_players = soup.find('table', id=id_table)
    # Extract all the rows (that contains the teams)
    rows = table_players.find_all('tr')

    # Key = Player's name, Elements = Link, Position, Age, Matches
    player_dict = {}
    players = []
    # Fill a dictionary with the team and the link to the squad
    for row in rows:
        player_info = []
        cols = row.find_all('th')
        for col in cols:
            if col.find('a') != None:
                # Append the player's name
                player_info.append(col.find('a').text)
                # Append player's link
                player_info.append(url + col.find('a', href = True)['href'][1:])
                cols2 = row.find_all('td')
                for col2 in cols2[:3]:
                    # Append player's Position, Age and Matches
                    player_info.append(col2.text)
                
                player_dict[player_info[0]] = player_info[1:]
    
    return player_dict


def extract_player_season(soup, id):
    # Find the link for each stats
    hist_div = soup.find("div", {"id": id})
    stats_link = []
    for tag in hist_div.find_all('ul'):
        tags_a = tag.find_all('a')
        for hrefs in tags_a:
            if ('summary' in hrefs['href']) & ('nat_tm' not in hrefs['href']):
                stats_link.append(hrefs['href'])

    return stats_link




def extract_matches_stats(url, team):
    tables = pd.DataFrame(pd.read_html(url, match = f'{team} Estatísticas d'))
    table_player = tables.loc[0][0]
    table_player = organize_table(table_player)

    
    return table_player.iloc[:-1, :]

def extract_player_matches(soup_, id_table):
    matches_link = []
    teams = []
    opponents = []
    date = []
    table_matches = soup_.find('table', id=id_table)
    rows = table_matches.find_all('tr')
    for row in rows:
        if (row.find('a') != None) & (len(row.find_all('td')) > 0):
            
            matches_link.append(row.find('a', href = True)['href'])
            date.append(row.find('a', href = True).contents[0])
            teams.append(row.find_all('td')[5].find('a').text)
            opponents.append(row.find_all('td')[6].find('a').text)
    return (date, matches_link, teams, opponents)

def organize_table(df):
    cols = df.columns.map('_'.join).tolist()
    cols = [col.split('_')[-1].lower() if 'Unnamed' in col else col.lower() for col in cols]
    treated_cols = []
    for word in manual_replace.keys():
        if word == 'nação':
            treated_cols.append('nacao')
        elif word == '#':
            treated_cols.append('num_camisa')
        elif '%' in word:
            treated_cols.append(word.replace('%', '_porc'))
        elif '.' in word:
            treated_cols.append(word.replace('.', ''))
        else:
            treated_cols.append(word)
    
    df.columns = treated_cols

    return df


# Main

def main():
    

    # Team to analyze
    team_analyzed = 'Brazil'

    # Seasons to analyze
    last_n_seasons = 3

    # URL to find stats about soccer players
    url = 'https://fbref.com/'
    world_cup_url = 'pt/comps/1/FIFA-World-Cup-Estatisticas'

    # Get world cup soup obj
    soup_wc = get_page_obj(url + world_cup_url)

    # Extract the teams of a group
    team_dict = extract_teams(url, soup_wc, 'results202211G_overall')            

    # Extract players soup obj
    soup_players = get_page_obj(team_dict[team_analyzed])

    # Get all the players 
    player_dict = extract_players(url, soup_players, 'stats_standard_4')



    # Empty dataframe      
    player_stats_df = pd.DataFrame()

    print(f'Getting matches stats for {team_analyzed} in the last {last_n_seasons} seasons...')
    for player in tqdm(list(player_dict.keys())):
        if int(player_dict[player][-1]) < 3:
            # It skips the players that have less than 3 matches in the Brazil team
            continue
        else:
            # Infos about the player
            player_info = player_dict[player]

            # Extract the soup obj for the player page
            soup_player = get_page_obj(player_info[0])

            # Extract the link for each season       
            stats_link = extract_player_season(soup_player, "bottom_nav_container")
            
            # Check all the seasons
            for stat_link in stats_link[-last_n_seasons:]:
                soup_season = get_page_obj(url[:-1] + stat_link)
                # Get the match link and the team to filter stats
                match_info = extract_player_matches(soup_season, 'matchlogs_all')
                # Iterate over the matches
                for date, link, team, opponent in zip(match_info[0],match_info[1], match_info[2], match_info[3] ):
                    
                    stats = extract_matches_stats(url[:-1] + link, team)
                    stats = stats.loc[:, ~stats.columns.duplicated()]
                    
                    stats['data'] = date
                    stats['equipe'] = team
                    stats['oponente'] = opponent

                    
                    # Concatenate the files
                    player_stats_df = pd.concat([player_stats_df, stats], axis = 0, ignore_index=True, sort=False)
                
        
    # Some players are from the same team and the stats are duplicated for the match
    player_stats_df = player_stats_df.drop_duplicates()

    # Organize Columns with Date at first
    player_stats_df = player_stats_df.loc[:, ['data', 'equipe', 'oponente'] + player_stats_df.drop(['data', 'equipe', 'oponente'], axis = 1).columns.tolist()]
        
    # Save to a CSV
    player_stats_df.to_csv('Brazil_world_cup_2022.csv')




if __name__ == '__main__':
    main()



