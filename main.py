import random
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1"
    # Add more User-Agent strings as needed
]
random_user_agent = random.choice(user_agents)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f"--user-agent={random_user_agent}")
chrome_options.add_experimental_option("detach", True)


# driver = webdriver.Chrome()
# driver.get('https://www.kinopoisk.ru/')
# driver.close()


class Parser:
    # genres_url = '/lists/categories/movies/8'
    # top_250_url = '/lists/movies/top250'

    def __init__(self, chrome_driver: webdriver.Chrome):
        self.driver: webdriver.Chrome = chrome_driver
        self.base_url: str = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'
        self.host: str = 'https://www.imdb.com'

    def get_genres(self):
        result = []
        self.driver.get(self.base_url)
        element = self.driver.find_element(By.CLASS_NAME, 'ipc-metadata-list')
        soup = BeautifulSoup(element.get_attribute('outerHTML'), "html.parser")
        for idx, item in enumerate(soup.find_all('li', class_='ipc-metadata-list-summary-item'), start=1):
            if idx == 20:
                break
            title = item.find('h3', class_='ipc-title__text').get_text(strip=True)
            print(title)
            link = item.find('a', class_='ipc-title-link-wrapper')['href']
            self.driver.get(self.host + link)
            inner_html = self.driver.page_source
            inner_soup = BeautifulSoup(inner_html, 'html.parser')
            descr = inner_soup.find('span', {'data-testid': 'plot-xl'}).get_text()
            # slogan = inner_soup.find('section', {
            #     'class': 'ipc-page-section ipc-page-section--base celwidget',
            # })

            details_section = inner_soup.find('section', {'data-testid': 'Details'})
            country = (details_section.find('div', {'data-testid': 'title-details-section'})
                       .find('li', {'data-testid': 'title-details-origin'}).find('a').get_text(strip=True))
            year = inner_soup.find('div', class_='sc-1f50b7c-0').find_all('li')[0].get_text(strip=True)
            producer = inner_soup.find('li', {'data-testid': 'title-pc-principal-credit'}).find('div').get_text(
                strip=True)
            # print(producer)
            genre = (inner_soup.find('div', {'data-testid': 'genres'})
                     .find('div', class_='ipc-chip-list__scroller'))
            genre = [i.get_text(strip=True) for i in genre.find_all('span')]
            budget_section = inner_soup.find('section', {'data-testid': 'BoxOffice'})
            try:
                budget = (budget_section.find('li', {'data-testid': 'title-boxoffice-budget'})
                .find('span', class_='ipc-metadata-list-item__list-content-item')
                .get_text(strip=True).split('(')[0])
            except:
                budget = 0
            try:
                fees_usa = (budget_section.find('li', {'data-testid': 'title-boxoffice-grossdomestic'})
                .find('span', class_='ipc-metadata-list-item__list-content-item')
                .get_text(strip=True).split('(')[0])
            except:
                fees_usa = 0

            try:
                fees_world = (budget_section.find('li', {'data-testid': 'title-boxoffice-cumulativeworldwidegross'})
                .find('span', class_='ipc-metadata-list-item__list-content-item')
                .get_text(strip=True).split('(')[0])
            except:
                fees_world = 0
            poster = inner_soup.find('div', {'data-testid': 'hero-media__poster'}).find('img')['src']
            # print(poster)
            rating = inner_soup.find('div', {'data-testid': 'hero-rating-bar__aggregate-rating__score'}).find(
                'span').get_text(strip=True)
            photos_section = inner_soup.find('section', {'data-testid': 'Photos'}).find('div', {'data-testid': 'shoveler-items-container'})
            photos = [item['src'] for item in photos_section.find_all('img')]
            # print(photos)
            actors_section = inner_soup.find('section', {'data-testid': 'title-cast'})
            actors = actors_section.find('div', {'data-testid': 'shoveler-items-container'}).find_all('div', {
                'data-testid': 'title-cast-item'})
            actors = [actor.find('a', {'data-testid': 'title-cast-item__actor'}).get_text(strip=True) for actor in
                      actors]

            result.append({
                'title': title,
                'year': year,
                'producer': producer,
                'actors': actors,
                'description': descr,
                'rating': rating,
                'country': country,
                'budget': budget,
                'fees_usa': fees_usa,
                'fees_world': fees_world,
                'genre': genre,
                'poster': poster,
                'photos': photos
            })
            # break

        with open('movies.json', mode='w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)


parser = Parser(chrome_driver=webdriver.Chrome(options=chrome_options))
parser.get_genres()
