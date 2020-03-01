import datetime
import requests
import dateutil.parser
import json

def check_time(user_data):
    time_user = dateutil.parser.parse(user_data.date.isoformat()[:-6])
    now_time = dateutil.parser.parse(datetime.datetime.now().isoformat())
    if not  now_time - time_user > datetime.timedelta(minutes=1440):
        time_left = datetime.timedelta(minutes=1440) - (now_time - time_user)
        hour = str((time_left.seconds//60//60)%60)
        minutes = str((time_left.seconds//60)%60)
        seconds = str(time_left.seconds%60)
        seconds = seconds if len(seconds) == 2 else '0'+seconds
        str_time_left = hour + ":" + minutes + ":" + seconds
        print time_left.seconds
        return time_left.seconds
    else:
        return None

def hash_ip(ip):
    str_finish = ""
    for el in map(int,ip.split('.')):
        str_finish = str_finish + chr((((el - (el % 16)) / 16 ) % 16)+ord('a')) + chr((el % 16)+ord('a'))
    return str_finish 

def send_money(wallet,coin,reffer):
    r = requests.post("https://faucetbox.com/api/v1/send", data={'api_key': '3dLUpLuDN49biUuK31OI1GtQRQ1uV', \
                                                                               'to': wallet,\
                                                                               'amount':coin})
    if r.status_code == 200:
        status = json.loads(r.text)
        if status['status'] == 200:
            r = requests.post("https://faucetbox.com/api/v1/send", data={'api_key': '3dLUpLuDN49biUuK31OI1GtQRQ1uV', \
                                                                           'to': reffer,\
                                                                           'amount':int(coin/2),'referral':True})
            return (True,)
        else:
            info_text = "bad address"
    else:
        info_text = "server error"
    return (False,info_text)
