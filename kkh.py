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
            if (chatId and text):
                data = [chatId, text]
                if (parseMode): data.append(parseMode)
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
    chatData = bot.get_chat(message.chat.id)
    def callback(chatId, value):
        if (value):
            if (chatData.type == "private"): bot.send_message(chatId, "Привет. Это бот-кликер.\nСделали: [@lomik31](tg://user?id=357694314), [@Discord Nitra MV](tg://user?id=1160222752).\nЕсли ты Игорькартошка или Денисизюм, то тебе [сюда](https://docs.google.com/document/d/15a6S5F26kxRn103Yboknpogu-tJtIoxin2G9tBjY65A).\nПо вопросам обращаться к ним.\n[Планы на будущее и то, что в разработке](https://trello.com/b/kfVkY65h/%D0%BA%D0%BA%D1%88)\nНаш канал с новостями: [@kkh_news] (t.me/kkh_news)\nДля списка всех команд введите `команды`.\nЕсли у вас есть промо-код, можете ввести его при помощи `промо <код>`\nНаша беседа: [тык](t.me/+_VgA7r0PfWZiMGFi)\n\n*По вопросам пишите* [@lomik31](tg://user?id=357694314)", "MARKDOWN")
            else: bot.send_message(chatId, "Эту команду можно использовать только в личных сообщениях с ботом!")
            return
        if (chatData.type == "private"): connection.send({"action": {"function": "append.appendId", "args": [chatData.type, message.chat.id, chatData.first_name, chatData.last_name]}}, chatId)
        else: connection.send({"action": {"function": "append.appendId", "args": [chatData.type, message.chat.id]}}, chatId)
        bot.send_message(chatId, "Привет. Это бот-кликер.\nСделали: [@lomik31](tg://user?id=357694314), [@Discord Nitra MV](tg://user?id=1160222752).\nЕсли ты Игорькартошка или Денисизюм, то тебе [сюда](https://docs.google.com/document/d/15a6S5F26kxRn103Yboknpogu-tJtIoxin2G9tBjY65A).\nПо вопросам обращаться к ним.\n[Планы на будущее и то, что в разработке](https://trello.com/b/kfVkY65h/%D0%BA%D0%BA%D1%88)\nНаш канал с новостями: [@kkh_news] (t.me/kkh_news)\nДля списка всех команд введите `команды`.\nЕсли у вас есть промо-код, можете ввести его при помощи `промо <код>`\nНаша беседа: [тык](t.me/+_VgA7r0PfWZiMGFi)\n\n*По вопросам пишите* [@lomik31](tg://user?id=357694314)", "MARKDOWN", reply_markup=Keyboards.mainMenu(), disable_web_page_preview=True)
    connection.send({"action": {"function": "get.id", "args": [message.chat.id, chatData.type]}}, message.chat.id, callback)

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
    def promoList(self):
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "promo.list"}}, self.message.chat.id, callback)
    def promoInfo(self):
        if (len(self.message_text) < 2): return bot.send_message(self.message.chat.id, "Использование: ипромо <название промокода>")
        promo = self.message.text.split(" ", 1)[-1]
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "promo.info", "args": promo}}, self.message.chat.id, callback)
    def promoFullInfo(self):
        def callback(chatId, value):
            if (not value): return
            if (len(self.message_text) < 2): return bot.send_message(self.message.chat.id, "Использование: фипромо <название промокода>")
            promo = self.message.text.split(" ", 1)[-1]
            def callback(chatId, message):
                bot.send_message(chatId, message)
            connection.send({"action": {"function": "promo.fInfo", "args": promo}}, self.message.chat.id, callback)
        connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
    def promoDelete(self):
        def callback(chatId, value):
            if (not value): return
            promo = self.message.text.split(" ", 1)[-1]
            def callback(chatId):
                bot.send_message(chatId, "Промокод удален")
            connection.send({"action": {"function": "promo.delete", "args": promo}}, self.message.chat.id, callback)
        connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
    def promoAdd(self):
        def callback(chatId, value):
            if (not value): return
            if (len(self.message_text) < 5): return bot.send_message(self.message.chat.id, "Использование: нпромо <название> <параметры({'balance':0, 'click':0, 'sec':0, 'sale':0, 'multiplier':0, 'balanceBoost':0})> <кол-во активаций> <время действия>")
            a = self.message.text.partition('{')
            b = a[2].partition('}')
            c = b[2][1:]
            paramsDictSTR = a[1] + b[0]+ b[1]
            try: paramsDict = JSON.loads(paramsDictSTR.replace("'",'"'))
            except Exception as e: return bot.send_message(self.message.chat.id, f"Произошла ошибка, попробуйте ещё раз!\n{e}")
            connection.send({"action": {"function": "promo.add", "args": [self.message_text[1], paramsDict, int(c.split(" ")[0]), c.split(" ")[1]]}}, chatId, lambda chatId: bot.send_message(chatId, "Промокод успешно добавлен"))
        connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
    def promoActivate(self):
        if len(self.message_text) < 2: return bot.send_message(self.message.chat.id, "Использование: промо <код>")
        connection.send({"action": {"function": "promo.activate", "args": [connection.CLIENT, self.message.chat.id, self.message.from_user.id, self.message.text.split(" ", 1)[-1]]}}, self.message.chat.id, lambda chatId, message: bot.send_message(chatId, message))
    def getUserInfo(self):
        def callback(chatId, value):
            if (not value): return
            if (len(self.message_text) < 2): userId = self.message.from_user.id
            elif (self.message_text[1] == "_" and self.message.reply_to_message): userId = self.message.reply_to_message.from_user.id
            else: userId = self.message_text[1]
            def callback(chatId, message):
                bot.send_message(chatId, JSON.dumps(message, ensure_ascii=False, indent=4))
            connection.send({"action": {"function": "get.data", "args": userId}}, self.message.chat.id, callback)
        connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
    def admin(self):
        def callback(chatId, value):
            if (value): bot.send_message(chatId, "Вы админ")
            else: bot.send_message(chatId, "Вы не админ")
        connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
    def removeId(self):
        def callback(chatId, value):
            if (not value): return
            if (len(self.message_text) < 2): return bot.send_message(chatId, "Использование: дюзер <id пользователя>")
            if (self.message_text[1] == "_" and self.message.reply_to_message): user = self.message.reply_to_message.from_user.id
            else: user = self.message_text[1]
            def callback(chatId, value):
                if (value): return bot.send_message(chatId, "Невозможно удалить администратора")
                connection.send({"action": {"function": "removeId", "args": user}}, chatId, lambda chatId: bot.send_message(chatId, "Пользователь успешно удален"))
            connection.send({"action": {"function": "get.get", "args": [user, "isAdmin"]}}, chatId, callback)
        connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
    def userslist(self):
        def callback(chatId, text):
            bot.send_message(chatId, text)
        connection.send({"action": {"function": "kmd.getIds", "args": self.message.from_user.id}}, self.message.chat.id, callback)
    def btcBet(self):
        if (len(self.message_text) < 3): return bot.send_message(self.message.chat.id, "Использование: бит <ставка> вверх/вниз")
        amount = self.message_text[1]
        bet = self.message_text[2]
        connection.send({"action": {"function": "game.btcBet", "args": [connection.CLIENT, self.message.chat.id, self.message.from_user.id, amount, bet]}}, self.message.chat.id)
    def commandsList(self):
        connection.send({"action": {"function": "kmd.commandsList", "args": self.message.from_user.id}}, self.message.chat.id, lambda chatId, message: bot.send_message(chatId, message))

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