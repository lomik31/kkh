import websocket, re
import json as JSON
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from threading import Thread
with open("config.json", encoding="utf-8") as config:
    config = JSON.load(config)

bot = TeleBot(config["tokens"]["telegram"])
class CONNECTION:
    id = 0
    sendIds = {}
    CLIENT = "telegram"
    def receiver(self, ws, json):
        json = JSON.loads(json)
        self.json = json
        # if (json.get("id")):
        #     cdata = self.sendIds.get(json["id"])
        #     if (cdata == None): raise KeyError("Пришедший id не является верным")
        #     if (not json.get("success")):
        #         msg = json.get("message")
        #         if (msg): bot.send_message(cdata["chatId"], msg)
        #         del self.sendIds[json["id"]]
        #         return
        #     f = self.sendIds.get(json["id"])["callback"]
        #     if (f):
        #         data = []
        #         if (json.get("data") != None):
        #             if (type(json["data"]) == list):
        #                 data += json["data"]
        #             else: data.append(json["data"])
        #         if (cdata.get("buffer")): data += cdata["buffer"]
        #         if data != []: f(cdata["chatId"], *data)
        #         else: f(cdata["chatId"])
        #     del self.sendIds[json["id"]]
        if (json.get("event") == "sendMessage" and json.get("message")):
            chatId = json["message"].get("chatId")
            text = json["message"].get("text")
            parseMode = json["message"].get("parseMode")
            keyboard = json["message"].get("keyboard")
            if (chatId and text):
                data = [chatId, text]
                if (parseMode): data.append(parseMode)
                if (keyboard):
                    if (keyboard == -1):
                        resK = ReplyKeyboardRemove()
                    else:
                        resK = ReplyKeyboardMarkup()
                        for i in keyboard:
                            resK.add(*i)
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
connection = CONNECTION()

@bot.message_handler(commands=["start"])
def start_command(message):
    connection.sendData({"event": "newCommand", "client": connection.CLIENT, "message": message})

@bot.message_handler(content_types=["text"])
def text(message):
    connection.sendData({"event": "newMessage", "client": connection.CLIENT, "message": message})

class kmd:
    def __init__(self, message, message_text, customCommand = None):
        self.message = message
        self.message_text = message_text
        def callback(chatId, value):
            if (not value): return bot.send_message(chatId, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!", parse_mode="MARKDOWN")
            if (customCommand): command = customCommand
            else: command = message.text
            connection.send({"action": {"function": "set.lastCommand", "args": [self.message.from_user.id, command]}}, chatId)
        connection.send({"action": {"function": "get.id", "args": self.message.from_user.id}}, self.message.chat.id, callback)
    def upgrades(self):
        type = bot.get_chat(self.message.chat.id).type
        def callback(chatId, value):
            if (not value): return bot.send_message(chatId, "Открыто меню апгрейдов")
            def callback(chatId, sec, click, sale, balanceBoost):
                connection.send({"action": {"function": "set.keyboard.active", "args": [self.message.chat.id, type, True]}}, self.message.chat.id)
                bot.send_message(chatId, "Открыто меню апгрейдов", reply_markup=Keyboards.upgrade(sec, click, sale, balanceBoost), parse_mode="HTML")
            connection.send({"action": {"function": "get.keyboardCosts", "args": self.message.from_user.id}}, chatId, callback)
        connection.send({"action": {"function": "get.keyboard", "args": [self.message.chat.id, "keyboard", type]}}, self.message.chat.id, callback)
    def keyboardSet(self):
        if (len(self.message_text) < 2 or self.message_text[1] not in ["да", "нет"]): return bot.send_message(self.message.chat.id, "Использование: клавиатура <да/нет>")
        if (self.message_text[1] == "да"): state = True
        elif (self.message_text[1] == "нет"): state = False
        type = bot.get_chat(self.message.chat.id).type
        def callback(chatId):
            if (state): bot.send_message(chatId, "Клавиатура включена", reply_markup=Keyboards.mainMenu())
            else: 
                connection.send({"action": {"function": "set.keyboard.active", "args": [self.message.chat.id, type, False]}}, self.message.chat.id)
                bot.send_message(chatId, "Клавиатура отключена", reply_markup=ReplyKeyboardRemove())
        connection.send({"action": {"function": "set.keyboard.passive", "args": [self.message.chat.id, type, state]}}, self.message.chat.id, callback)
    def backKeyboardMenu(self):
        type = bot.get_chat(self.message.chat.id).type
        def callback(chatId, value):
            if (value):
                connection.send({"action": {"function": "set.keyboard.active", "args": [chatId, type, False]}}, chatId)
                bot.send_message(chatId, "Вы вышли из меню", reply_markup=Keyboards.mainMenu())
            else: bot.send_message(chatId, "Вы вышли из меню")
        connection.send({"action": {"function": "get.keyboard", "args": [self.message.chat.id, "activeKeyboard", type]}}, self.message.chat.id, callback)

class Keyboards:
    def upgrade(sec, click, sale, balanceBoost):
        keyboard = ReplyKeyboardMarkup(True)
        button_sec = KeyboardButton(f"+сек ({sec} КШ)")
        button_click = KeyboardButton(f"+клик ({click} КШ)")
        button_sale = KeyboardButton(sale)
        button_balanceBoost = KeyboardButton(balanceBoost)
        button_back = KeyboardButton("Назад")
        keyboard.add(button_sec, button_click)
        keyboard.add(button_sale, button_balanceBoost)
        keyboard.add(button_back)
        return keyboard
    def mainMenu():
        keyboard = ReplyKeyboardMarkup()
        button_click = KeyboardButton("🔮")
        button_upgrades = KeyboardButton("Апгрейды")
        button_balance = KeyboardButton("Баланс")
        button_reset = KeyboardButton("Сброс")
        keyboard.add(button_click)
        keyboard.add(button_upgrades, button_balance)
        keyboard.add(button_reset)
        return keyboard

if __name__ == "__main__":
    ws = websocket.WebSocketApp("ws://127.0.0.1:3200/?client={}".format(connection.CLIENT),
                on_open=connection.on_open,
                on_message=connection.receiver,
                on_error=connection.on_error,
                on_close=connection.on_close)
    Thread(target=ws.run_forever).start()
    bot.polling(True, interval=0.5, timeout=123, long_polling_timeout=123)