import websocket, re
import json as JSON
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from threading import Thread
bot = TeleBot("1609358198:AAHs5roy9uMih-5fTlvzHKgLlfkdQXm-LPk")
class CONNECTION:
    id = 0
    sendIds = {}
    CLIENT = "telegram"
    def receiver(self, ws, json):
        json = JSON.loads(json)
        print(json)
        self.json = json
        if (json.get("id")):
            cdata = self.sendIds.get(json["id"])
            if (cdata == None): raise KeyError("Пришедший id не является верным")
            if (not json.get("success")):
                msg = json.get("message")
                if (msg): bot.send_message(cdata["chatId"], msg)
                del self.sendIds[json["id"]]
                return
            f = self.sendIds.get(json["id"])["callback"]
            if (f):
                data = []
                if (json.get("data") != None):
                    if (type(json["data"]) == list):
                        data += json["data"]
                    else: data.append(json["data"])
                if (cdata.get("buffer")): data += cdata["buffer"]
                if data != []: f(cdata["chatId"], *data)
                else: f(cdata["chatId"])
            del self.sendIds[json["id"]]
        elif (json.get("action") == "sendMessage" and json.get("data")):
            chatId = json["data"].get("chatId")
            text = json["data"].get("text")
            if (chatId and text):
                try: bot.send_message(chatId, text)
                except: pass
        else: print(json)
    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###\ncode: {}, message: {}".format(close_status_code, close_msg))
    def on_error(self, ws, error):
        print("error: ", error)
        if (not error): bot.send_message(self.sendIds.get(self.json["id"])["chatId"], "noerr") #TODO
    def on_open(self, ws):
        print("Opened connection")
    def send(self, data, chatId, callback = None, buffer:list = None):
        self.id += 1
        self.sendIds[self.id] = {"chatId":chatId, "callback": callback, "buffer": buffer}
        data["id"] = self.id
        self.sendData(data)
    def sendData(self, data):
        ws.send(JSON.dumps(data))
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
    message_text = message.text.lower().split(" ")
    if (message_text[0] == "кмд"):
        def callback(chatId, value):
            if (not value): return
            if (len(message_text) < 3): return bot.send_message(chatId, "Использование: кмд <id> <команда>")
            if (message_text[1] == "_" and message.reply_to_message): userId = message.reply_to_message.from_user.id
            else: userId = message_text[1]
            def callback(chatId, value):
                if (not value): return bot.send_message(chatId, "Id не найден")
                if message_text[2] == "кмд": return bot.send_message(message.chat.id, "э, так нельзя, бан")
                def callback(chatId, value):
                    if (value and message.from_user.id != 357694314): return bot.send_message(message.chat.id, "Невозможно выполнить кмд для этого юзера!")
                    kmd(message, message_text)
                    message.from_user.id = userId
                    a = message.text.split(" ")[2:]
                    message.text = ""
                    b = 0
                    for i in a:
                        b = len(a) - 1
                        if b == 0:
                            message.text += i
                        else:
                            message.text += f"{i} "
                    text(message)
                connection.send({"action": {"function": "get.get", "args": [userId, "isAdmin"]}}, chatId, callback)
            connection.send({"action": {"function": "get.id", "args": userId}}, chatId, callback)
        connection.send({"action": {"function": "get.get", "args": [message.from_user.id, "isAdmin"]}}, message.chat.id, callback)
    elif (message_text[0] == "_"):
        def callback(chatId, command):
            if command == "": bot.send_message(message.chat.id, "Последняя команда не обнаружена")
            else:
                message.text = command
                text(message)
        connection.send({"action": {"function": "get.get", "args": [message.from_user.id, "lastCommand"]}}, message.chat.id, callback)
    elif (message_text[0] in ["топ", "всетоп"]): kmd(message, message_text).top()
    elif (message_text[0] == "бэкап"): kmd(message, message_text).backup()
    elif (message_text[0] in ["клик", "🔮"]): kmd(message, message_text).click()
    elif (message_text[0] in ["баланс", "б"]): kmd(message, message_text).balance()
    elif (message_text[0] in ["бдзапись", "записьбд"]): kmd(message, message_text).writeDB()
    elif (message_text[0] == "цена"): kmd(message, message_text).price()
    elif (message_text[0] == "set"): kmd(message, message_text).set()
    elif (message_text[0] in ["монета", "монетка"]): kmd(message, message_text).coin()
    elif (message_text[0] == "сброс"): kmd(message, message_text).reset()
    elif (message_text[0] == "перевод"): kmd(message, message_text).pay()
    elif (message_text[0] == "бонус"): kmd(message, message_text).bonus()
    elif (message_text[0] == "бонус2"): kmd(message, message_text).bonus2()
    elif (message_text[0].startswith("+") and message_text[0][1:] != "банк"):
        loxtext = message.text
        message.text = re.sub(r" \(\d+[\.\d]* КШ\)", "", message.text)[1:]
        message_text = message.text.lower().split(" ")
        t = message_text[0]
        for i in range(0, len(message_text)):
            if (t in ["сек", "клик", "скидка", "1% скидки", "бб", "баланс", "баланс/день", "буст баланса", "буст баланс", "1% баланса/день"]): return kmd(message, message_text, loxtext).buyBoost(t)
            t += f" {message_text[i+1]}"
        return bot.send_message(message.chat.id, "Неверный тип апгрейда")
    elif (message_text[0] == "апгрейды"): kmd(message, message_text).upgrades()
    # elif (message_text[0] == "test"): bot.send_message(message.chat.id, "lox", reply_markup=ReplyKeyboardRemove()) ВНИМАНИЕ БЛЯТЬ
    elif (message_text[0] == "клавиатура"): kmd(message, message_text).keyboardSet()
    elif (message_text[0] in ["назад", "главное меню"]): kmd(message, message_text).backKeyboardMenu()
    elif (message_text[0] in ["послать", "послатьанон"]): kmd(message, message_text).sendUser()
    elif (message_text[0] in ["+банк", "-банк", "банк"]): kmd(message, message_text).bankTransfer()
    elif (message_text[0] == "рассылка"): kmd(message, message_text).mailing()
    elif (message_text[0] == "лпромо"): kmd(message, message_text).promoList()
    elif (message_text[0] == "ипромо"): kmd(message, message_text).promoInfo()
    elif (message_text[0] == "фипромо"): kmd(message, message_text).promoFullInfo()
    elif (message_text[0] == "дпромо"): kmd(message, message_text).promoDelete()
    elif (message_text[0] == "нпромо"): kmd(message, message_text).promoAdd()
    elif (message_text[0] == "промо"): kmd(message, message_text).promoActivate()
    elif (message_text[0] == "инфо"): kmd(message, message_text).getUserInfo()
    elif (message_text[0] == "админ"): kmd(message, message_text).admin()
    elif (message_text[0] == "дюзер"): kmd(message, message_text).removeId()
    elif (message_text[0] == "юзерслист"): kmd(message, message_text).userslist()
    elif (message_text[0] == "бит"): kmd(message, message_text).btcBet()
    elif (message_text[0] == "команды"): kmd(message, message_text).commandsList()

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
    def top(self):
        top = {"page": 1, "mode": "balance", "activeMode": True, "id": self.message.from_user.id}
        if (self.message_text[0] == "всетоп"): top["activeMode"] = False
        if (len(self.message_text) >= 2):
            if (self.message_text[1] in ["клик", "к", "click"]): top["mode"] = "click"
            elif (self.message_text[1] in ["сек", "с", "sec"]): top ["mode"] = "sec"
            elif (self.message_text[1] in ["бб", "бустбаланса", "bb", "balanceboost", "балансбуст", "balanceBoost"]): top["mode"] = "balanceBoost"
            elif (self.message_text[1] == "буст" and len(self.message_text) >= 3 and self.message_text[2] in ["баланс", "баланса"]):
                top["mode"] = "balanceBoost"
                self.message_text.pop(2)
            elif (self.message_text[1] in ["регистрация", "р", "рег", "register", "registerTime"]): top["mode"] = "registerTime"
            elif (self.message_text[1] in ["банк", "bank"]): top["mode"] = "bank"
            elif (self.message_text[1] in ["д", "деньги", "money"]): top["mode"] = "money"
            if (len(self.message_text) >= 3):
                try:
                    top["page"] = int(self.message_text[2])
                except: pass
        def callback(chatId, msg):
            bot.send_message(chatId, msg, parse_mode="HTML")
        connection.send({"action": {"function": "kmd.leaderboard", "args": [top['mode'], top['activeMode'], top['id'], top['page']]}}, self.message.chat.id, callback)
    def backup(self):
        if (len(self.message_text) < 2): return bot.send_message(self.message.chat.id, "Использование: бэкап <создать>\nСоздаёт бэкап в папку с бекапами и загружает в облако.")
        if (self.message_text[1] == "создать"):
            def callback(chatId, message):
                bot.send_message(chatId, message)
            connection.send({"action": {"function": "backup"}}, self.message.chat.id, callback)
        else: bot.send_message(self.message.chat.id, "Использование: бэкап <создать>")
    def click(self):
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "kmd.click", "args": self.message.from_user.id}}, self.message.chat.id, callback)
    def balance(self):
        user = self.message.from_user.id
        if (len(self.message_text) > 1): 
            if (self.message_text[1] == "_" and self.message.reply_to_message): user = self.message.reply_to_message.from_user.id
            else: user = self.message_text[1]
        def callback(chatId, message):
            bot.send_message(chatId, message, parse_mode="MARKDOWN")
        connection.send({"action": {"function": "kmd.balance", "args": user}}, self.message.chat.id, callback)
    def writeDB(self):
        def callback(chatId, msg):
            bot.send_message(chatId, msg)
        connection.send({"action": {"function": "dbWrite"}}, self.message.chat.id, callback)
    def price(self):
        if (len(self.message_text) < 2): return bot.send_message(self.message.chat.id, "Использование: цена <апгрейд>")
        upgrade = self.message.text[5:].replace("+", "")
        if (upgrade == "клик"): upgrade = "click"
        elif (upgrade == "сек"): upgrade = "sec"
        elif (upgrade in ["скидка", "скидки"]): upgrade = "sale"
        elif (upgrade in ["бб", "баланс", "баланса", "баланс/день"]): upgrade = "balanceBoost"
        if (upgrade not in ["click", "sec", "sale", "balanceBoost"]): return bot.send_message(self.message.chat.id, "Неверный апгрейд")
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "calc.boost", "args": [self.message.from_user.id, upgrade]}}, self.message.chat.id, callback)
    def set(self):
        if (len(self.message_text) < 4): return bot.send_message(self.message.chat.id, "Использование: set <id> <параметр> <значение>")
        amount = self.message_text[3]
        user = self.message_text[1]
        if (self.message_text[1] == "_" and self.message.reply_to_message): user = self.message.reply_to_message.from_user.id
        if (amount == "true"): amount = True
        elif (amount == "false"): amount = False
        connection.send({"action": {"function": "kmd.set", "args": [self.message.from_user.id, user, self.message.text.split(" ")[2], amount]}}, self.message.chat.id, lambda chatId, message: bot.send_message(chatId, message))
    def coin(self):
        if (len(self.message_text) < 3): return bot.send_message(self.message.chat.id, "Использование: монета <ставка> орел/решка")
        bet = self.message_text[1]
        side = self.message_text[2]
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "game.coin", "args": [self.message.from_user.id, bet, side]}}, self.message.chat.id, callback)
    def reset(self):
        def callback(chatId, message):
            bot.send_message(chatId, message, parse_mode="MARKDOWN")
        if (len(self.message_text) == 1): connection.send({"action": {"function": "kmd.resetMessage"}}, self.message.chat.id, callback)
        elif (len(self.message_text) > 1):
            if (self.message_text[1] == "справка"): connection.send({"action": {"function": "kmd.resetMessage"}}, self.message.chat.id, callback)
            elif (self.message_text[1] == "подтвердить"): connection.send({"action": {"function": "resetId", "args": [self.message.from_user.id, 1]}}, self.message.chat.id, lambda chatId: bot.send_message(chatId, "Ваш прогресс сброшен!"))
            else:
                def callback(chatId, state):
                    if (not state): return bot.send_message(chatId, "Использование: сброс <подтвердить/справка>")
                    user = self.message_text[1]
                    def callback(chatId):
                        def callback(chatId, name):
                            bot.send_message(chatId, f"Прогресс пользователя {name} (`{user}`) успешно сброшен!", parse_mode="MARKDOWN")
                            try: bot.send_message(user, "Ваш прогресс сброшен администратором!")
                            except: pass
                        connection.send({"action": {"function": "get.get", "args": [user, "fullName"]}}, self.message.chat.id, callback)
                    connection.send({"action": {"function": "resetId", "args": [user, 2]}}, self.message.chat.id, callback)
                connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
    def pay(self):
        if (len(self.message_text) < 3): return bot.send_message(self.message.chat.id, "Использование: перевод <сумма> <id получателя> [комментарий]")
        fr0m = self.message.from_user.id
        to = self.message_text[2]
        amount = self.message_text[1]
        comment = ""
        if (len(self.message_text) > 3):
            for i in self.message.text.split(" ")[3:]:
                comment += i
        if (to == "_" and self.message.reply_to_message): to = self.message.reply_to_message.from_user.id
        def callback(chatId, message):
            bot.send_message(chatId, message)
        if (comment): connection.send({"action": {"function": "kmd.pay", "args": [fr0m, to, amount, comment]}}, self.message.chat.id, callback)
        else: connection.send({"action": {"function": "kmd.pay", "args": [fr0m, to, amount]}}, self.message.chat.id, callback)
    def bonus(self):
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "give.bonus", "args": [self.message.from_user.id]}}, self.message.chat.id, callback)
    def bonus2(self):
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "give.bonus2", "args": [self.message.from_user.id]}}, self.message.chat.id, callback)
    def buyBoost(self, boost: str):
        args = [i for i in self.message_text if i not in boost.split(" ")]
        if (boost == "клик"): boost = "click"
        elif (boost == "сек"): boost = "sec"
        elif (boost in ["скидка", "1% скидки"]): boost = "sale"
        elif (boost in ["бб", "баланс", "баланс/день", "буст баланса", "буст баланс", "1% баланса/день"]): boost = "balanceBoost"
        def callback(chatId, message):
            def callback(chatId, value):
                if (not value): return bot.send_message(chatId, message, parse_mode="HTML")
                def callback(chatId, sec, click, sale, balanceBoost):
                    bot.send_message(chatId, message, reply_markup=Keyboards.upgrade(sec, click, sale, balanceBoost), parse_mode="HTML")
                connection.send({"action": {"function": "get.keyboardCosts", "args": self.message.from_user.id}}, chatId, callback)
            connection.send({"action": {"function": "get.keyboard", "args": [self.message.chat.id, "activeKeyboard", bot.get_chat(chatId).type]}}, chatId, callback)
        count = 1
        if (len(args) > 0):
            if (args[0] in ["все", "всё"]): count = -1
            else: count = args[0]
            return connection.send({"action": {"function": "kmd.buyBoost", "args": [self.message.from_user.id, boost, count]}}, self.message.chat.id, callback)
        connection.send({"action": {"function": "kmd.buyBoost", "args": [self.message.from_user.id, boost]}}, self.message.chat.id, callback)
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
    def sendUser(self):
        if (len(self.message_text) < 2): return bot.send_message(self.message.chat.id, f"Использование: {self.message_text[0]} <id пользователя>")
        if (self.message_text[1] == "_" and self.message.reply_to_message): user = self.message.reply_to_message.from_user.id
        else: user = self.message_text[1]
        if (self.message_text[0] == "послать"): type = "normal"
        elif (self.message_text[0] == "послатьанон"): type = "anonymous"
        def callback(chatId, message):
            bot.send_message(chatId, message)
        connection.send({"action": {"function": "kmd.sendUser", "args": [self.message.from_user.id, user, type]}}, self.message.chat.id, callback)
    def bankTransfer(self):
        if (self.message_text[0] == "+банк"): action = "put"
        elif (self.message_text[0] == "-банк"): action = "take"
        elif (self.message_text[0] == "банк"): return bot.send_message(self.message.chat.id, "helpMessage")
        def callback(chatId, message):
            bot.send_message(chatId, message)
        if (len(self.message_text) > 1):
            value = self.message_text[1]
            return connection.send({"action": {"function": "kmd.bankTransfer", "args": [self.message.from_user.id, action, value]}}, self.message.chat.id, callback)
        connection.send({"action": {"function": "kmd.bankTransfer", "args": [self.message.from_user.id, action]}}, self.message.chat.id, callback)
    def mailing(self):
        if (len(self.message_text) < 2): return bot.send_message(self.message.chat.id, "Использование: рассылка <да/нет>")
        state = None
        if (self.message_text[1] == "да"): state = True
        elif (self.message_text[1] == "нет"): state = False
        if (state != None):
            def callback(chatId):
                if (state): bot.send_message(chatId, "Рассылка включена.\nДля отключения введите рассылка нет")
                else: bot.send_message(chatId, "Рассылка отключена.\nДля включения введите рассылка да")
            return connection.send({"action": {"function": "set.set", "args": [self.message.from_user.id, "mails", state]}}, self.message.chat.id, callback)
        if (self.message_text[1] == "создать"):
            def callback(chatId, value):
                if (not value): return
                if (len(self.message_text) < 3): return bot.send_message(chatId, "Использование: рассылка создать <текст>")
                text = self.message.text.split(" ", 2)[-1]
                connection.send({"action": {"function": "kmd.mailingSend", "args": text}}, self.message.chat.id)
            return connection.send({"action": {"function": "get.get", "args": [self.message.from_user.id, "isAdmin"]}}, self.message.chat.id, callback)
        bot.send_message(self.message.chat.id, "Использование: рассылка <да/нет>")
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