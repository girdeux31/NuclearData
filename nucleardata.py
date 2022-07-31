import os
import time
import requests
import tweepy
from dotenv import load_dotenv
from lxml import etree
from io import StringIO

# load environment variables

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
SLEEPING_TIME = float(os.getenv('SLEEPING_TIME'))

# define some parameters

infinite_loop = True
bot_id = '1528123312781549568'
max_mentions = 10
file = '.last'

emojis = dict()

emojis['nuclear'] = '☢️'
emojis['operation'] = '🔋'
emojis['shutdown'] = '🪫'
emojis['construction'] = '🚧'
emojis['time'] = '⌛️'

countries = list()

countries.append({'code': 'AR', 'flag': '🇦🇷', 'name': 'Argentina'})
countries.append({'code': 'AM', 'flag': '🇦🇲', 'name': 'Armenia'})
countries.append({'code': 'BD', 'flag': '🇧🇩', 'name': 'Bangladesh'})
countries.append({'code': 'BY', 'flag': '🇧🇾', 'name': 'Belarus'})
countries.append({'code': 'BE', 'flag': '🇧🇪', 'name': 'Belgium'})
countries.append({'code': 'BR', 'flag': '🇧🇷', 'name': 'Brazil'})
countries.append({'code': 'BG', 'flag': '🇧🇬', 'name': 'Bulgaria'})
countries.append({'code': 'CA', 'flag': '🇨🇦', 'name': 'Canada'})
countries.append({'code': 'CN', 'flag': '🇨🇳', 'name': 'China'})
countries.append({'code': 'CZ', 'flag': '🇨🇿', 'name': 'Czech Republic'})
countries.append({'code': 'FI', 'flag': '🇫🇮', 'name': 'Finland'})
countries.append({'code': 'FR', 'flag': '🇫🇷', 'name': 'France'})
countries.append({'code': 'DE', 'flag': '🇩🇪', 'name': 'Germany'})
countries.append({'code': 'HU', 'flag': '🇭🇺', 'name': 'Hungary'})
countries.append({'code': 'IN', 'flag': '🇮🇳', 'name': 'India'})
countries.append({'code': 'IR', 'flag': '🇮🇷', 'name': 'Iran'})
countries.append({'code': 'IT', 'flag': '🇮🇹', 'name': 'Italy'})
countries.append({'code': 'JP', 'flag': '🇯🇵', 'name': 'Japan'})
countries.append({'code': 'KZ', 'flag': '🇰🇿', 'name': 'Kazakhstan'})
countries.append({'code': 'KR', 'flag': '🇰🇷', 'name': 'Korea'})
countries.append({'code': 'LT', 'flag': '🇱🇹', 'name': 'Lithuania'})
countries.append({'code': 'MX', 'flag': '🇲🇽', 'name': 'Mexico'})
countries.append({'code': 'NL', 'flag': '🇳🇱', 'name': 'Netherlands'})
countries.append({'code': 'PK', 'flag': '🇵🇰', 'name': 'Pakistan'})
countries.append({'code': 'RO', 'flag': '🇷🇴', 'name': 'Romania'})
countries.append({'code': 'RU', 'flag': '🇷🇺', 'name': 'Russia'})
countries.append({'code': 'SK', 'flag': '🇸🇰', 'name': 'Slovakia'})
countries.append({'code': 'SI', 'flag': '🇸🇮', 'name': 'Slovenia'})
countries.append({'code': 'ZA', 'flag': '🇿🇦', 'name': 'South Africa'})
countries.append({'code': 'ES', 'flag': '🇪🇸', 'name': 'Spain'})
countries.append({'code': 'SE', 'flag': '🇸🇪', 'name': 'Sweden'})
countries.append({'code': 'CH', 'flag': '🇨🇭', 'name': 'Switzerland'})
countries.append({'code': 'TR', 'flag': '🇹🇷', 'name': 'Turkey'})
countries.append({'code': 'UA', 'flag': '🇺🇦', 'name': 'Ukraine'})
countries.append({'code': 'AE', 'flag': '🇦🇪', 'name': 'United Arab Emirates'})
countries.append({'code': 'GB', 'flag': '🇬🇧', 'name': 'United Kingdom'})
countries.append({'code': 'US', 'flag': '🇺🇸', 'name': 'United States'})


