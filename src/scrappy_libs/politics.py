import requests
from bs4 import BeautifulSoup


def parse_finance(count: int):
    url = 'https://ua.korrespondent.net/'

    data = []
    i = 0
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    contents = soup.select('div.article.text_bold')

    for content in contents:
        try:
            time = content.find('div', attrs={'class': 'article__time'}).text
            news = content.find('div', attrs={'class': 'article__title'}).find('a').text
            data.append(f'{time}: {news}')
        except AttributeError:
            continue

        i += 1
        if i == count:
            return data


if __name__ == '__main__':
    store = parse_finance(10)
    print(store)
