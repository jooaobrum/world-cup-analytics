# %% 

# Imports
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
 
# %% 
# URL to find stats about soccer players
url = 'https://fbref.com/'

# Team to analyze
team_analyzed = 'Brazil'

# Seasons to analyze
last_n_seasons = 2 

# Selenium Options 
options = Options()
options.headless = True

# Initiate the selenium driver with firefox
driver = webdriver.Firefox(options=options)
# Get the access 
driver.get(url + '/pt/comps/1/FIFA-World-Cup-Estatisticas')

# Get the html page source
page_source_wc = driver.page_source


# %%
# Create the soup object
soup = BeautifulSoup(page_source_wc, 'lxml')


# Extract the table of G group
table = soup.find('table', id="results202211G_overall")
# Extract all the rows (that contains the teams)
rows = table.findAll('tr')

team_dict = {}
# Fill a dictionary with the team and the link to the squad
for row in rows:
    cols = row.find_all('td')
    for col in cols:
        if col.find('span') != None:
            team_dict[col.find('span')['title']] = url + col.find('a', href = True)['href']
            
# %%
# Move to the team squad
driver.get(team_dict[team_analyzed])

# Get the html page source
page_source_team = driver.page_source

# Create the soup object
soup = BeautifulSoup(page_source_team, 'lxml')
# %%
# Extract the players
table_players = soup.find('table', id="stats_standard_4")
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


# %%
player_stats_df = pd.DataFrame()
for player in tqdm(list(player_dict.keys())):
    if int(player_dict[player][-1]) < 3:
        # It skips the players that have less than 3 matches in the Brazil team
        continue
    else:
        player_info = player_dict[player]

        

        # Move to the player page
        driver.get(player_info[0])

        # Get the html page source
        page_source_player = driver.page_source

        # Create the soup object
        soup = BeautifulSoup(page_source_player, 'lxml')

        
        # Find the link for each stats
        hist_div = soup.find("div", {"id": "bottom_nav_container"})
        stats_link = []
        for tag in hist_div.find_all('ul'):
            tags_a = tag.find_all('a')
            for hrefs in tags_a:
                if ('summary' in hrefs['href']) & ('nat_tm' not in hrefs['href']):
                    stats_link.append(hrefs['href'])
        
        for stats_link_season in stats_link[-last_n_seasons:]:
            

           
            # Get the player stats with pandas
            player_stats = pd.DataFrame(pd.read_html(url + stats_link_season[1:])[0])

            # Change columns 
            player_stats.columns = player_stats.columns.get_level_values(1)


            # Add Other players info
            player_stats['Nome'] = player
            player_stats['Posicao'] = player_info[1]
            player_stats['Idade'] = player_info[2]


            # Organize columns 
            player_stats = player_stats.loc[:, player_stats.columns.tolist()[-3:] + player_stats.columns.tolist()[:-3]]

        # Fill the players table with all matches info in the season
        player_stats_df = pd.concat([player_stats_df, player_stats], ignore_index=True, sort=False)