class Country:

    def __init__(self, country):

        self.code = country['code'].upper()
        self.name = country['name']
        self.flag = country['flag']
        self.url = r'https://pris.iaea.org/PRIS/CountryStatistics/CountryDetails.aspx?current=' + self.code
        self.xpath_tbody = r'//*[@id="content"]/div/table/tbody'
        self.xpath_script = r'//*[@id="content"]/div/div[2]/script[1]'

        self.tree = self._get_tree()
        self.nuclear_production = self._get_nuclear_production()
        self.non_nuclear_production = self._get_non_nuclear_production()
        self.nuclear_share = self._get_nuclear_share()
        self.plants = self._get_plants()

        self.operation_reactors, self.operation_power = self._get_operational_info()
        self.shutdown_reactors, self.shutdown_power = self._get_shutdown_info()
        self.construction_reactors, self.construction_power = self._get_construction_info()

    def _get_tree(self):

        # Set explicit HTMLParser
        parser = etree.HTMLParser()

        # Request page content
        response = requests.get(self.url)

        # Decode the page content from bytes to string
        html = response.content.decode("utf-8")

        # Create your etree with a StringIO object
        return etree.parse(StringIO(html), parser=parser)

    # just for debug
    def _write_tree(self, file):

        response = requests.get(self.url)

        with open(file, mode='wb') as d:
            d.write(response.content)

    def _get_nuclear_production(self):

        script = self.tree.xpath(self.xpath_script)[0]
        text = script.text.split('\n')[2].replace('var PieNuclearElectricityProduction =', '').replace(';', '').strip()
        return int(text) if text else None

    def _get_non_nuclear_production(self):

        script = self.tree.xpath(self.xpath_script)[0]
        text = script.text.split('\n')[3].replace('var PieNonNuclearElectricityProduction =', '').replace(';', '').strip()
        return int(text) if text else None

    def _get_nuclear_share(self):

        return self.nuclear_production / (self.nuclear_production + self.non_nuclear_production) * 100.0 if self.nuclear_production else 0.0

    def _get_plants(self):

        data = list()
        tbody = self.tree.xpath(self.xpath_tbody)[0]

        for tr in tbody:

            tds = tr.xpath('td')

            name = tds[0].xpath('a')[0].text.strip()
            status = tds[2].text.strip()
            power = int(tds[4].text.strip())

            data.append({'name': name, 'status': status, 'power': power})

        return data

    def _get_operational_info(self):

        data = [plant['power'] for plant in self.plants if plant['status'] == 'Operational']
        return len(data), sum(data)

    def _get_shutdown_info(self):

        data = [plant['power'] for plant in self.plants if plant['status'] == 'Permanent Shutdown']
        return len(data), sum(data)

    def _get_construction_info(self):

        data = [plant['power'] for plant in self.plants if plant['status'] == 'Under Construction']
        return len(data), sum(data)

    def get_tweet(self):

        return f'{self.flag} {self.name} Nuclear Information {self.flag}\n\n' \
               f'{emojis["operation"]} {self.operation_reactors} reactors in operation with {round(self.operation_power):.0f} MWe\n' \
               f'{emojis["shutdown"]} {self.shutdown_reactors} permanent shutdown reactors with {round(self.shutdown_power):.0f} MWe\n' \
               f'{emojis["construction"]} {self.construction_reactors} reactors under construction with {round(self.construction_power):.0f} MWe\n' \
               f'{emojis["nuclear"]} Nuclear share is {self.nuclear_share:.1f} %'


