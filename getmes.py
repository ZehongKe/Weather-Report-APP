import requests
from datetime import datetime, timedelta

api_key = "736cdedc3150498b9c04196466b17dd5"
city_list = []



#获取查询城市代码，支持模糊搜索
def city_data(lan, city): 
    url = f"https://geoapi.qweather.com/v2/city/lookup?location={city}&key={api_key}&lang={lan}"
    response = requests.get(url)
    data = response.json()
    return data

#获得实时天气信息
def weathernow(lan, citycode):
    url = f"https://devapi.qweather.com/v7/weather/now?location={citycode}&key={api_key}&lang={lan}"
    response = requests.get(url)
    data = response.json()
    weather_data = data['now']
    update_time = data['updateTime']
    return (update_time, weather_data)

#获得未来24h天气情况
def weatherfeature(lan, citycode): 
    url = f"https://devapi.qweather.com/v7/weather/24h?location={citycode}&key={api_key}&lang={lan}"
    response = requests.get(url)
    data = response.json()
    weather_datas = data['hourly']
    update_time = data['updateTime']
    return (update_time, weather_datas)

#获取未来7天天气预报
def weather7d(lan, citycode):
    url = f"https://devapi.qweather.com/v7/weather/7d?location={citycode}&key={api_key}&lang={lan}"
    response = requests.get(url)
    data = response.json()
    weather_datas = data['daily']
    update_time = data['updateTime']
    return (update_time, weather_datas)

#获得预警信息，可能无信息为空
def getwarn(lan, citycode): 
    url = f"https://devapi.qweather.com/v7/warning/now?location={citycode}&key={api_key}&lang={lan}"
    response = requests.get(url)
    data = response.json()
    update_time = data['updateTime']
    warn_data = data['warning']
    return  (update_time,warn_data)

#将实时天气信息进行文字输出
def outputweatherhour(lan, weather_data):
    if lan == 'cn':
        print('实时温度：{}℃'.format(weather_data['temp']))
        print('体感温度：{}℃'.format(weather_data['feelsLike']))
        print('天气：{}'.format(weather_data['text']))
        print('风向风力：{}{}级'.format(weather_data['windDir'],weather_data['windScale']))
        print('相对湿度：{}'.format(weather_data['humidity']))

    # elif lan == 'en':

#将未来24h天气信息进行文字输出
def outputweatherday(lan, weather_data):
    if lan == 'cn':
        print('日期：{}'.format(weather_data['fxDate']))
        print('最高温度：{}℃'.format(weather_data['tempMax']))
        print('最低温度：{}℃'.format(weather_data['tempMin']))
        print('天气：{}'.format(weather_data['textDay']))
        print('风向风力：{}{}级'.format(weather_data['windDirDay'],weather_data['windScaleDay']))
        print('相对湿度：{}'.format(weather_data['humidity']))
        print('日出时间：{} 日落时间：{}'.format(weather_data['sunrise'],weather_data['sunset']))

    # elif lan == 'en':

# dtime,warn=getwarn(lan,city_data(lan, 'sssss')) #缺少无预警信息时的返回