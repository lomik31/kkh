# -*- coding: utf-8 -*-
from telebot import types, apihelper, TeleBot
import time
import rec_file
from threading import Thread
import random
import yadisk
import shutil
import datetime
import schedule
import json
import requests
import logging
from commands import COMMANDS

logging.basicConfig(filename=f"logs/logs.log", level=logging.INFO, format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")

main = logging.getLogger("main")
messageLog = logging.getLogger("message")

with open("usrs.json", encoding="utf-8") as fileRead:
    fileRead = json.load(fileRead)
main.info("USERSDATA LOADED")
with open("config.json", encoding="utf-8") as config:
    config = json.load(config)
main.info("CONFIG LOADED")
with open("tags.json", encoding="utf-8") as tags:
    tags = json.load(tags)
main.info("USERTAGS LOADED")

bot = TeleBot(config["telegramToken"])
apihelper.proxy = {'http':'http://10.10.1.10:3128'}
main.info("BOT IS RUNNING NOW")
y = yadisk.YaDisk(token=config["yandexDiskToken"])
main.info("CLOUD CONNECTED")
roulette = []

def getId(toFind):
    if len(toFind) < 2: return "Id не найден"
    if toFind[0] == "@": toFind = toFind[1:]
    if toFind in fileRead["users"].keys(): return int(toFind)
    elif toFind in list(tags.values()):
        for i in tags:
            if tags[i] == toFind: return int(i)
        return "Id не найден"
def getTag(toFind):
    if (toFind in tags.keys() or str(toFind) in tags.keys()):
        if tags[str(toFind)] != None: return f"@{tags[str(toFind)]}"
        else: return int(toFind)
    else: return "ID не найден"
def getName(id):
     fullname = bot.get_chat(id)
     name = fullname.first_name
     lastname = fullname.last_name
     if lastname != None:
          name += f" {lastname}"
     return name
@bot.message_handler(commands=["start"])
def start_command(message):
    messageLog.info(f"TEXT: {message.chat.id}: {getName(message.from_user.id)} ({message.from_user.id}): {message.text}")
    if (bot.get_chat(message.chat.id).type != "private"):
        if str(message.chat.id) not in fileRead["groups"].keys():
            fullinfo = bot.get_chat(message.chat.id)
            firstName = fullinfo.first_name;
            lastName = fullinfo.last_name
            rec_file.append_id(message.chat.id, fullinfo.type, firstName, lastName, fileRead);
            if (fullinfo.username != None): tags[str(message.chat.id)] = fullinfo.username.lower()
        bot.send_message(message.chat.id, "Эту команду можно использовать только в личных сообщениях с ботом!");
    else:
        if str(message.from_user.id) not in fileRead["users"].keys():
            fullinfo = bot.get_chat(message.from_user.id)
            rec_file.append_id(message.from_user.id, bot.get_chat(message.chat.id).type, fullinfo.first_name, fullinfo.last_name, fileRead);
            bot.send_message(message.chat.id, config["messages"]["startCommand"], disable_web_page_preview=True, reply_markup=main_menu_buttons(), parse_mode="MARKDOWN");
        else:
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, config["messages"]["startCommand"]);

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    messageLog.info(f"CALL: {call.message.chat.id}: {getName(call.from_user.id)} ({call.from_user.id}): {call.data}")
    if (call.data.split(" ")[0] == "r"):
        call.data = call.data[2:]
        if (call.data in ["1:3", "1:3(2)", "1:3(3)", "1st12", "2nd12", "3rd12", "1to18", "19to36", "even", "odd", "red", "black"]):
            bot.answer_callback_query(call.id)
            bot.edit_message_media(types.InputMediaPhoto("AgACAgIAAxkBAAEERyxh0ZLbF82ZvyLwUJfjbOvxh2Z3PwAC2rcxGyzskEoC-uMjPRKv6gEAAwIAA3kAAyME"), call.message.chat.id, call.message.id)
            # bot.edit_message_media(types.InputMediaPhoto("AgACAgIAAxkBAAJS5mMcm3T2QwGsS2gw_Iq0k4jGAVf-AAI8tTEb4KQ5S_X7F-E3605YAQADAgADbQADKQQ"), call.message.chat.id, call.message.id)
            bot.register_next_step_handler(bot.send_message(call.message.chat.id, "Введите вашу ставку"), rouletteButtonsBet, call.data, call.from_user.id, call.message.chat.id)

@bot.message_handler(content_types=["text"])
def send_text(message):
    if (message.text != None): message_text = message.text.lower().split(" ")
    if message_text[0] != "кмд" and message_text[0] != "_":
        if check_messages(message, message_text) != False:
            messageLog.info(f"TEXT: {message.chat.id}: {getName(message.from_user.id)} ({message.from_user.id}): {message.text}")
            if str(message.from_user.id) in fileRead["users"].keys():
                rec_file.append_last_command(message.from_user.id, message.text, fileRead);
    elif message_text[0] == "_":
        repeat_command(message)
    else: #кмд
        rec_file.append_last_command(message.from_user.id, message.text, fileRead)
        if rec_file.get_admin(message.from_user.id, fileRead) == 0: return
        if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: кмд <id> <команда>")
        try:
            if message_text[1] == "_":
                userid = message.reply_to_message
                if userid != None: userid = userid.from_user.id
                else: userid = 0
            else: userid = getId(message_text[1])
        except ValueError: return bot.send_message(message.chat.id, "Неверный id. ID должен состоять только из цифр!")
        if (userid == 0): return bot.send_message(message.chat.id, "Используйте `_` при ответе на сообщение", parse_mode="MARKDOWN")
        if (userid not in rec_file.get_ids(fileRead)): return bot.send_message(message.chat.id, "ID не найден")
        message_text = message_text[2::]
        if (rec_file.get_admin(userid, fileRead) == True and message.from_user.id != 357694314): return bot.send_message(message.chat.id, "Невозможно выполнить кмд для этого юзера!")
        message.from_user.id = userid
        a = message.text.split(" ")[2::]
        message.text = ""
        b = 0
        for i in a:
            b = len(a) - 1
            if b == 0:
                message.text += i
            else:
                message.text += f"{i} "
        if message_text[0] == "кмд": return bot.send_message(message.chat.id, "э, так нельзя, бан")
        check_messages(message, message_text)

def whiletrue():
    global fileRead
    while True:
        rec_file.time_nachislenie(fileRead)
        schedule.run_pending()
        time.sleep(1)
def autoBackup():
    today = datetime.datetime.today()
    name = f"backup-{today.strftime('%Y-%m-%d_%H.%M.%S')}.txt"
    shutil.copyfile("usrs.json", f"backups/{name}")
    y.upload(f"backups/{name}", (f"/kkh_backups/{name}"))
def updateUsersNameInFile():
    dict = rec_file.updateUserName(fileRead)
    for i in dict:
        try:
            fullinfo = bot.get_chat(int(i[0]))
            i[1] = fullinfo.first_name
            i[2] = fullinfo.last_name
            if (fullinfo.username != None): tags[str(i[0])] = fullinfo.username.lower()
            else: tags[str(i[0])] = fullinfo.username
        except: pass
    with open('tags.json', 'w', encoding="utf-8") as outfile:
        json.dump(tags, outfile, ensure_ascii=False, indent=4)
    rec_file.updateUserNameWrite(dict, fileRead)
    
