import requests
from bs4 import BeautifulSoup


def parse_city():
    CITY = {}
    url = 'https://sinoptik.ua/%D1%83%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    contents = soup.select('.clearfix > ul > li')

    for content in contents:
        city = content.find('a').text
        href = content.find('a')['href']
        CITY.update({city: href})
    return CITY


def parse_weather(city: str):
    data = []
    city_dict = parse_city()
    response = requests.get('https:' + city_dict[city])
    soup = BeautifulSoup(response.text, 'html.parser')

    contents = soup.select('.main')
    for content in contents:
        day = content.find('p', attrs={'class': 'date'}).text
        month = content.find('p', attrs={'class': 'month'}).text
        min_temperature = content.find('div', attrs={'class': 'min'}).text
        max_temperature = content.find('div', attrs={'class': 'max'}).text
        try:
            day_of_the_week = content.find('p', attrs={'class': 'day-link'}).text
        except AttributeError:
            day_of_the_week = content.find('p').find('a').text
        data.append(f'{day} {month}: {day_of_the_week}: {min_temperature}: {max_temperature}')
    return data


if __name__ == '__main__':
    store = parse_weather('Днепр')
    print(store)
    #print(CITY)