class World:

    def __init__(self):

        self.url = r'https://pris.iaea.org/PRIS/home.aspx'
        self.xpath_operation_reactors = r'//*[@id="MainContent_lblNuclearPowerReactorsInOperation"]'
        self.xpath_operation_power = r'//*[@id="MainContent_lblTotalNetInstalledCapacity"]'
        self.xpath_operation_time = r'//*[@id="MainContent_lblReactorYearsOfOperation"]'
        self.xpath_construction_reactors = r'//*[@id="MainContent_lblNuclearPowerReactorsUnderConstruction"]'

        self.tree = self._get_tree()

        self.operation_reactors = self._get_operational_reactors()
        self.operation_power = self._get_operational_power()
        self.operation_time = self._get_operational_time()
        self.construction_reactors = self._get_construction_reactors()

    def _get_tree(self):

        # Set explicit HTMLParser
        parser = etree.HTMLParser()

        # Request page content
        response = requests.get(self.url)

        # Decode the page content from bytes to string
        html = response.content.decode("utf-8")

        # Create your etree with a StringIO object
        return etree.parse(StringIO(html), parser=parser)

    # just for debug
    def _write_tree(self, file):

        response = requests.get(self.url)

        with open(file, mode='wb') as d:
            d.write(response.content)

    def _get_operational_reactors(self):

        text = self.tree.xpath(self.xpath_operation_reactors)[0].text
        return int(text.replace(' ', ''))

    def _get_operational_power(self):
        
        text = self.tree.xpath(self.xpath_operation_power)[0].text
        return int(text.replace(' ', ''))

    def _get_operational_time(self):
        
        text = self.tree.xpath(self.xpath_operation_time)[0].text
        return int(text.replace(' ', ''))

    def _get_construction_reactors(self):
        
        text = self.tree.xpath(self.xpath_construction_reactors)[0].text
        return int(text.replace(' ', ''))

    def get_tweet(self):

        return f'{emojis["nuclear"]} Worldwide Nuclear Information {emojis["nuclear"]}\n\n' \
               f'{emojis["operation"]} {self.operation_reactors} reactors in operation with {round(self.operation_power/1000):.0f} GWe\n' \
               f'{emojis["time"]} {self.operation_time} reactor-years of operation\n' \
               f'{emojis["construction"]} {self.construction_reactors} reactors under construction'

def get_country_from_tweet(text):

    for country in countries:
        if country['code'] in text or country['name'].lower() in text.lower():
            return country

    return None

def write_last_tweet_id(file, id):

    with open(file, 'w') as f:
        f.write(str(id))

def read_last_tweet_id(file):

    with open(file, 'r') as f:
        return int(f.read())


if __name__ == '__main__':

    while True:

        last_tweet_id = read_last_tweet_id(file) if os.path.isfile(file) else 0
        print(last_tweet_id)

        try:
   
            # authenticate client
            client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
                                   access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
            
            # get bot mentions
            tweets = client.get_users_mentions(id=bot_id, max_results=max_mentions, since_id=last_tweet_id, user_auth=True)

        except Exception as error:

            tweets = list()
            print('Error finding mentions')
            print('Error is ' + str(error))

        if tweets and tweets.data:

            for tweet in tweets.data:

                # print(tweet.text, tweet.id)
                country = get_country_from_tweet(tweet.text)
                object = Country(country) if country else World()
                text = object.get_tweet()
                # print(text)

                try:

                    # post tweet
                    client.create_tweet(text=text, in_reply_to_tweet_id=tweet.id)

                    if tweet.id > last_tweet_id:

                        last_tweet_id = tweet.id
                        write_last_tweet_id(file, tweet.id)

                    code = country['code'] if country else 'WR'

                    print(f'Tweet in response to tweet id {tweet.id} with code {code} at {time.strftime("%Y-%m-%d %H:%M:%S")}')

                except Exception as error:

                    print(f'Error sending tweet, its length is {len(text)}')
                    print('Error is ' + str(error))

        # put to sleep

        if infinite_loop:
            time.sleep(SLEEPING_TIME)
        else:
            break
 
