import time
import schedule
import json
import sys
import telegram
import datetime


def open_configs(filename='config.json'):
    with open(filename) as json_file:
        configs = json.load(json_file)
        token = configs["user"]["token"]
        chatid = configs["user"]["chatid"]
        return token, chatid


def telegram_bot_sendtext(bot_message):
    bot_token, bot_chatid = open_configs()
    bot = telegram.Bot(token=bot_token)

    # print("token: " + bot_token + "  chatid: " + bot_chatid)
    bot.send_message(chat_id=bot_chatid, text=bot_message)


def telegram_send_image(imageFile='data/prediction.png'):
    bot_token, bot_chatid = open_configs()
    bot = telegram.Bot(token=bot_token)

    bot.send_photo(chat_id=bot_chatid, photo=open(imageFile, 'rb'))


def generate_report():
    today = datetime.date.today()
    # test message combination
    stock_name = "삼성전자"
    stock_price = "1,000,000"
    message = "{:%d %b %Y} \n {} : {}".format(today, stock_name, stock_price)
    return message


def send_report():
    message = generate_report()

    telegram_bot_sendtext(message)
    telegram_send_image()


def test():
    send_report()

test()

'''
schedule.every().day.at("9:00").do(report)

while True:
    schedule.run_pending()
    time.sleep(1)
'''
