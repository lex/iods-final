# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import codecs
import urllib
import re
import time
import requests
import traceback

minimum_number_of_beers_for_brewery = 80
output_file = '../data/beers.csv'
base_url = 'https://www.ratebeer.com{}'
brewery_base_url = 'https://www.ratebeer.com/Ratings/Beer/ShowBrewerBeers.asp?BrewerID={}'
breweries_by_country_urls = [
    'https://www.ratebeer.com/breweries/finland/0/71/',
    'https://www.ratebeer.com/breweries/estonia/0/67/',
    'https://www.ratebeer.com/breweries/czech-republic/0/56/',
    'https://www.ratebeer.com/breweries/belgium/0/23/',
    'https://www.ratebeer.com/breweries/scotland/0/241/',
]


def main():
    print '[+] Writing csv header'

    with codecs.open(output_file, 'w', encoding='utf8') as f:
        headers = [
            '', 'retired', 'brewery', 'country', 'styles', 'score',
            'score_style', 'ratings', 'weighted_avg_score', 'special',
            'calories', 'abv'
        ]

        f.write(';'.join('"{}"'.format(header) for header in headers))
        f.write('\n')

    for i, country_url in enumerate(breweries_by_country_urls):
        print '[*] Scraping country {}/{}'.format(
            i + 1, len(breweries_by_country_urls))
        url = country_url

        scrape_country(url)

    print '[+] Done'


def scrape_country(url):
    try:
        r = get_url_contents(url)
        soup = BeautifulSoup(r.text, 'html5lib')
        country = soup.find('h1').text.replace(' Breweries', '')
        print country
        body = soup.find('div', attrs={'class': 'tab-content'})
        breweries = body.find_all('tr')
        selected_breweries = []

        for b in breweries:
            columns = b.find_all('td')
            if not columns:
                continue

            number_of_beers = int(columns[2].text.lstrip())

            if number_of_beers >= minimum_number_of_beers_for_brewery:
                brewery_url = b.find('a', href=True)
                if brewery_url and brewery_url['href']:
                    m = re.search('\/(\d+)\/$', brewery_url['href'])
                    if m:
                        selected_breweries.append(m.group(1))

        for i, url in enumerate(selected_breweries):
            print ' [*] Scraping brewery {}/{}'.format(i + 1,
                                                       len(selected_breweries))
            scrape_brewery(brewery_base_url.format(url), country)
    except Exception as e:
        print e


def scrape_brewery(url, country):
    try:
        r = get_url_contents(url)
        soup = BeautifulSoup(r.text, 'html5lib')
        beers = soup.find_all('tr')

        for i, b in enumerate(beers):
            print '  [*] Scraping beer {}/{}'.format(i + 1, len(beers))
            u = b.find('a', href=True)
            if u and u['href']:
                scrape_beer(base_url.format(u['href']), country)
                time.sleep(2)
    except Exception as e:
        traceback.print_exc()


# works for me???
def scrape_beer(url, country):
    try:
        r = get_url_contents(url)
        soup = BeautifulSoup(r.text, 'html5lib')

        # check for aliased beer

        aliased = soup.find(
            'a', attrs={'class': 'medium orange awesome'}, href=True)
        if aliased and aliased['href']:
            print '    [!] Found an aliased beer!'
            r = get_url_contents(base_url.format(aliased['href']))
            soup = BeautifulSoup(r.text, 'html5lib')

        body = soup.find('div', attrs={'class': 'row columns-container'})
        header = soup.find('div', attrs={'class': 'user-header'})

        name = soup.find('h1').text.strip().replace(u'\x92', '\'')
        retired = not not soup.find(
            'label', attrs={'title': 'Currently out of production'})
        brewery = body.find(
            'a', attrs={'itemprop': 'brand'}).text.strip().replace(u'\x92',
                                                                   '\'')

        styles = body.find_all('a', href=re.compile('^\/beerstyles\/'))

        rating = body.find('div', attrs={'class': 'ratingValue'})
        rating = rating.text.strip() if rating else ''

        style_rating = body.find(
            'div',
            attrs={
                'style':
                'font-size: 25px; font-weight: bold; color: #fff; padding: 20px 0px; '
            })
        style_rating = style_rating.text.strip()[:-5] if style_rating else ''

        raw_stats = body.find('div', attrs={'stats-container'}).find('small')
        stats_split = raw_stats.text.split(u'\xa0\xa0')
        stats = [stat.lstrip().split(u': ') for stat in stats_split]
        stats_dict = {}

        for raw_stat in stats:
            stats_dict[raw_stat[0]] = raw_stat[1]

        ratings_count = stats_dict.get(u'RATINGS', '')
        weighted_average = stats_dict.get(u'WEIGHTED AVG', '')
        seasonal = stats_dict.get(u'SEASONAL', 'no')
        calories = stats_dict.get(u'EST. CALORIES', '')
        abv = stats_dict.get(u'ABV', '')

        # remove unnecessary characters
        weighted_average = weighted_average[:-2] if weighted_average else ''
        abv = abv[:-1] if abv else ''

        s = u'{};{};{};{};{};{};{};{};{};{};{};{}'.format(
            u'"{}"'.format(name), u'T' if retired else u'F',
            u'"{}"'.format(brewery), u'"{}"'.format(country),
            u'"{}"'.format(','.join(style.text.strip() for style in styles)),
            rating, style_rating, ratings_count, weighted_average,
            u'"{}"'.format(seasonal), calories, abv)
        print s

        with codecs.open(output_file, 'a', encoding='utf8') as f:
            f.write(s)
            f.write('\n')

    except Exception as e:
        traceback.print_exc()


def get_url_contents(url):
    # more desktop friendly user agent
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }

    response = requests.get(url, headers=headers)

    return response


if __name__ == "__main__":
    main()
