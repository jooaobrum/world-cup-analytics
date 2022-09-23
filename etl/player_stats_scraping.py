# %% 

# Imports
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


# URL to find stats about soccer players
url = 'https://fbref.com/'

# Team to be analyzed
team_analyzed = 'Brazil'

# Selenium Options 
options = Options()
options.headless = True

# Initiate the selenium driver with firefox
driver = webdriver.Firefox(options=options)
# Get the access 
driver.get(url + '/pt/comps/1/FIFA-World-Cup-Estatisticas')

# Get the html page source
page_source = driver.page_source


# %%
# Create the soup object
soup = BeautifulSoup(page_source, 'lxml')


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
            

team_dict[team_analyzed]
# %%
# Move to the team squad
driver.get(team_dict[team_analyzed])

# Get the html page source
page_source = driver.page_source

