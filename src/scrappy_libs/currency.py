import requests
from bs4 import BeautifulSoup


def parse_currency():
    url = 'https://finance.i.ua/'

    data = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    contents_column = soup.select('.widget-currency_bank > .data_container > .-important > thead > tr > td')
    contents_money = soup.select('.widget-currency_bank > .data_container > .-important > tbody > tr > th')
    contents_lines = soup.select('.widget-currency_bank > .data_container > .-important > tbody > tr > td')

    for content_column in contents_column:
        column_name = content_column.text
        data.append(f'{column_name[:7]}')

    for content_line in contents_money:
        line_value = content_line.text
        data.append(f'{line_value[:7]}')

    for content_line in contents_lines:
        line_value = content_line.text
        data.append(f'{line_value[:7]}')
    return data


if __name__ == '__main__':
    store = parse_currency()
    print(store)
