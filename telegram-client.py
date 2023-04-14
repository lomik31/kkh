import websocket
import json as JSON
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from threading import Thread
from time import sleep
with open("config.json", encoding="utf-8") as config:
    config = JSON.load(config)

bot = TeleBot(config["tokens"]["telegram"])
class CONNECTION:
    CLIENT = "telegram"
    def receiver(self, ws, json):
        json = JSON.loads(json)
        self.json = json
        if (json.get("event") == "sendMessage" and json.get("message")):
            chatId = json["message"].get("chatId")
            text = json["message"].get("text")
            parseMode = json["message"].get("parseMode")
            keyboard = json["message"].get("keyboard")
            if (chatId and text):
                data = [chatId, text]
                if (parseMode): data.append(parseMode)
                if (keyboard):
                    if (keyboard == -1): resK = ReplyKeyboardRemove()
                    else:
                        resK = ReplyKeyboardMarkup(True)
                        for i in keyboard: resK.add(*i)
                    try: bot.send_message(*data, reply_markup=resK)
                    except Exception as e: print(e)
                    return
                try: bot.send_message(*data)
                except Exception as e: print(e)
        else: pass
    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###\ncode: {}, message: {}".format(close_status_code, close_msg))
    def on_error(self, ws, error):
        print("error: ", error)
        if (not error): bot.send_message(self.sendIds.get(self.json["id"])["chatId"], "noerr") #TODO
    def on_open(self, ws):
        print("Opened connection")
    def send(self, data, chatId, callback = None):
        self.id += 1
        self.sendIds[self.id] = {"chatId":chatId, "callback": callback}
        data["id"] = self.id
        self.sendData(data)
    def sendData(self, data):
        if (isinstance(data, object)): ws.send(JSON.dumps(data, default=lambda x: x.__dict__))
        else: ws.send(JSON.dumps(data))
    def reconnect():
        while True:
            if (not ws.keep_running):
                a = Thread(target=ws.run_forever).start()
                sleep(15)
            sleep(10)
connection = CONNECTION()

@bot.message_handler(commands=["start"])
def start_command(message):
    connection.sendData({"event": "newCommand", "client": connection.CLIENT, "message": message})

@bot.message_handler(content_types=["text"])
def text(message):
    connection.sendData({"event": "newMessage", "client": connection.CLIENT, "message": message})

if __name__ == "__main__":
    ws = websocket.WebSocketApp(f"ws://{config['websocketIp']}/?client={connection.CLIENT}",
                on_open=connection.on_open,
                on_message=connection.receiver,
                on_error=connection.on_error,
                on_close=connection.on_close)
    a = Thread(target=ws.run_forever).start()
    Thread(target=CONNECTION.reconnect).start()
    
    bot.infinity_polling(timeout=123, long_polling_timeout=123, skip_pending=True)