def weeklyLotteryLostMoneyCoin():
        lastWeekCoinSum = fileRead["sharedData"]["weeklyData"]["lostCoin"] - fileRead["sharedData"]["weeklyData"]["winCoin"]
        fileRead["sharedData"]["weeklyData"]["winCoin"], fileRead["sharedData"]["weeklyData"]["lostCoin"] = 0, 0
        for i in fileRead["users"].keys():
            fileRead["sharedData"]["weeklyData"]["winCoin"] += fileRead["users"][i]["wonMoneta"]
            fileRead["sharedData"]["weeklyData"]["lostCoin"] += fileRead["users"][i]["lostMoneta"]
        thisWeekCoinSum = fileRead["sharedData"]["weeklyData"]["lostCoin"] - fileRead["sharedData"]["weeklyData"]["winCoin"] - lastWeekCoinSum
        if thisWeekCoinSum <= 0: return bot.send_message(357694314, "разыгрывать нечего")
        id = rec_file.chooseNewWinner(604800, fileRead)
        sum = int(thisWeekCoinSum * 0.3)
        rec_file.append_balance(id, sum, fileRead)
        try: bot.send_message(id, f"Поздравляем!\nВы выиграли в еженедельном конкурсе {rec_file.ob_chisla(sum)} КШ!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
        except: pass
        id = rec_file.chooseNewWinner(604800, fileRead)
        sum = int(thisWeekCoinSum * 0.25)
        rec_file.append_balance(id, sum, fileRead)
        try: bot.send_message(id, f"Поздравляем!\nВы выиграли в еженедельном конкурсе {rec_file.ob_chisla(sum)} КШ!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
        except: pass
        id = rec_file.chooseNewWinner(604800, fileRead)
        sum = int(thisWeekCoinSum * 0.2)
        rec_file.append_balance(id, sum, fileRead)
        try: bot.send_message(id, f"Поздравляем!\nВы выиграли в еженедельном конкурсе {rec_file.ob_chisla(sum)} КШ!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
        except: pass
        id = rec_file.chooseNewWinner(604800, fileRead)
        sum = int(thisWeekCoinSum * 0.15)
        rec_file.append_balance(id, sum, fileRead)
        try: bot.send_message(id, f"Поздравляем!\nВы выиграли в еженедельном конкурсе {rec_file.ob_chisla(sum)} КШ!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
        except: pass
        id = rec_file.chooseNewWinner(604800, fileRead)
        sum = int(thisWeekCoinSum * 0.1)
        rec_file.append_balance(id, sum, fileRead)
        try: bot.send_message(id, f"Поздравляем!\nВы выиграли в еженедельном конкурсе {rec_file.ob_chisla(sum)} КШ!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
        except: pass
Thread(target=whiletrue).start()
schedule.every().day.at("00:00").do(rec_file.balance_boost_nachislenie, fileRead)
schedule.every().day.at("04:20").do(updateUsersNameInFile)
schedule.every().hour.at(":00").do(rec_file.bank_nachislenie, fileRead)
schedule.every(2).hours.do(autoBackup)

#кнопки
def main_menu_buttons():
    main_menu_board = types.ReplyKeyboardMarkup(True)
    button_click = types.KeyboardButton("🔮")
    button_upgrades = types.KeyboardButton("Апгрейды")
    button_balance = types.KeyboardButton("Баланс")
    button_reset = types.KeyboardButton("Сброс")
    main_menu_board.add(button_click)
    main_menu_board.add(button_upgrades, button_balance)
    main_menu_board.add(button_reset)
    return main_menu_board
def upgades_buttons(id):
    upgades_board = types.ReplyKeyboardMarkup(True)
    button_sec = types.KeyboardButton(f"+сек ({rec_file.ob_chisla(rec_file.cal_boost_sec(id, fileRead))} КШ)")
    button_click = types.KeyboardButton(f"+клик ({rec_file.ob_chisla(rec_file.cal_boost_click(id, fileRead))} КШ)")
    if rec_file.get_skidka(id, fileRead) >= 25:
        button_skidka = types.KeyboardButton(message_max_skidka())
    else:
        button_skidka = types.KeyboardButton(f"+1% скидки ({rec_file.ob_chisla(rec_file.cal_boost_skidka(id, fileRead))} КШ)")
    if rec_file.get_boost_balance(id, fileRead) >= rec_file.cal_boost_balance(id, fileRead)[1]:
        button_boost_balance = types.KeyboardButton(message_max_boost_balance())
    else:
        button_boost_balance = types.KeyboardButton(f"+1% баланса/день ({rec_file.ob_chisla(rec_file.cal_boost_balance(id, fileRead)[0])} КШ)")
    button_back = types.KeyboardButton("Назад")
    upgades_board.add(button_sec, button_click)
    upgades_board.add(button_skidka, button_boost_balance)
    upgades_board.add(button_back)
    return upgades_board
def rouletteKeyboard():
    upgades_board = types.InlineKeyboardMarkup(row_width=4)
    firstLine = types.InlineKeyboardButton("1:3(3)", callback_data="r 1:3(3)")
    secondLine = types.InlineKeyboardButton("1:3(2)", callback_data="r 1:3(2)")
    thirdLine = types.InlineKeyboardButton("1:3", callback_data="r 1:3")
    firstColumn = types.InlineKeyboardButton("1st12", callback_data="r 1st12")
    secondColumn = types.InlineKeyboardButton("2nd12", callback_data="r 2nd12")
    thirdColumn = types.InlineKeyboardButton("3rd12", callback_data="r 3rd12")
    oneToEighteen = types.InlineKeyboardButton("1to18", callback_data="r 1to18")
    even = types.InlineKeyboardButton("EVEN", callback_data="r even")
    red = types.InlineKeyboardButton("RED", callback_data="r red")
    black = types.InlineKeyboardButton("BLACK", callback_data="r black")
    odd = types.InlineKeyboardButton("ODD", callback_data="r odd")
    nineteenToThirtySix = types.InlineKeyboardButton("19to36", callback_data="r 19to36")
    upgades_board.add(firstColumn, secondColumn, thirdColumn, firstLine)
    upgades_board.add(oneToEighteen, red, nineteenToThirtySix, secondLine)
    upgades_board.add(even, black, odd, thirdLine)
    return upgades_board
#сообщения юзеру
def message_bought_upgrade(user_message, a):
    return f"Успешно куплено апгрейдов: {a}\nid: `{user_message.from_user.id}`\nАпгрейды: {fileRead['users'][str(user_message.from_user.id)]['sec']}/сек; {fileRead['users'][str(user_message.from_user.id)]['click']}/клик; {rec_file.get_skidka(user_message.from_user.id, fileRead)}% скидки; {rec_file.get_boost_balance(user_message.from_user.id, fileRead)}% баланса/день\nБаланс: {rec_file.ob_chisla(fileRead['users'][str(user_message.from_user.id)]['balance'])} КШ"
def message_not_enough_money_click(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(str(rec_file.cal_boost_click(user_message.from_user.id, fileRead) - rec_file.get_balance(user_message.from_user.id, fileRead)))} КШ"
def message_not_enough_money_sec(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(rec_file.cal_boost_sec(user_message.from_user.id, fileRead) - rec_file.get_balance(user_message.from_user.id, fileRead))} КШ"
def message_not_enough_money_boost_balance(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(rec_file.cal_boost_balance(user_message.from_user.id, fileRead)[0] - rec_file.get_balance(user_message.from_user.id, fileRead))} КШ"
def sendmessage_check_active_keyboard(chatid, userid, userOrGroup, send_message):
    if (userOrGroup == "private"):
        if rec_file.get_keyboard(userid, fileRead):
            if rec_file.get_active_passive_keyboard(userid, fileRead) == 1: bot.send_message(chatid, send_message, reply_markup=upgades_buttons(userid), disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется с обновленными ценами в клавиатуре
            else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется без клавиатуры
        else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")
    else:
        if (fileRead["groups"][str(chatid)]["keyboard"]):
            if (fileRead["groups"][str(chatid)]["activeKeyboard"]): bot.send_message(chatid, send_message, reply_markup=upgades_buttons(userid), disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется с обновленными ценами в клавиатуре
            else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется без клавиатуры
        else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")
def message_max_skidka():
    return "Достигнут максимум апгрейдов скидки"
def message_max_boost_balance():
    return "Достигнут максимум апгрейдов баланса/день"
def message_not_enough_money_skidka(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(str(rec_file.cal_boost_skidka(user_message.from_user.id, fileRead) - rec_file.get_balance(user_message.from_user.id, fileRead)))} КШ"
def message_bot_not_started():
    return "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!"
#другое
def manual_backup():
    today = datetime.datetime.today()
    name = "backup-" + today.strftime("%Y-%m-%d_%H.%M.%S") + ".txt"
    shutil.copyfile("usrs.json", f"backups/{name}")
    y.upload(f"backups/{name}", (f"/kkh_backups/{name}"))
    return "Бэкап успешно выполнен и загружен на сервер!"
   
def check_messages(message, message_text):
    i = 0
    checkCommand = message_text[0]
    while True:
        if i > 3: return False
        if checkCommand in COMMANDS.keys():
            kmd(message).checkReg()
            if "link" in COMMANDS[checkCommand].keys(): checkCommand = COMMANDS[checkCommand]["link"]
            if COMMANDS[checkCommand]["permissions"] == "admin" and rec_file.get_admin(message.from_user.id, fileRead) == False: return False
            if COMMANDS[checkCommand]["permissions"] == "owner" and message.from_user.id != config["ownerId"]: return False
            eval(COMMANDS[checkCommand]["action"])
            break
        i += 1
        if i != len(message_text) - 1: return False
        checkCommand += f" { message_text[i]}"
def repeat_command(message):
    messageLog.info(f"TEXT (repeat): {message.chat.id}: {getName(message.from_user.id)} ({message.from_user.id}): {message.text}")
    command = rec_file.get_last_command(message.from_user.id, fileRead)
    comm = None
    try: comm = int(command)
    except: pass
    if comm == "": bot.send_message(message.chat.id, "Последняя команда не обнаружена")
    else:
        message.text = command
        send_text(message)
#kmd
class kmd:
    def __init__(self, message, message_text = None) -> None:
        self.message = message
        self.message_text = message_text
    def click(message, message_text):
        rec_file.click_nachislenie(message.from_user.id, fileRead)
        bot.send_message(message.chat.id, f"Коллекция кристальных шаров пополнена!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(message.from_user.id, fileRead))} КШ")
    def buy_sec(message, message_text):
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_sec(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, fileRead), fileRead)
            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
            rec_file.append_sec(message.from_user.id, 1, fileRead)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_sec(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_sec(message.from_user.id, fileRead):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, fileRead), fileRead)
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
                        rec_file.append_sec(message.from_user.id, 1, fileRead)
                        a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                if message_text[1] == "все" or message_text[1] == "всё":
                    if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_sec(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
                    while rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_sec(message.from_user.id, fileRead):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, fileRead), fileRead)
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
                        rec_file.append_sec(message.from_user.id, 1, fileRead)
                        a += 1
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                elif (len(message_text) >= 3):
                    try:
                        if message_text[1][0] == "(" and message_text[2][-1] == ")":
                            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_sec(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, fileRead), fileRead)
                            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
                            rec_file.append_sec(message.from_user.id, 1, fileRead)
                            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))  
                        else:
                            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, "Неверный параметр +сек [кол-во апгрейдов]")
                    except: pass
    def buy_click(message, message_text):
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_click(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_click(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, fileRead), fileRead)
            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, fileRead)
            rec_file.append_click(message.from_user.id, 1, fileRead)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_click(message.from_user.id, fileRead): return  bot.send_message(message.chat.id, message_not_enough_money_click(message))
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_click(message.from_user.id, fileRead):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, fileRead), fileRead)
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, fileRead)
                        rec_file.append_click(message.from_user.id, 1, fileRead)
                        a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                if message_text[1] == "все" or message_text[1] == "всё":
                    if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_click(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_click(message))
                    while rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_click(message.from_user.id, fileRead):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, fileRead), fileRead)
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, fileRead)
                        rec_file.append_click(message.from_user.id, 1, fileRead)
                        a += 1
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                elif (len(message_text) >= 3):
                    try:
                        if message_text[1][0] == "(" and message_text[2][-1] == ")":
                            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_click(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_click(message))
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, fileRead), fileRead)
                            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, fileRead)
                            rec_file.append_click(message.from_user.id, 1, fileRead)
                            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                        else:
                            bot.send_message(message.chat.id, "Неверный параметр +клик [кол-во апгрейдов]")
                    except:
                        pass
    def buy_skidka(message, message_text):
        if rec_file.get_skidka(message.from_user.id, fileRead) >= 25: return bot.send_message(message.chat.id, message_max_skidka())
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_skidka(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_skidka(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, fileRead), fileRead)
            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, fileRead)
            rec_file.append_skidka(message.from_user.id, 1, fileRead)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_skidka(message.from_user.id, fileRead) < 25:
                        if rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_skidka(message.from_user.id, fileRead):
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, fileRead), fileRead)
                            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, fileRead)
                            rec_file.append_skidka(message.from_user.id, 1, fileRead)
                            a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                if message_text[1] == "все" or message_text[1] == "всё":
                    if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_skidka(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_skidka(message))
                    while rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_skidka(message.from_user.id, fileRead) and rec_file.get_skidka(message.from_user.id, fileRead) < 25:
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, fileRead), fileRead)
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, fileRead)
                        rec_file.append_skidka(message.from_user.id, 1, fileRead)
                        a += 1
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                else: bot.send_message(message.chat.id, "Неверный параметр +скидка [кол-во апгрейдов]")
    def buy_skidka_2(message, message_text):
        if rec_file.get_skidka(message.from_user.id, fileRead) >= 25: return bot.send_message(message.chat.id, message_max_skidka())
        if len(message_text) >= 4:
            if message_text[1] == 'скидки':
                try:
                    if message_text[2][0] == "(" and message_text[3][-1] == ")":
                        if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_skidka(message.from_user.id, fileRead): return bot.send_message(message.chat.id, message_not_enough_money_skidka(message))
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, fileRead), fileRead)
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, fileRead)
                        rec_file.append_skidka(message.from_user.id, 1, fileRead)
                        sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                except: pass
    def price(message, message_text):
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: цена <сек/клик/скидка>")
        if message_text[1] == "сек" or message_text[1] == "+сек": bot.send_message(message.chat.id, f"Цена за {fileRead['users'][str(message.from_user.id)]['sec'] + 1} апгрейд +сек со скидкой {rec_file.get_skidka(message.from_user.id, fileRead)}%: {rec_file.ob_chisla(rec_file.cal_boost_sec(message.from_user.id, fileRead))} КШ")
        elif message_text[1] == "клик" or message_text[1] == "+клик": bot.send_message(message.chat.id, f"Цена за {fileRead['users'][str(message.from_user.id)]['click'] + 1} апгрейд +клик со скидкой {rec_file.get_skidka(message.from_user.id, fileRead)}%: {rec_file.ob_chisla(rec_file.cal_boost_click(message.from_user.id, fileRead))} КШ")
        elif message_text[1] == "скидка" or message_text[1] == "+скидка" or message_text[1] == "скидки" or message_text[1] == "+скидки":
            if rec_file.get_skidka(message.from_user.id, fileRead) < 25: bot.send_message(message.chat.id, f"Цена за {rec_file.get_skidka(message.from_user.id, fileRead) + 1} апгрейд со скидкой {rec_file.get_skidka(message.from_user.id, fileRead)}%: {rec_file.ob_chisla(rec_file.cal_boost_skidka(message.from_user.id, fileRead))} КШ")
            else: bot.send_message(message.chat.id, message_max_skidka())
        elif message_text[1] == "бб" or message_text[1] == "+бб" or message_text[1] == "баланс" or message_text[1] == "баланса" or message_text[1] == "+баланса" or message_text[1] == "+баланс" or message_text[1] == "баланс/день" or message_text[1] == "+баланс/день":
            if rec_file.get_boost_balance(message.from_user.id, fileRead) < rec_file.cal_boost_balance(message.from_user.id, fileRead)[1]: bot.send_message(message.chat.id, f"Цена за {rec_file.get_boost_balance(message.from_user.id, fileRead) + 1} апгрейд со скидкой {rec_file.get_skidka(message.from_user.id, fileRead)}%: {rec_file.ob_chisla(rec_file.cal_boost_balance(message.from_user.id, fileRead)[0])} КШ")
            else: bot.send_message(message.chat.id, message_max_boost_balance())
        else: bot.send_message(message.chat.id, "Неизвестный тип")
    def add_money(message, message_text):
        if len(message_text) <= 2: return bot.send_message(message.chat.id, "Использование: добавить <id/себе> <сумма>")
        sum = rec_file.ob_k_chisla(message_text[2])
        if message_text[1] == "_":
            userid = message.reply_to_message
            if userid != None: userid = userid.from_user.id
            else: userid = 0
        elif message_text[1] == "себе":
            try:
                userid = message.from_user.id
                rec_file.append_balance(userid, int(rec_file.ob_k_chisla(sum)), fileRead)
                fileRead["users"][str(userid)]["othersProceeds"] += int(rec_file.ob_k_chisla(sum))
                bot.send_message(message.chat.id, f"Вам начислено {rec_file.ob_chisla(sum)} КШ")
            except ValueError:
                bot.send_message(message.chat.id, "Использование: добавить <id/себе> <сумма>")
        else: userid = getId(message_text[1])
        if userid not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, "Юзер не найден!")
        rec_file.append_balance(userid, int(rec_file.ob_k_chisla(sum)), fileRead)
        fileRead["users"][str(userid)]["othersProceeds"] += int(rec_file.ob_k_chisla(sum))
        bot.send_message(message.chat.id, f"Пользователю {getTag(userid)} ({rec_file.getFullName(userid, fileRead)}) начислено {rec_file.ob_chisla(sum)} КШ")
        bot.send_message(userid, f"Вам начислено {rec_file.ob_chisla(sum)} КШ администратором")
    def addMoneyBank(message, message_text):
        if len(message_text) <= 2: return bot.send_message(message.chat.id, "Использование: добавить <id/себе> <сумма>")
        sum = rec_file.ob_k_chisla(message_text[2])
        if message_text[1] == "_":
            userid = message.reply_to_message
            if userid != None: userid = userid.from_user.id
            else: userid = 0
        elif message_text[1] == "себе":
            try:
                rec_file.appendBank(message.from_user.id, int(rec_file.ob_k_chisla(sum)), fileRead)
                fileRead["users"][str(message.from_user.id)]["othersProceeds"] += int(rec_file.ob_k_chisla(sum))
                bot.send_message(message.chat.id, f"Вам начислено {rec_file.ob_chisla(sum)} КШ в банк")
            except ValueError:
                bot.send_message(message.chat.id, "Использование: добавить <id/себе> <сумма>")
        else: userid = getId(message_text[1])
        if userid not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, "Юзер не найден!")
        rec_file.appendBank(userid, int(rec_file.ob_k_chisla(sum)), fileRead)
        fileRead["users"][str(userid)]["othersProceeds"] += int(rec_file.ob_k_chisla(sum))
        bot.send_message(message.chat.id, f"Пользователю {getTag(userid)} ({rec_file.getFullName(userid, fileRead)}) начислено {rec_file.ob_chisla(sum)} КШ в банк")
        bot.send_message(userid, f"Вам начислено {rec_file.ob_chisla(sum)} КШ в банк администратором")
    def balance(message, message_text):
        if len(message_text) == 1: bot.send_message(message.chat.id, f"Имя: {rec_file.getFullName(message.from_user.id, fileRead)}\nid: `{message.from_user.id}`\nАпгрейды: {fileRead['users'][str(message.from_user.id)]['sec']}/сек; {fileRead['users'][str(message.from_user.id)]['click']}/клик; {rec_file.get_skidka(message.from_user.id, fileRead)}% скидки; {rec_file.get_boost_balance(message.from_user.id, fileRead)}% баланса/день\nБаланс: {rec_file.ob_chisla(fileRead['users'][str(message.from_user.id)]['balance'])} КШ\nВ банке: {rec_file.ob_chisla(fileRead['users'][str(message.from_user.id)]['bank'])} КШ", parse_mode="MARKDOWN")
        elif len(message_text) >= 2:
            try:
                if message_text[1] == "_":
                    userid = message.reply_to_message
                    if userid != None: userid = userid.from_user.id
                    else: userid = 0
                else: userid = getId(message_text[1])
                if userid not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, "id не найден")
                bot.send_message(message.chat.id, f"Имя: {rec_file.getFullName(userid, fileRead)}\nid: `{userid}`\nАпгрейды: {fileRead['users'][str(userid)]['sec']}/сек; {fileRead['users'][str(userid)]['click']}/клик; {rec_file.get_skidka(userid, fileRead)}% скидки; {rec_file.get_boost_balance(userid, fileRead)}% баланса/день\nБаланс: {rec_file.ob_chisla(fileRead['users'][str(userid)]['balance'])} КШ\nВ банке: {rec_file.ob_chisla(fileRead['users'][str(userid)]['bank'])} КШ", parse_mode="MARKDOWN")
            except ValueError: bot.send_message(message.chat.id, "Использование: Баланс/б [id]")
    def upgrades(message, message_text):
        rec_file.set_active_passive_keyboard(message.chat.id, True, bot.get_chat(message.chat.id).type, fileRead)
        if (bot.get_chat(message.chat.id).type == "private"):
            if rec_file.get_keyboard(message.from_user.id, fileRead) == True:
                bot.send_message(message.chat.id, "Открыто меню апгрейдов", reply_markup=upgades_buttons(message.from_user.id))
            elif rec_file.get_keyboard(message.from_user.id, fileRead) == False:
                bot.send_message(message.chat.id, "Открыто меню апгрейдов")
        else:
            if (fileRead["groups"][str(message.chat.id)]["keyboard"]):
                bot.send_message(message.chat.id, "Открыто меню апгрейдов", reply_markup=upgades_buttons(message.from_user.id))
            if (fileRead["groups"][str(message.chat.id)]["keyboard"] == False):
                bot.send_message(message.chat.id, "Открыто меню апгрейдов")
    def back(message, message_text):
        if (bot.get_chat(message.chat.id).type == "private"):
            if rec_file.get_keyboard(message.from_user.id, fileRead): bot.send_message(message.chat.id, "Вы вышли из меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Вы вышли из меню")
        else:
            if (fileRead["groups"][str(message.chat.id)]["keyboard"]): bot.send_message(message.chat.id, "Вы вышли из меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Вы вышли из меню")
        rec_file.set_active_passive_keyboard(message.chat.id, False, bot.get_chat(message.chat.id).type, fileRead)
    def moneta(message, message_text):
        if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: монета <ставка/всё> <орел/решка>")
        if message_text[1] == "все" or message_text[1] == "всё": bot.send_message(message.chat.id, rec_file.moneta_stavka(message.from_user.id, str(rec_file.get_balance(message.from_user.id, fileRead)), message_text[2], fileRead))
        else:
            sum = rec_file.ob_k_chisla(message_text[1])
            bot.send_message(message.chat.id, rec_file.moneta_stavka(message.from_user.id, sum, message_text[2], fileRead))
    def reset(message, message_text):
        if len(message_text) < 2: return bot.send_message(message.chat.id, config["messages"]["resetHelp"], parse_mode="MARKDOWN")
        if message_text[1] == "подтвердить":
            rec_file.clear_id(message.from_user.id, fileRead)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, "Ваш прогресс сброшен!")
        elif message_text[1] == "справка": bot.send_message(message.chat.id, config["messages"]["resetHelp"], parse_mode="MARKDOWN")
        else:
            if rec_file.get_admin(message.from_user.id, fileRead):
                try:
                    if message_text[1] == "_":
                        a = message.reply_to_message
                        if a != None: a = a.from_user.id
                        else: a = 0
                    else: a = getId(message_text[1])
                    if a not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, "Такой id не найден!")
                    if (rec_file.get_admin(a, fileRead) == True and message.from_user.id != 357694314): return bot.send_message(message.chat.id, "Невозможно применить эту команду к этому пользователю")
                    rec_file.clear_id(a, fileRead)
                    bot.send_message(message.chat.id, f"Прогресс пользователя {rec_file.getFullName(a, fileRead)} (`{a}`) успешно сброшен!", parse_mode="MARKDOWN")
                    sendmessage_check_active_keyboard(a, a, bot.get_chat(message.chat.id).type, "Ваш прогресс сброшен администратором!")
                except ValueError: return bot.send_message(message.chat.id, "Использование: сброс <подтвердить/справка/id юзера>")
            if rec_file.get_admin(message.from_user.id, fileRead) == 0: bot.send_message(message.chat.id, "Использование: сброс <подтвердить/справка>")
    def pay(message, message_text):
        if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: перевод <сумма> <id получателя> [комментарий]")
        if (message_text[1] == "#r"): sum = random.randint(1, rec_file.get_balance(message.from_user.id, fileRead))
        else:
            if message_text[1][-1] == "%":
                if 1 <= int(message_text[1][:-1:]) <= 100:
                    try: sum = rec_file.get_balance(message.from_user.id, fileRead)*int(message_text[1][:-1:])//100
                    except: return bot.send_message(message.chat.id, "Неверное использование процентного перевода. Использование: перевод <1%-100%> <id получателя> [комментарий]")
                else: return bot.send_message(message.chat.id, "Неверное использование процентного перевода. Использование: перевод <1%-100%> <id получателя> [комментарий]")
            else:
                try: sum = int(rec_file.ob_k_chisla(message_text[1]))
                except ValueError:
                    if message_text[1] == "все" or message_text[1] == "всё": sum = int(round(rec_file.get_balance(message.from_user.id, fileRead)))
                    else: return bot.send_message(message.chat.id, "Использование: перевод <сумма> <id получателя> [комментарий]")
        try:
            if message_text[2] == "#r":
                poly4atel = random.choice(rec_file.get_ids(fileRead))
            elif message_text[2] == "_":
                poly4atel = message.reply_to_message
                if poly4atel != None: poly4atel = poly4atel.from_user.id
                else: poly4atel = 0
            else: poly4atel = getId(message_text[2])
            if poly4atel not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, "Пользователь с таким id не найден!")
            if rec_file.get_balance(message.from_user.id, fileRead) < sum: return bot.send_message(message.chat.id, "Недостаточно средств")
            if sum < 100: return bot.send_message(message.chat.id, "Переводы меньше 100 КШ запрещены")
            rec_file.append_balance(message.from_user.id, -sum, fileRead)
            fileRead["users"][str(message.from_user.id)]["paidKkh"] += sum
            rec_file.append_balance(poly4atel, sum, fileRead)
            fileRead["users"][str(poly4atel)]["receivedKkh"] += sum
            send_message = f"Перевод {rec_file.ob_chisla(sum)} КШ пользователю {rec_file.getFullName(poly4atel, fileRead)} ({getTag(poly4atel)}) выполнен успешно!"
            if len(message_text) >= 4:
                comment = message.text.split(" ", 3)[-1]
                send_message = f"{send_message}\nКомментарий к переводу: {comment}"
            bot.send_message(message.chat.id, send_message)
            send_message = f"Получен перевод {rec_file.ob_chisla(sum)} КШ от пользователя {getTag(message.from_user.id)} ({rec_file.getFullName(message.from_user.id, fileRead)})"
            if len(message_text) >= 4: send_message = f"{send_message}\nСообщение: {comment} "
            bot.send_message(poly4atel, send_message) 
        except ValueError: bot.send_message(message.chat.id, "Неверное id получателя! id должно содержать только цифры")
    def admin(message, message_text):
        if message.from_user.id == 357694314:
            if len(message_text) == 1: bot.send_message(message.chat.id, "Использование: админ [добавить/удалить] <id>")
            elif len(message_text) >= 2:
                if message_text[1] == "добавить" or message_text[1] == "назначить":
                    if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: админ добавить <id>")
                    try: user = getId(message_text[2])
                    except:
                        if message_text[2] == "себя" or message_text[2] == "себе" or message_text[2] == "я": user = message.from_user.id
                        elif (message_text[2] == "_") and (message.reply_to_message != None): user = message.reply_to_message.from_user.id;
                        else: return bot.send_message(message.chat.id, "Использование: админ добавить <id>")
                    if user not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` не найден", parse_mode="MARKDOWN")
                    if rec_file.get_admin(user, fileRead): return bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` уже имеет права администратора", parse_mode="MARKDOWN")
                    rec_file.set_admin(user, fileRead)
                    bot.send_message(message.chat.id, f"Пользователь {rec_file.getFullName(user, fileRead)} ({message_text[2]}) назначен администратором!")
                    bot.send_message(user, "Вас назначили администратором, ведите себя хорошо!")
                elif message_text[1] == "удалить" or message_text[1] == "снять":
                    if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: админ удалить <id>")
                    try: user = getId(message_text[2])
                    except:
                        if message_text[2] == "себя" or message_text[2] == "себе" or message_text[2] == "я": user = message.from_user.id
                        elif (message_text[2] == "_") and (message.reply_to_message != None): user = message.reply_to_message.from_user.id;
                        else: return bot.send_message(message.chat.id, "Использование: админ удалить <id>")
                    if user not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` не найден", parse_mode="MARKDOWN")
                    if rec_file.get_admin(user, fileRead) == False: return bot.send_message(message.chat.id, f"Пользователь {rec_file.getFullName(user, fileRead)} ({message_text[2]}) не имеет прав администратора!")
                    rec_file.unset_admin(user, fileRead)
                    bot.send_message(message.chat.id, f"С пользователя {rec_file.getFullName(user, fileRead)} ({message_text[2]}) сняты права администратора!")
                    bot.send_message(user, "С вас сняты права администатора!")  
                else: bot.send_message(message.chat.id, "Использование: админ [добавить/удалить] <id>")
        else:
            if rec_file.get_admin(message.from_user.id, fileRead) == True: bot.send_message(message.chat.id, "Ты админ")
            else: bot.send_message(message.chat.id, "Ты не админ")
    def bonus(message, message_text):
        if rec_file.get_time_now() - rec_file.get_time_give_bonus(message.from_user.id, fileRead) < 86400: return bot.send_message(message.chat.id, f"Ежедневный бонус уже был получен сегодня\nДо следующего бонуса: {rec_file.ob_vremeni_bonusa(rec_file.get_time_give_bonus(message.from_user.id, fileRead) + 86400 - rec_file.get_time_now())}")
        bot.send_message(message.chat.id, rec_file.give_bonus(message.from_user.id, fileRead))
        rec_file.set_time_give_bonus(message.from_user.id, message.date, fileRead)
    def bonus2(message, message_text):
        if (rec_file.get_time_now() - rec_file.get_time_give_bonus2(message.from_user.id, fileRead)) < 28800: return bot.send_message(message.chat.id, f"Бонус2 можно получать каждые 8 часов\nДо следующего бонуса2: {rec_file.ob_vremeni_bonusa(rec_file.get_time_give_bonus2(message.from_user.id, fileRead) + 28800 - rec_file.get_time_now())}")
        rec_file.set_time_give_bonus2(message.from_user.id, message.date, fileRead)
        bot.send_message(message.chat.id, rec_file.give_bonus2(message.from_user.id, fileRead))
    def activate_promo(message, message_text):
        global fileRead
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: промо <код>")
        fileRead, inf_message = rec_file.activation_promo(message.from_user.id, message_text[1], fileRead)
        bot.send_message(message.chat.id, inf_message)
    def keyboard(message, message_text):
        if len(message_text) == 2:
            if message_text[1] == "нет" or message_text[1] == "выключить":
                rec_file.keyboard_off(message.chat.id, bot.get_chat(message.chat.id).type, fileRead)
                bot.send_message(message.chat.id, "Клавиатура отключена", reply_markup=types.ReplyKeyboardRemove())
            elif message_text[1] == "да" or message_text[1] == "включить":
                rec_file.keyboard_on(message.chat.id, bot.get_chat(message.chat.id).type, fileRead)
                bot.send_message(message.chat.id, "Клавиатура включена", reply_markup=main_menu_buttons())
        else:
            bot.send_message(message.chat.id, "Использование: Клавиатура <да/нет>")
    def rassilka(message, message_text):
        if len(message_text) >= 3:
            if rec_file.get_admin(message.from_user.id, fileRead) == True:
                if message_text[1] == "создать":
                    msg = message.text.split(" ", 2)[-1]
                    send_message = f"{msg}\n\n____\nДля отключения рассылки введите рассылка нет"
                    for i in rec_file.get_ids(fileRead):
                        if rec_file.get_rassilka(i, fileRead) == True:
                            try:
                                bot.send_message(i, send_message)
                            except: pass
                    bot.send_message(message.chat.id, send_message)
                else: bot.send_message(message.chat.id, "Использование: рассылка <создать> <сообщение>")
            else: bot.send_message(message.chat.id, "Использование: рассылка <да/нет>")
        elif len(message_text) == 2 and (message_text[1] == "да" or message_text[1] == "нет"):
            if message_text[1] == "да":
                rec_file.set_rassilka(message.from_user.id, True, fileRead)
                bot.send_message(message.chat.id, "Рассылка включена.\nДля отключения введите рассылка нет")
            elif message_text[1] == "нет":
                rec_file.set_rassilka(message.from_user.id, False, fileRead)
                bot.send_message(message.chat.id, "Рассылка отключена.\nДля включения введите рассылка да")
            else: bot.send_message(message.chat.id, "Использование: рассылка <да/нет>")
        else:
            if rec_file.get_admin(message.from_user.id, fileRead) == True: bot.send_message(message.chat.id, "Использование: рассылка <да/нет> или рассылка <создать> <сообщение>")
            else: bot.send_message(message.chat.id, "Использование: рассылка <да/нет>")
    def backup(message, message_text):
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: бэкап <создать>\nСоздаёт бэкап в папку с бекапами и загружает в облако.")
        if message_text[1] == "создать": bot.send_message(message.chat.id, manual_backup())
        else: bot.send_message(message.chat.id, "Использование: бэкап <создать>")
    def buy_procent_balance(message, message_text):
        if rec_file.get_boost_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_balance(message.from_user.id, fileRead)[1]: return bot.send_message(message.chat.id, message_max_boost_balance())
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]: return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, fileRead)[0], fileRead)
            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
            rec_file.append_boost_balance(message.from_user.id, 1, fileRead)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]: return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]:
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, fileRead)[0], fileRead)
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
                        rec_file.append_boost_balance(message.from_user.id, 1, fileRead)
                        a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                try:
                    if message_text[1][0] == "(" and message_text[2][-1] == ")":
                        if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]: return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, fileRead), fileRead)[0]
                        fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
                        rec_file.append_boost_balance(message.from_user.id, 1, fileRead)
                        sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                    elif message_text[1] == "все" or message_text[1] == "всё":
                        if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]: return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
                        while rec_file.get_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_balance(message.from_user.id, fileRead)[0] and rec_file.get_boost_balance(message.from_user.id, fileRead) < rec_file.cal_boost_balance(message.from_user.id, fileRead)[1]:
                            if rec_file.get_boost_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_balance(message.from_user.id, fileRead)[1]: return bot.send_message(message.chat.id, message_max_boost_balance())
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, fileRead)[0], fileRead)
                            fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
                            rec_file.append_boost_balance(message.from_user.id, 1, fileRead)
                            a += 1
                        sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                    else:
                        sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, "Неверный параметр +сек [кол-во апгрейдов]")
                except:
                    pass
    def buy_procent_balance_2(message, message_text):
        if rec_file.get_boost_balance(message.from_user.id, fileRead) >= rec_file.cal_boost_balance(message.from_user.id, fileRead)[1]: return bot.send_message(message.chat.id, message_max_boost_balance())
        if len(message_text) >= 2:
            if message_text[1] == "баланса/день":
                try:
                    if rec_file.get_balance(message.from_user.id, fileRead) < rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]: return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
                    rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, fileRead)[0], fileRead)
                    fileRead["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, fileRead)[0]
                    rec_file.append_boost_balance(message.from_user.id, 1, fileRead)
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                except: pass
    def main_menu(message, message_text):
        if (bot.get_chat(message.chat.id).type == "private"):
            if rec_file.get_keyboard(message.from_user.id, fileRead) == True: bot.send_message(message.chat.id, "Открыто главное меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Открыто главное меню")
        else:
            if (fileRead["groups"][str(message.chat.id)]["keyboard"]): bot.send_message(message.chat.id, "Открыто главное меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Открыто главное меню")
        rec_file.set_active_passive_keyboard(message.chat.id, False, bot.get_chat(message.chat.id).type, fileRead)
    def full_inf_user(message, message_text):
        if len(message_text) >= 2:
            if message_text[1] == "_":
                if message.reply_to_message == None: return bot.send_message(message.chat.id, "Использовать _ можно только при ответе на сообщение")
                id = message.reply_to_message.from_user.id
            else: id = getId(message_text[1])
        else: id = message.from_user.id
        if str(id) not in fileRead["users"].keys(): return bot.send_message(message.chat.id, "ID не найден")
        msg = ""
        for i in fileRead["users"][str(id)].keys():
            if (type(fileRead['users'][str(id)][i]) == int):
                msg += f"{i}: {rec_file.ob_chisla(fileRead['users'][str(id)][i])}" + "\n"
            else: msg += f"{i}: {fileRead['users'][str(id)][i]}" + "\n"
        bot.send_message(message.chat.id, msg)
    def del_user(message, message_text):
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: дюзер <id>")
        try: id = getId(message_text[1])
        except ValueError:
            if message_text[1] == "_":
                if (message.reply_to_message != None): id = message.reply_to_message.from_user.id;
                else: return bot.send_message(message.chat.id, "ID дожден состоять только из цифр!")
            return bot.send_message(message.chat.id, "ID дожден состоять только из цифр!")
        if id not in rec_file.get_ids(fileRead): return bot.send_message(message.chat.id, "ID не найден")
        if (rec_file.get_admin(id, fileRead) == True and message.from_user.id != 357694314): return bot.send_message(message.chat.id, "Невозможно использование дюзер для этого пользователя")
        name = rec_file.getFullName(id, fileRead)
        rec_file.remove_id(id, fileRead)
        bot.send_message(message.chat.id, f"{name}: ID удалён из бд")
    def userlist(message, message_text):
        send_message = f"Вот id всех {len(fileRead['users'].keys()) - 1} пользователей:"
        for i in fileRead["users"].keys():
            if (i != "default"):
                name = f"{fileRead['users'][i]['firstName']}"
                if (fileRead['users'][i]['lastName'] != None):
                    name += f" {fileRead['users'][i]['lastName']}"
                send_message += f"\n<a href='tg://user?id={i}'>{name}</a> ({i}), "
        send_message = send_message[:-2:]
        bot.send_message(message.chat.id, send_message, parse_mode="HTML")
    def manual_write_file(message, message_text):
        updateUsersNameInFile()
        rec_file.write(fileRead)
        bot.send_message(message.chat.id, "БД записана")
    def addPromo(message, message_text):
        if (len(message_text) < 5):
            message.text = "команда нпромо"
            message_text = message.text.split(" ")
            return kmd.helpCommand(message, message_text)
        name = message_text[1];
        a = message.text.partition('{')
        b = a[2].partition('}')
        c = b[2][1:]
        paramsDictSTR = a[1] + b[0]+ b[1];
        try: paramsDict = json.loads(paramsDictSTR.replace("'",'"'))
        except Exception as e: return bot.send_message(message.chat.id, f"Произошла ошибка, попробуйте ещё раз!\n{e}")
        activationLimit = int(c.split(" ")[0]);
        durationTime = c.split(" ")[1];
        bot.send_message(message.chat.id, rec_file.promo_append(name, paramsDict, activationLimit, durationTime, fileRead));
        #except: return bot.send_message(message.chat.id, f"Использование: промо добавить <название> <params({paramsPromos})> <кол-во активаций> <время действия>")
    def commandsList(message, message_text):
        if (rec_file.get_admin(message.from_user.id, fileRead)): bot.send_message(message.chat.id, config["messages"]["commandsList"]);
        else: bot.send_message(message.chat.id, config["messages"]["commandsListUser"]);
    def helpCommand(message, message_text):
        if (len(message_text) < 2): return bot.send_message(message.chat.id, "Использование: команда <команда>");
        message.text = message.text[8:]
        message_text.pop(0)
        i = 0
        checkCommand = message_text[0]
        while True:
            if i > 3: return False
            if checkCommand in COMMANDS.keys():
                kmd(message).checkReg()
                if "link" in COMMANDS[checkCommand].keys(): checkCommand = COMMANDS[checkCommand]["link"]
                if COMMANDS[checkCommand]["permissions"] == "admin" and rec_file.get_admin(message.from_user.id, fileRead) == False: return False
                if COMMANDS[checkCommand]["permissions"] == "owner" and message.from_user.id != config["ownerId"]: return False
                break
            i += 1
            if i != len(message_text) - 1: return False
            checkCommand += f" { message_text[i]}"
        msg = f"{checkCommand} "
        if "links" in COMMANDS[checkCommand].keys():
            for i in COMMANDS[checkCommand]["links"]:
                msg += f"/ {i} "
        msg = msg[:-1] + f": {COMMANDS[checkCommand]['description']}\nИспользование: {COMMANDS[checkCommand]['usage']}"
        if "parse" in COMMANDS[checkCommand].keys(): return bot.send_message(message.chat.id, msg, parse_mode=COMMANDS[checkCommand]["parse"])
        bot.send_message(message.chat.id, msg);
    def delPromo(message, message_text):
        if (len(message_text) < 2): return bot.send_message(message.chat.id, "Использование: промо удалить <название>");
        bot.send_message(message.chat.id, rec_file.promo_remove(message_text[1], fileRead));
    def sendUser(message, message_text):
        if (len(message_text) < 2) and (message_text[0] == "послать"): return bot.send_message(message.chat.id, "Послать пользователя (1.000.000 КШ): Послать <id юзера>");
        if (len(message_text) < 2) and (message_text[0] == "послатьанон"): return bot.send_message(message.chat.id, "Анонимно послать пользователя (3.000.000 КШ): Послатьанон <id юзера>");
        try: id = getId(message_text[1]);
        except: 
            if (message_text[1] == "_"):
                if (message.reply_to_message != None): id = message.reply_to_message.from_user.id;
                else: return bot.send_message(message.chat.id, "При использовании _ вам необходимо ответить на сообщение юзера");
            else: return bot.send_message(message.chat.id, "ID пользователя должен состоять только из цифр!");
        if (message_text[0] == "послать"):
            if (rec_file.get_balance(message.from_user.id, fileRead) < 1000000): return bot.send_message(message.chat.id, "У вас недостаточно КШ!");
            rec_file.append_balance(message.from_user.id, -1000000, fileRead);
            fileRead["users"][str(message.from_user.id)]["othersSpends"] += 1000000
            bot.send_message(id, f"Вас послал нахуй пользователь {rec_file.getFullName(message.from_user.id, fileRead)} ({getTag(message.from_user.id)})");
            bot.send_message(message.chat.id, f"Вы послали нахуй игрока {rec_file.getFullName(id, fileRead)} ({getTag(id)})\nЗабрано 1.000.000 КШ");
        elif (message_text[0] == "послатьанон"):
            if (rec_file.get_balance(message.from_user.id, fileRead) < 3000000): return bot.send_message(message.chat.id, "У вас недостаточно КШ!");
            rec_file.append_balance(message.from_user.id, -3000000, fileRead);
            fileRead["users"][str(message.from_user.id)]["othersSpends"] += 3000000
            bot.send_message(id, f"Вас анонимно послали нахуй");
            bot.send_message(message.chat.id, f"Вы анонимно послали нахуй игрока {rec_file.getFullName(id, fileRead)} ({getTag(id)})\nЗабрано 3.000.000 КШ");
    def promoInf(message, message_text):
        if (len(message_text) < 2): return bot.send_message(message.chat.id, "Использование: промо инфо <название промокода>")
        if (rec_file.promo_check(message_text[1]) == False): return bot.send_message(message.chat.id, f"Промокод {message_text[1]} не найден!")
        bot.send_message(message.chat.id, rec_file.promo_info(message_text[1]))
    def promoList(message, message_text):
        bot.send_message(message.chat.id, rec_file.promo_list())
    def userTop(message, message_text):
        top = {"mode": "б", "page": 1, "active": True}
        if message_text[0] == "всетоп": top["active"] = False
        if (len(message_text) == 1): pass
        elif (len(message_text) == 2):
            top["mode"] = message_text[1]
        elif (len(message_text) >= 3):
            try: top["page"] = int(message_text[2])
            except:
                return bot.send_message(message.chat.id, "Страница топа должна быть числом")
            top["mode"] = message_text[1]
        return bot.send_message(message.chat.id, rec_file.leaderboard(fileRead, top["mode"], message.from_user.id, top["page"], top["active"]), parse_mode="HTML")
    def btcBet(message, message_text):
        if (len(message_text) < 3): return bot.send_message(message.chat.id, "Использование: бит <ставка> <вверх/вниз>")
        try: betAmount = int(rec_file.ob_k_chisla(message_text[1]))
        except: 
            if (message_text[1] == "#r"): betAmount = random.randint(1, rec_file.get_balance(message.from_user.id, fileRead))
            elif (message_text[1] == "все") or (message_text[1] == "всё"): betAmount = rec_file.get_balance(message.from_user.id, fileRead)
            elif (message_text[1][-1] == "%"):
                message_text[1] = message_text[1][:-1]
                try: message_text[1] = int(message_text[1])
                except: return bot.send_message(message.chat.id, "Неверное использование процентной ставки. Процентная ставка должна быть не менее 1 и не более 100% от вашего баланса и иметь численное значение!")
                if (0 < message_text[1] <= 100): betAmount = rec_file.get_balance(message.from_user.id, fileRead) * message_text[1] // 100
                else: return bot.send_message(message.chat.id, "Неверное использование процентной ставки. Процентная ставка должна быть не менее 1 и не более 100% от вашего баланса!")
            else: return bot.send_message(message.chat.id, "Ставка должна иметь численный вид")
        if (0 < betAmount <= rec_file.get_balance(message.from_user.id, fileRead)):
            variants = ["вверх", "вниз"]
            if (message_text[2] not in variants):
                if message_text[2] != "#r": return bot.send_message(message.chat.id, "Использование: бит <ставка> <вверх/вниз>")
                else: message_text[2] = random.choice(variants)
            rec_file.append_balance(message.from_user.id, -betAmount, fileRead)
            bot.send_message(message.chat.id, f"Ваша ставка {rec_file.ob_chisla(betAmount)} КШ, ждем минуту!")
            Thread(target=bitcoinBet, args=(message.from_user.id, message_text[2], betAmount, message.chat.id)).start()
        else: return bot.send_message(message.chat.id, "Неверная ставка (меньше нуля или больше вашего баланса)")
    def roulette(message, message_text):
        if (len(message_text) == 1): return bot.send_photo(message.chat.id, "AgACAgIAAxkBAAEERyxh0ZLbF82ZvyLwUJfjbOvxh2Z3PwAC2rcxGyzskEoC-uMjPRKv6gEAAwIAA3kAAyME", reply_markup=rouletteKeyboard())
        # if (len(message_text) == 1): return bot.send_photo(message.chat.id, "AgACAgIAAxkBAAJS5mMcm3T2QwGsS2gw_Iq0k4jGAVf-AAI8tTEb4KQ5S_X7F-E3605YAQADAgADbQADKQQ", reply_markup=rouletteKeyboard())
        else: bot.send_photo(message.chat.id, "AgACAgIAAxkBAAEERyxh0ZLbF82ZvyLwUJfjbOvxh2Z3PwAC2rcxGyzskEoC-uMjPRKv6gEAAwIAA3kAAyME")
        # else: bot.send_photo(message.chat.id, "AgACAgIAAxkBAAJS5mMcm3T2QwGsS2gw_Iq0k4jGAVf-AAI8tTEb4KQ5S_X7F-E3605YAQADAgADbQADKQQ")
        if (len(message_text) < 3): return bot.send_message(message.chat.id, config["messages"]["rouletteHelp"])
        betAmount = message_text[1]
        bet = message_text[2]
        if bet in ["1:3", "1:3(2)", "1:3(3)", "1st12", "2nd12", "3rd12", "1to18", "19to36", "even", "odd", "red", "black"]: 

            return rouletteButtonsBet(betAmount, bet, message.from_user.id, message.chat.id)
        elif (bet == "#r"): return rouletteButtonsBet(betAmount, random.randint(0, 36), message.from_user.id, message.chat.id)
        else:
            try: bet = int(bet)
            except: return bot.send_message(message.chat.id, "Неправильная ставка")
            if (bet < 0 or bet > 36): return bot.send_message(message.chat.id, "Неправильная ставка")
            return rouletteButtonsBet(betAmount, bet, message.from_user.id, message.chat.id)
    def bankPut(message, message_text):
        fee = 0.2#% (комиссия)
        if (len(message_text) < 2): sum = rec_file.get_balance(message.from_user.id, fileRead)
        else:
            if (message_text[1] == "все" or message_text[1] == "всё"): sum = rec_file.get_balance(message.from_user.id, fileRead)
            elif (message_text[1][-1] == "%"):
                sum = message_text[1][:-1]
                try: sum = int(sum)
                except: return bot.send_message(message.chat.id, "Неверное использование процентного числа. Процентное число должно быть не менее 1 и не более 100% от вашего баланса и иметь численное значение!")
                if (0 < sum <= 100): sum = rec_file.get_balance(message.from_user.id, fileRead) * sum // 100
                else: return bot.send_message(message.chat.id, "Неверное использование процентного числа. Процентное число должно быть не менее 1 и не более 100% от вашего баланса!")
            else:
                try: sum = int(rec_file.ob_k_chisla(message_text[1]))
                except: return bot.send_message(message.chat.id, "Использование: +банк [сумма]")
        if (rec_file.get_balance(message.from_user.id, fileRead) < sum): return bot.send_message(message.chat.id, "Недостаточно средств на балансе!")
        feeSum = int(sum*fee/100)
        fileRead["users"][str(message.from_user.id)]["balance"] -= sum
        fileRead["users"][str(message.from_user.id)]["bank"] += (sum - feeSum)
        fileRead["users"][str(message.from_user.id)]["paidKkh"] += feeSum
        bot.send_message(message.chat.id, f"Переведено {rec_file.ob_chisla(sum)} КШ в банк\nКомиссия {rec_file.ob_chisla(feeSum)} КШ ({fee}%)\nВ банке: {rec_file.ob_chisla(rec_file.getBank(message.from_user.id, fileRead))} КШ\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(message.from_user.id, fileRead))} КШ")
    def bankTake(message, message_text):
        fee = 0.2#% (комиссия)
        if (len(message_text) < 2): sum = rec_file.getBank(message.from_user.id, fileRead)
        else:
            if (message_text[1] == "все" or message_text[1] == "всё"): sum = rec_file.getBank(message.from_user.id, fileRead)
            elif (message_text[1][-1] == "%"):
                sum = message_text[1][:-1]
                try: sum = int(sum)
                except: return bot.send_message(message.chat.id, "Неверное использование процентного числа. Процентное число должно быть не менее 1 и не более 100% от баланса в банке и иметь численное значение!")
                if (0 < sum <= 100): sum = rec_file.getBank(message.from_user.id, fileRead) * sum // 100
                else: return bot.send_message(message.chat.id, "Неверное использование процентного числа. Процентное число должно быть не менее 1 и не более 100% от баланса в банке!")
            else:
                try: sum = int(rec_file.ob_k_chisla(message_text[1]))
                except: return bot.send_message(message.chat.id, "Использование: -банк [сумма]")
        if (rec_file.getBank(message.from_user.id, fileRead) < sum): return bot.send_message(message.chat.id, "Недостаточно средств а банке!")
        feeSum = int(sum*fee/100)
        fileRead["users"][str(message.from_user.id)]["balance"] += sum - feeSum
        fileRead["users"][str(message.from_user.id)]["bank"] -= sum
        fileRead["users"][str(message.from_user.id)]["paidKkh"] += feeSum
        bot.send_message(message.chat.id, f"Выведено {rec_file.ob_chisla(sum)} КШ из банка\nКомиссия {rec_file.ob_chisla(feeSum)} КШ ({fee}%)\nВ банке: {rec_file.ob_chisla(rec_file.getBank(message.from_user.id, fileRead))} КШ\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(message.from_user.id, fileRead))} КШ")
    def checkReg(self):
        if (str(self.message.from_user.id) not in fileRead["users"].keys()): return bot.send_message(self.message.chat.id, message_bot_not_started(), parse_mode="MARKDOWN")
def bitcoinBet(id, bet, betAmount, chatid):
    try: startPrice = float(requests.get("https://blockchain.info/ticker").json()["RUB"]["sell"])
    except: return bot.send_message(chatid, "Возникла ошибка! Сообщите об этом разработчику!")
    time.sleep(60)
    endPrice = float(requests.get("https://blockchain.info/ticker").json()["RUB"]["sell"])
    if (bet == "вверх") and (startPrice < endPrice):
        rec_file.append_balance(id, betAmount * 2, fileRead)
        fileRead["users"][str(id)]["wonBtcBets"] += betAmount * 2;
        return bot.send_message(chatid, f"Вы выиграли!\nКурс BTC изменился на {round(endPrice - startPrice, 2)} RUB.\nВаш выигрыш: {rec_file.ob_chisla(betAmount)} КШ\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
    elif (bet == "вниз") and (startPrice > endPrice):
        rec_file.append_balance(id, betAmount * 2, fileRead)
        fileRead["users"][str(id)]["wonBtcBets"] += betAmount * 2;
        return bot.send_message(chatid, f"Вы выиграли!\nКурс BTC изменился на {round(endPrice - startPrice, 2)} RUB.\nВаш выигрыш: {rec_file.ob_chisla(betAmount)} КШ\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
    else:
        fileRead["users"][str(id)]["lostBtcBets"] += betAmount * 2;
        return bot.send_message(chatid, f"Вы проиграли!\nКурс BTC изменился на {round(endPrice - startPrice, 2)} RUB.\nПроиграно {rec_file.ob_chisla(betAmount)} КШ\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, fileRead))} КШ")
def rouletteButtonsBet(betAmount, bet, userId, chatId):
    if (type(betAmount) != str):
        if userId != betAmount.from_user.id: return bot.register_next_step_handler(betAmount, rouletteButtonsBet, bet, userId, chatId)
        betAmount = betAmount.text
    #["1:3", "1:3(2)", "1:3(3)", "1st12", "2nd12", "3rd12", "1to18", "19to36", "even", "odd", "red", "black"]
    try: betAmount = int(rec_file.ob_k_chisla(betAmount))
    except:
        if (betAmount == "#r"): betAmount = random.randint(1, rec_file.get_balance(userId, fileRead))
        elif (betAmount == "все") or (betAmount == "всё"): betAmount = rec_file.get_balance(userId, fileRead)
        elif (betAmount[-1] == "%"):
            betAmount = betAmount[:-1]
            try: betAmount = int(betAmount)
            except: return bot.send_message(chatId, "Неверное использование процентной ставки. Процентная ставка должна быть не менее 1 и не более 100% от вашего баланса и иметь численное значение!")
            if (0 < betAmount <= 100): betAmount = rec_file.get_balance(userId, fileRead) * betAmount // 100
            else: return bot.send_message(chatId, "Неверное использование процентной ставки. Процентная ставка должна быть не менее 1 и не более 100% от вашего баланса!")
        else: return bot.send_message(chatId, "Ставка должна иметь численный вид")
    if (betAmount > rec_file.get_balance(userId, fileRead)): return bot.send_message(chatId, "Ставка не может быть больше вашего баланса")
    if roulette != []: 
        bot.send_message(chatId, "Ставка сделана. Игра уже в процессе!")
        return roulette.append({"id": userId, "bet": bet, "amount": betAmount})
    roulette.append({"id": userId, "bet": bet, "amount": betAmount})
    bot.send_message(chatId, "Ставка сделана. Игра начнется через 30 секунд!")
    Thread(target=rouletteStart, args=(chatId, "a")).start()

def rouletteStart(chatId, text):
    global roulette
    time.sleep(30)


    number = random.randint(0, 36)
    red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    black = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,33,35]
    even = [i for i in range(2,37,2)]
    odd = [i for i in range(1,36,2)]
    firstColumn = [i for i in range(1,13)]
    secondColumn = [i for i in range(13,25)]
    thirdColumn = [i for i in range(25,37)]
    firstLine = [i for i in range(1, 35, 3)]
    secondLine = [i for i in range(2, 36, 3)]
    thirdLine = [i for i in range(3, 37, 3)]
    oneToEighteen = [i for i in range(1,19)]
    nineteenToThirtySix = [i for i in range (19, 37)]

    msg = f"Выпало число {number}\nСтавки:"
    results = {}
    for i in roulette:
        match i["bet"]:
            case "red":
                if number in red:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "black":
                if number in black:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "even":
                if number in even:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "odd":
                if number in odd:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "1:3":
                if number in firstLine:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "1:3(2)":
                if number in secondLine:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "1:3(3)":
                if number in thirdLine:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "1st12":
                if number in firstColumn:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "2nd12":
                if number in secondColumn:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "3rd12":
                if number in thirdColumn:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "1to18":
                if number in oneToEighteen:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case "19to36":
                if number in nineteenToThirtySix:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
            case _:
                try: bet = int(bet)
                except:
                    results[i["id"]] = {"error": "Произошла ошибка!"}
                    continue
                if (number == bet):
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] += i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": i["amount"]}
                else:
                    if i["id"] in results:
                        results[i["id"]]["bet"].append(i["bet"])
                        results[i["id"]]["sum"] -= i["amount"]
                    else:
                        results[i["id"]] = {"bet": [i["bet"]], "sum": -i["amount"]}
    
    for i in results.keys():
        rec_file.append_balance(i, results[i]["sum"], fileRead)
        fileRead["users"][str(i)]["wonRoulette"] += results[i]["sum"]
        msg += f"\n\n<a href = 'tg://user?id={i}'>{getName(i)}</a>:\nCтавки: {results[i]['bet']}\nОбщее изменение баланса: "
        if results[i]["sum"] > 0: msg += "+"
        elif results[i]["sum"] < 0: msg += "-"
        msg += f"{rec_file.ob_chisla(abs(results[i]['sum']))} КШ\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(i, fileRead))} КШ"
    
    bot.send_photo(chatId, "AgACAgIAAxkBAAEERyxh0ZLbF82ZvyLwUJfjbOvxh2Z3PwAC2rcxGyzskEoC-uMjPRKv6gEAAwIAA3kAAyME")
    # bot.send_photo(chatId, "AgACAgIAAxkBAAJS5mMcm3T2QwGsS2gw_Iq0k4jGAVf-AAI8tTEb4KQ5S_X7F-E3605YAQADAgADbQADKQQ")
    bot.send_message(chatId, msg, parse_mode="HTML")
    roulette = []
    results = {}

bot.infinity_polling(timeout=123, long_polling_timeout=123)
# bot.polling(True, interval=0.5, timeout=123, long_polling_timeout=123)
#962 -> 630