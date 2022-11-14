import requests
from bs4 import BeautifulSoup


def parse_football(count: int):
    url = 'https://football.ua/'
    i = 0
    data = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    contents = soup.select('#ctl00_columnRight > article > ul > li')

    for content in contents:
        try:
            time = content.find('div').text
            news = content.find('a').text
            print(f'{time}: {news}')
            data.append(f'{time}: {news}')
        except AttributeError:
            continue

        i += 1
        if i == count:
            return data


if __name__ == '__main__':
    store = parse_football(10)
    print(store)
