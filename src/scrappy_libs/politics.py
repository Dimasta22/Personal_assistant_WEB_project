import requests
from bs4 import BeautifulSoup


def parse_finance(count: int):
    url = 'https://ua.korrespondent.net/'
    i = 0
    data = {}
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    contents = soup.select('div.article')
    for content in contents:
        try:
            time = content.find('div', attrs={'class': 'article__time'}).text
            news = content.find('div', attrs={'class': 'article__title'}).find('a').text
            href = content.find('div', attrs={'class': 'article__title'}).find('a')['href']
            data.update({f'{time}: {news.replace("Сюжет", "")}': href})
        except AttributeError:
            continue
        i += 1
        if i == count:
            return data


if __name__ == '__main__':
    store = parse_finance(10)
    print(store)
