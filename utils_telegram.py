import time
import schedule
import json
import sys
import telegram
import datetime

class TeleBot:

    def __init__(self):
        self.bot_token, self.bot_chatid = self._open_configs()
        
        if (self.bot_token, self.bot_chatid):
            print("bot token: {}, bot chatid: {}".format(self.bot_token, self.bot_chatid))
            print("Telegram bot's connected")
        else:
            print("Telegram bot connection failed")
            return False

    def _open_configs(self, filename='config.json'):
        with open(filename) as json_file:
            configs = json.load(json_file)
            token = configs["user"]["telegram"]["token"]
            chatid = configs["user"]["telegram"]["chatid"]
            return token, chatid

    def telegram_bot_sendtext(self, bot_message):
        bot = telegram.Bot(token=self.bot_token)

        # print("token: " + bot_token + "  chatid: " + bot_chatid)
        bot.send_message(chat_id=self.bot_chatid, text=bot_message)


    def telegram_send_image(self, imageFile='data/prediction.png'):

        bot = telegram.Bot(token=self.bot_token)
        print(">> sending image -> {}".format(imageFile))
        bot.send_photo(chat_id=self.bot_chatid, photo=open(imageFile, 'rb'))

    def generate_report(self):
        today = datetime.date.today()
        # test message combination
        stock_name = "삼성전자"
        stock_price = "1,000,000"
        message = "{:%d %b %Y} \n {} : {}".format(today, stock_name, stock_price)

        print(">> sending message\n---\n {} \n---\n".format(message))
        return message

    def send_report(self):
        message = self.generate_report()

        self.telegram_bot_sendtext(message)
        self.telegram_send_image()


    def kick_regular_report(self):
        schedule.every().day.at("9:00").do(self.send_report)

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    instTele = TeleBot()
    instTele.send_report()
