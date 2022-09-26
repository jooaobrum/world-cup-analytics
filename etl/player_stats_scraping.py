 

# Imports
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm
import requests


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

def extract_player_stats(url, stats_link, last_n_seasons):
    player_seasons = pd.DataFrame()
    for stats_link_season in stats_link[-last_n_seasons:]:
        print(stats_link_season)    
        # Get the player stats with pandas
        player_stats = pd.DataFrame(pd.read_html(url + stats_link_season[1:])[0])

        # Change columns 
        player_stats.columns = player_stats.columns.get_level_values(1)


        
        # Organize columns 
        player_stats = player_stats.loc[:, player_stats.columns.tolist()[-3:] + player_stats.columns.tolist()[:-3]]
        player_seasons = pd.concat([player_seasons, player_stats], axis = 0, ignore_index=True)
    return player_seasons

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

    # Columns to fill the dataframe
    valid_columns = ['Nome', 'Posicao', 'Idade', 'Data', 'Dia', 'Camp.', 'Rodada', 'Local',
        'Resultado', 'Equipe', 'Oponente', 'Início', 'Pos.', 'Min.', 'Gols',
        'Assis.', 'PB', 'PT', 'TC', 'CaG', 'CrtsA', 'CrtV', 'Contatos',
        'Pressão', 'Div', 'Crts', 'Bloqueios', 'xG', 'npxG', 'xA', 'SCA', 'GCA',
        'Cmp', 'Att', 'Cmp%', 'Progresso', 'Conduções', 'Succ', 'Desativado', 'TklW',
        'OG','Fts','PKcon','Pênaltis convertidos','FltsP','Crz', 'Relatório da Partida']

    # Empty dataframe      
    player_stats_df = pd.DataFrame(columns = valid_columns)


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
            
            # Get the stats for the player in the last n seasons
            player_stats = extract_player_stats(url, stats_link, last_n_seasons)
            
            # Add Other players info
            player_stats['Nome'] = player
            player_stats['Posicao'] = player_info[1]
            player_stats['Idade'] = player_info[2]
        
        # Fill the columns that don't contain info with nan 
        for col in valid_columns:
            if col not in player_stats.columns.tolist():
                player_stats[col] = np. nan  
        player_stats = player_stats.loc[:, ~player_stats.columns.duplicated()]
        
        # Fill the players table with all matches info in the season
        player_stats_df = pd.concat([player_stats_df, player_stats[valid_columns]], axis = 0, ignore_index=True, sort=False)
    # Save the data to a csv 
    player_stats_df.to_csv(f'{team_analyzed}_world_cup_2022.csv')
    
if __name__ == '__main__':
    main()