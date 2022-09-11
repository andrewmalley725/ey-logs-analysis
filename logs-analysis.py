import json
import pandas as pd

df = pd.read_excel('network-logs.xlsx').to_dict('records')

OPEN = 8

CLOSE = 20

COUNTRIES = ['USA', 'England', 'Brazil']

CITIES = ['Los Angeles', 'New York City', 'Charlotte', 'London', 'Sao Paulo']

def get_city(msg):
    city = ''
    index = msg.find('City')
    index += 6
    while msg[index] != '\n':
        city += msg[index]
        index += 1
    if city in CITIES:
        return True, city
    return False, city
    
def get_country(msg):
    country = ''
    index = msg.find('Country')
    index += 9
    while msg[index] != '\n':
        country += msg[index]
        index += 1
    if country in COUNTRIES:
        return True, country
    return False, country

def ip_address(msg):
    address = ''
    index = msg.find('Address')
    index += 9
    while msg[index] != '\n':
        address += msg[index]
        index += 1
    return address

def ip_address_occurrence(dit):
    addresses = {}
    for i in dit:
        if i['Task Category'] == 'Authentication':
            msg = i['Unnamed: 5']
            if not get_country(msg)[0]:
                address = ip_address(msg)
                if address not in addresses:
                    addresses[address] = {
                        'COUNTRY': get_country(msg)[1],
                        'ATTEMPTS': 0,
                        'TIMES': []
                    }
                    addresses[address]['TIMES'].append(str(i['Date and Time']))
                else:
                    addresses[address]['ATTEMPTS'] += 1
                    addresses[address]['TIMES'].append(str(i['Date and Time']))

    return addresses
            
def breaches(dit):
    after_hours = []
    breaches = []
    for i in dit:
        msg = i['Unnamed: 5']
        if (i['Date and Time'].hour < OPEN or i['Date and Time'].hour > CLOSE) and i['Task Category'] == 'Authentication' and get_country(msg):
            after_hours.append(i)
        if i['Task Category'] == 'Authentication':
            if not get_country(msg)[0] and 'success' in msg:
                breaches.append(i)
    return breaches, after_hours

if __name__ == '__main__':
    
    def breach_list():
        for i in breaches(df)[0]:
            print(i['Unnamed: 5'])

    def num_breaches():
        print(len(breaches(df)[0]))

    def json_ip():
        json_object = json.dumps(ip_address_occurrence(df), indent = 4)
        print(json_object)

    def duplicate_times():
        for i in range(len(df)):
            count = 0
            if df[i]['Task Category'] == 'Authentication':
                _ip_address = ip_address(df[i]["Unnamed: 5"])
                current = str(df[i]['Date and Time'])
                for j in df:
                    if j['Task Category'] == 'Authentication':
                        if str(j['Date and Time']) == current and ip_address(j["Unnamed: 5"]) == _ip_address:
                            count += 1
            if count > 1:
                print(json.dumps({
                    'IP Address': ip_address(df[i]['Unnamed: 5']),
                    'Location': get_city(df[i]['Unnamed: 5'])[1]+ ', ' + get_country(df[i]['Unnamed: 5'])[1],
                    'Count': count,
                    'Time': str(df[i]['Date and Time'])
                }, indent=4))

    def time_range():
        instances = []
        for i in df:
            if i['Task Category'] == 'Authentication':
                obj = {
                    'IP Address': ip_address(i['Unnamed: 5']),
                    'Location': get_city(i['Unnamed: 5'])[1]+ ', ' + get_country(i['Unnamed: 5'])[1],
                    'Times': []
                }
                if obj not in instances:
                    instances.append(obj)
        return instances

    def times():
        instances = time_range()
        for i in instances:
            ip = i['IP Address']
            for j in df:
                if j['Task Category'] == 'Authentication':
                    dfip = ip_address(j['Unnamed: 5'])
                    if dfip == ip:
                        if len(i['Times']) > 0:
                            if pd.Timedelta(j['Date and Time'] - i['Times'][len(i['Times']) - 2]).seconds <= 30:
                                i['Times'].append(j['Date and Time'])
                                i['Times'].append('Success: ' + str('success' in j['Unnamed: 5']))
                        else:
                            i['Times'].append(j['Date and Time'])
                            i['Times'].append('Success: ' + str('success' in j['Unnamed: 5']))
        return instances
                
    def get_times():           
        for i in times():
            if len(i['Times']) > 2:
                print()
                print(i)
                print()

    get_times()

            