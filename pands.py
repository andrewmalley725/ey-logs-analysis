import pandas as pd

df = pd.read_excel('network-logs.xlsx')

COUNTRIES = ['USA', 'England', 'Brazil']

CITIES = ['Los Angeles', 'New York City', 'Charlotte', 'London', 'Sao Paulo']

def get_city(df):
    cities = []
    lst = list(df['Unnamed: 5'])
    for i in lst:
        city = ''
        index = i.find('City')
        index += 6
        while i[index] != '\n':
            city += i[index]
            index += 1
        cities.append(city)
    df['City'] = cities
    return df

def get_country(df):
    countries = []
    lst = list(df['Unnamed: 5'])
    for i in lst:
        country = ''
        index = i.find('Country')
        index += 9
        while i[index] != '\n':
            country += i[index]
            index += 1
        countries.append(country)
    df['Country'] = countries
    return df

def get_ip(df):
    addresses = []
    lst = list(df['Unnamed: 5'])
    for i in lst:
        ip = ''
        index = i.find('Address') + 9
        while i[index] != '\n':
            ip += i[index]
            index += 1
        addresses.append(ip)
    df['IP Address'] = addresses
    return df

tasks = df[(df['Task Category'] == 'Authentication')&(df['Unnamed: 5'].str.contains('success'))]

myData = get_ip(get_country(get_city(tasks)))[['Date and Time', 'City', 'Country', 'IP Address']]

afterHours = myData[(myData['Date and Time'].dt.hour < 8) | (myData['Date and Time'].dt.hour > 20)]

breaches = myData[~(myData['City'].isin(CITIES)) & ~(myData['Country'].isin(COUNTRIES))]

IP_addresses = set(list(breaches[(breaches['Country'] == 'Russia')]['IP Address'].sort_values()))

print(breaches.sort_values('IP Address'))