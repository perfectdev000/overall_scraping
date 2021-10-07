import re

import requests
from bs4 import BeautifulSoup
from dateutil import parser
import time 

def get_event_name_and_date(url):
    if 'eventbrite.' in url:
        return check_eventbrite(url)
    elif 'bigtickets.' in url:
        return check_bigticket(url)
    elif 'etix.' in url:
        return check_etix(url)
    elif 'frontgatetickets.' in url:
        return check_frontgate(url)
    elif 'ticketweb.' in url:
        return check_ticketweb(url)
    elif 'seetickets.us' in url:  
        return check_seetickets(url)
    elif 'showclix.' in url:  
        return check_showclix(url)


def make_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0.'}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return BeautifulSoup(r.content, 'html.parser')
    print(r.status_code, url)

def check_eventbrite(url):
    soup = make_request(url)
    try:
        name = soup.find('h1', {'class': 'text-body-large'}).text.strip()
    except:
        name = soup.find('h1', {'class': 'listing-hero-title'}).text.strip()
    try:
        date = soup.find('div', {'class': 'event-details__data'}).find('meta')['content']
    except TypeError:
        date = soup.find('time', {'class': 'clrfix'}).find('p').text.strip()
    if len(date)<2:
        date = str(soup.select("#event-page > main > div.js-hidden-when-expired.event-listing.event-listing--has-image > div.g-grid.g-grid--page-margin-manual > div > section.listing-info.clrfix > div.listing-info__body.l-sm-pad-vert-0.l-sm-pad-vert-6.clrfix.g-group.g-group--page-margin-reset > div > div > div.g-cell.g-cell-12-12.g-cell-md-4-12.g-offset-md-1-12.g-cell--no-gutters.l-lg-pad-left-6 > div > div:nth-child(4) > meta:nth-child(1)")).split('\"')[1]
    date = date.replace('–',' ').strip()
    if date.find('-')>0:
        date = date.replace('-',' ').strip()
    date = parser.parse(date).strftime('%Y-%m-%d')
    loc = [x.find_next('div', {'class': 'event-details__data'}) for x in soup.find_all('h3', {'class': 'label-primary l-mar-bot-2'}) if 'Location' in x.text][0]
    loc = loc.find_all('p')
    venue, loc = loc[0].text.strip(), loc[2].text.strip()
    name = name + " {} {}".format(venue, loc)
    return name, date



def check_bigticket(url):
    soup = make_request(url)
    try:
        name = soup.find('div', {'class': 'event-titles'}).find_next('h1').decode_contents()
        date = soup.find('div', {'class': 'event-titles'}).find_next('h4').decode_contents().split('<')[0]
        date = parser.parse(date).strftime('%Y-%m-%d')
        venue = soup.find('a', {'title': 'View on Google Maps', 'class':'tab-link'}).decode_contents().split('<br>')[0].replace('\n', '').replace('\t', '')
        loc = soup.find('a', {'title': 'View on Google Maps', 'class':'tab-link'}).decode_contents().split('<br>')[1].replace('\n', '').replace('\t', '')
        name = name + " {} {}".format(venue, loc)
    except:
        name = soup.find('div', {'class': 'event-info'}).find_next('h1').decode_contents()
        date = soup.find('span', {'class': 'event-dates'}).decode_contents().split('|')[0]
        date = parser.parse(date).strftime('%Y-%m-%d')
        venue = soup.find('span', {'class': 'event-city'}).decode_contents()
        name = name + " {} ".format(venue)
    return name, date


def check_etix(url):
    soup = make_request(url)
    name = soup.find('h1', {'itemprop': 'name'}).text.strip()
    date = soup.find('div', {'class': 'time'})
    date = date.find('meta', {'itemprop': 'startDate'})['content']
    # print(date)
    # date.find('script').extract()
    # date = date.text.strip()
    # date = re.sub(' +', ' ', date)
    date = parser.parse(date).strftime('%Y-%m-%d')
    venue = soup.find('div', {'class': 'location'}).text.strip()
    name = name + " " + venue
    return name, date


def check_frontgate(url):
    soup = make_request(url)
    try:
        name = soup.find('meta', {'property': 'og:title'})['content']
    except:
        name = soup.find('meta', {'property':'og:site_name'})['content']
    date = soup.find('div', {'class': 'date'}).text.strip().split('-')[0]
    date = date.split('\n')[0]
    date = parser.parse(date).strftime('%Y-%m-%d')
    venue = soup.find('div', {'class': 'venue'}).text.replace('at', '').strip()
    adr = soup.find('div', {'class': 'address'}).text.strip()
    adr = adr.split(',')
    adr = ','.join(adr[-2:])
    name = name + " " + venue + " " + adr
    return name, date


def check_ticketweb(url):
    soup = make_request(url)
    name = soup.find('h1', {'class': 'title'}).find('span', {'class': 'big'}).text.strip()
    date = soup.find('div', {'class': 'info-item info-time'}).find('h4').text.strip()
    date = parser.parse(date).strftime('%Y-%m-%d')
    venue = soup.find('a', {'href': '#', 'data-ng-click': "visible()", 'class': 'theme-title'})
    adr = venue.find_next('span').find_next('span').text.strip()
    venue = venue.text.strip()
    name = name + " " + venue + " " + adr

    return name, date

def check_seetickets(url):
    soup = make_request(url)
    name = soup.find('h1', {'class': 'event-h2'}).text.strip()
    date = soup.find('time', {'itemprop': 'startDate'})['datetime']
    date = parser.parse(date).strftime('%Y-%m-%d')
    venue = soup.find('p', {'class': 'float-r'}).find_next('h5').decode_contents()
    adr = soup.find('input', {'type':'hidden', 'id':'locationaddress'})['value']
    # print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{adr}")
    # time.sleep(3000)
    name = name + " " + venue + " " + adr

    return name, date

def check_showclix(url):
    soup = make_request(url)
    name = soup.find('h1', {'class':'showtitle'}).text.strip()
    date = soup.find('div', {'class':'event_date'}).text.strip()
    date = parser.parse(date.split('-')[0]).strftime('%Y-%m-%d')
    venue = soup.find('span', {'class':'venuename'}).text.strip()
    adr = soup.find('span', {'class':'venuename'}).find_next('span').find_next('span').text.strip()
    name = name + " " + venue + " " + adr
    return name, date
#
# for url in ['https://basscanyonfestival.frontgatetickets.com/event/i8co6kruzz405we8',
#             'https://www.ticketfly.com/purchase/event/1803134/tfly',
#             'https://www.eventbrite.com/e/casablanca-the-montalban-rooftop-movies-tickets-54783106747?aff=erelexpmlt#tickets',
#             'https://www.etix.com/ticket/p/3379234/hartmut-sauers-musikkabinettduosassoninocturne-wandel-durch-die-nacht-dresdensch%C3%B6nfeld-deutschlands-zauberschloss?partner_id=430',
#             'https://www.ticketweb.com/event/lords-of-acid-with-special-brick-by-brick-tickets/9072935?REFERRAL_ID=twflash']:
#     print('for url', url)
#     print(get_event_name_and_date(url))
