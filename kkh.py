# -*- coding: utf-8 -*-
import telebot
from telebot import types
import time
import rec_file
from threading import Thread
import random
import yadisk
import shutil
import datetime
import schedule
import json

with open("usrs.json", encoding="utf-8") as file_readed:
    file_readed = json.load(file_readed)
with open("config.json", encoding="utf-8") as config:
    config = json.load(config)

bot = telebot.TeleBot(config["telegramToken"])
y = yadisk.YaDisk(token=config["yandexDiskToken"])

@bot.message_handler(commands=["start"])
def start_command(message):
    if (bot.get_chat(message.chat.id).type != "private"):
        if str(message.chat.id) not in file_readed["groups"].keys():
             firstName = bot.get_chat(message.chat.id).first_name;
             lastName = bot.get_chat(message.chat.id).last_name
             rec_file.append_id(message.chat.id, bot.get_chat(message.chat.id).type, firstName, lastName, file_readed);
        bot.send_message(message.chat.id, "Эту команду можно использовать только в личных сообщениях с ботом!");
    else:
        if str(message.from_user.id) not in file_readed["users"].keys():
            rec_file.append_id(message.from_user.id, bot.get_chat(message.chat.id).type, None, None, file_readed);
            bot.send_message(message.chat.id, config["messages"]["startCommand"], disable_web_page_preview=True, reply_markup=main_menu_buttons(), parse_mode="MARKDOWN");
        else:
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, config["messages"]["startCommand"]);

@bot.message_handler(content_types=["text"])
def send_text(message):
    if (message.text != None): message_text = message.text.lower().split(" ")
    if message_text[0] != "кмд" and message_text[0] != "_":
        if check_messages(message, message_text) != False:
            if str(message.from_user.id) in file_readed["users"].keys():
                rec_file.append_last_command(message.from_user.id, message.text, file_readed);
    elif message_text[0] == "_":
        repeat_command(message)
    else:
        rec_file.append_last_command(message.from_user.id, message.text, file_readed)
        if rec_file.get_admin(message.from_user.id, file_readed) == 1:
            if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: кмд <id> <команда>")
            try:
                if message_text[1] == "_":
                    userid = message.reply_to_message
                    if userid != None: userid = userid.from_user.id
                    else: userid = 0
                else: userid = int(message_text[1])
            except ValueError: return bot.send_message(message.chat.id, "Неверный id. ID должен состоять только из цифр!")
            if (userid == 0): return bot.send_message(message.chat.id, "Используйте `_` при ответе на сообщение")
            if (userid not in rec_file.get_ids(file_readed)): return bot.send_message(message.chat.id, "ID не найден")
            message_text = message_text[2::]
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
    global file_readed
    while True:
        rec_file.time_nachislenie(file_readed)
        time.sleep(1)
def backup_whiletrue():
    today = datetime.datetime.today()
    name = f"backup-{today.strftime('%Y-%m-%d_%H.%M.%S')}.txt"
    shutil.copyfile("usrs.json", f"backups/{name}")
    y.upload(f"backups/{name}", (f"/kkh_backups/{name}"))
    time.sleep(7200)
def updateUsersNameInFile():
    dict = rec_file.updateUserName(file_readed)
    for i in dict:
        try:
            i[1] = bot.get_chat(int(i[0])).first_name
            i[2] = bot.get_chat(int(i[0])).last_name
        except: pass
    rec_file.updateUserNameWrite(dict, file_readed)
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)
Thread(target=whiletrue).start()
Thread(target=backup_whiletrue).start()
schedule.every().day.at("00:00").do(rec_file.balance_boost_nachislenie, file_readed)
schedule.every().day.at("04:20").do(updateUsersNameInFile)
Thread(target=schedule_checker).start()

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
    button_sec = types.KeyboardButton(f"+сек ({rec_file.ob_chisla(rec_file.cal_boost_sec(id, file_readed))} КШ)")
    button_click = types.KeyboardButton(f"+клик ({rec_file.ob_chisla(rec_file.cal_boost_click(id, file_readed))} КШ)")
    if rec_file.get_skidka(id, file_readed) >= 25:
        button_skidka = types.KeyboardButton(message_max_skidka())
    else:
        button_skidka = types.KeyboardButton(f"+1% скидки ({rec_file.ob_chisla(rec_file.cal_boost_skidka(id, file_readed))} КШ)")
    if rec_file.get_boost_balance(id, file_readed) >= 15:
        button_boost_balance = types.KeyboardButton(message_max_boost_balance())
    else:
        button_boost_balance = types.KeyboardButton(f"+1% баланса/день ({rec_file.ob_chisla(rec_file.cal_boost_balance(id, file_readed))} КШ)")
    button_back = types.KeyboardButton("Назад")
    upgades_board.add(button_sec, button_click)
    upgades_board.add(button_skidka, button_boost_balance)
    upgades_board.add(button_back)
    return upgades_board
#сообщения юзеру
def message_bought_upgrade(user_message, a):
    return f"Успешно куплено апгрейдов: {a}\nid: `{user_message.from_user.id}`\nАпгрейды: {file_readed['users'][str(user_message.from_user.id)]['sec']}/сек; {file_readed['users'][str(user_message.from_user.id)]['click']}/клик; {rec_file.get_skidka(user_message.from_user.id, file_readed)}% скидки; {rec_file.get_boost_balance(user_message.from_user.id, file_readed)}% баланса/день\nБаланс: {rec_file.ob_chisla(file_readed['users'][str(user_message.from_user.id)]['balance'])} КШ"
def message_not_enough_money_click(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(str(rec_file.cal_boost_click(user_message.from_user.id, file_readed) - rec_file.get_balance(user_message.from_user.id, file_readed)))} КШ"
def message_not_enough_money_sec(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(rec_file.cal_boost_sec(user_message.from_user.id, file_readed) - rec_file.get_balance(user_message.from_user.id, file_readed))} КШ"
def message_not_enough_money_boost_balance(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(rec_file.cal_boost_balance(user_message.from_user.id, file_readed) - rec_file.get_balance(user_message.from_user.id, file_readed))} КШ"
def sendmessage_check_active_keyboard(chatid, userid, userOrGroup, send_message):
    if (userOrGroup == "private"):
        if rec_file.get_keyboard(userid, file_readed):
            if rec_file.get_active_passive_keyboard(userid, file_readed) == 1: bot.send_message(chatid, send_message, reply_markup=upgades_buttons(userid), disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется с обновленными ценами в клавиатуре
            else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется без клавиатуры
        else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")
    else:
        if (file_readed["groups"][str(chatid)]["keyboard"]):
            if (file_readed["groups"][str(chatid)]["activeKeyboard"]): bot.send_message(chatid, send_message, reply_markup=upgades_buttons(userid), disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется с обновленными ценами в клавиатуре
            else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")#отправляется без клавиатуры
        else: bot.send_message(chatid, send_message, disable_web_page_preview = True, parse_mode="MARKDOWN")
def message_max_skidka():
    return "Достигнут максимум апгрейдов скидки"
def message_max_boost_balance():
    return "Достигнут максимум апгрейдов баланса/день"
def message_not_enough_money_skidka(user_message):
    return f"Недостаточно средств. Для покупки ещё необходимо {rec_file.ob_chisla(str(rec_file.cal_boost_skidka(user_message.from_user.id, file_readed) - rec_file.get_balance(user_message.from_user.id, file_readed)))} КШ"
#другое
def manual_backup():
    today = datetime.datetime.today()
    name = "backup-" + today.strftime("%Y-%m-%d_%H.%M.%S") + ".txt"
    shutil.copyfile("usrs.json", f"backups/{name}")
    y.upload(f"backups/{name}", (f"/kkh_backups/{name}"))
    return "Бэкап успешно выполнен и загружен на сервер!"

def check_messages(message, message_text):
    #if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!");
    if message.text.lower() == "клик" or message.text == "🔮":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.click(message, message_text)
    elif message_text[0] == "+сек":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.buy_sec(message, message_text)
    elif message_text[0] == "+клик":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.buy_click(message, message_text)
    elif message_text[0] == "+скидка":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.buy_skidka(message, message_text)
    elif message_text[0] == "+баланс" or message_text[0] == "+баланс/день" or message_text[0] == "+бб":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.buy_procent_balance(message, message_text)
    elif message_text[0] == "+буст":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        if len(message_text) >= 2:
            if message_text[1] == "баланса" or message_text[1] == "баланс":
                kmd.buy_procent_balance(message, message_text)
    elif message_text[0] == "+1%":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        if len(message_text) >= 2:
            if message_text[1] == "скидки":
                kmd.buy_skidka_2(message, message_text)
            elif message_text[1] == "баланса/день":
                kmd.buy_procent_balance_2(message, message_text)
    elif message_text[0] == "цена":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.price(message, message_text)
    elif message_text[0] == "добавить":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.add_money(message, message_text)
    elif message_text[0] == "баланс" or message_text[0] == "б":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.balance(message, message_text)
    elif message.text.lower() == "апгрейды":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.upgrades(message, message_text)
    elif message.text.lower() == "назад":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.back(message, message_text)
    elif message_text[0] == "монета" or message_text[0] == "монетка":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.moneta(message, message_text)
    elif message_text[0] == "сброс":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.reset(message, message_text)
    elif message_text[0] == "перевод":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.pay(message, message_text)
    elif message_text[0] == "админ":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.admin(message, message_text)
    elif message.text.lower() == "бонус":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.bonus(message, message_text)
    elif (message_text[0] == "промо") and (len(message_text) > 1) and(message_text[1] == "добавить"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.addPromo(message, message_text);
    elif (message_text[0] == "промо") and (len(message_text) > 1) and (message_text[1] == "удалить"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.delPromo(message, message_text);
    elif (message_text[0] == "промо") and (len(message_text) > 1) and (message_text[1] == "инфо"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.promoInf(message, message_text);
    elif (message_text[0] == "промо") and (len(message_text) > 1) and(message_text[1] == "лист"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.promoList(message, message_text);
    elif message_text[0] == "промо":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.activate_promo(message, message_text)
    elif message_text[0] == "клавиатура":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.keyboard(message, message_text)
    elif message_text[0] == "рассылка":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.rassilka(message, message_text)
    elif message_text[0] == "бэкап":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.backup(message, message_text)
    elif message.text.lower() == "главное меню":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.main_menu(message, message_text)
    elif message.text.lower() == "начать":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        start_command(message)
    elif message.text.lower() == "команды":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.commandsList(message, message_text)
    elif message_text[0] == "инфо":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.full_inf_user(message, message_text);
    elif message_text[0] == "дюзер":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.del_user(message, message_text);
    elif message_text[0] == "юзерслист":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.userlist(message, message_text);
    elif message_text[0] == "бдзапись" or message_text[0] == "записьбд" or message_text[0] == "запись":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.manual_write_file(message, message_text);
    elif message.text.lower() == "бонус2":
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.bonus2(message, message_text)
    elif (message_text[0] == "команда"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.helpCommand(message, message_text);
    elif (message_text[0] == "послать") or (message_text[0] == "послатьанон"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.sendUser(message, message_text);
    elif (message_text[0] == "топ"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.userTop(message, message_text)
    elif (message_text[0] == "chatinfo"):
        if (str(message.from_user.id) not in file_readed["users"].keys()): return bot.send_message(message.chat.id, "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!")
        kmd.chatInfo(message, message_text)
    else:
        return False
def repeat_command(message):
    command = rec_file.get_last_command(message.from_user.id, file_readed)
    comm = None
    try: comm = int(command)
    except: pass
    if comm == "": bot.send_message(message.chat.id, "Последняя команда не обнаружена")
    else:
        message.text = command
        send_text(message)
#kmd
class kmd:
    def click(message, message_text):
        rec_file.click_nachislenie(message.from_user.id, file_readed)
        bot.send_message(message.chat.id, f"Коллекция кристальных шаров пополнена!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(message.from_user.id, file_readed))} КШ")
    def buy_sec(message, message_text):
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_sec(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, file_readed), file_readed)
            rec_file.append_sec(message.from_user.id, 1, file_readed)
            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_sec(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_sec(message.from_user.id, file_readed):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
                        rec_file.append_sec(message.from_user.id, 1, file_readed)
                        a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                if message_text[1] == "все" or message_text[1] == "всё":
                    if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_sec(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
                    while rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_sec(message.from_user.id, file_readed):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
                        rec_file.append_sec(message.from_user.id, 1, file_readed)
                        a += 1
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                elif (len(message_text) >= 3):
                    try:
                        if message_text[1][0] == "(" and message_text[2][-1] == ")":
                            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_sec(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_sec(message))
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_sec(message.from_user.id, file_readed), file_readed)
                            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
                            rec_file.append_sec(message.from_user.id, 1, file_readed)
                            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))  
                        else:
                            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, "Неверный параметр +сек [кол-во апгрейдов]")
                    except: pass
    def buy_click(message, message_text):
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_click(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_click(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, file_readed), file_readed)
            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, file_readed)
            rec_file.append_click(message.from_user.id, 1, file_readed)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_click(message.from_user.id, file_readed): return  bot.send_message(message.chat.id, message_not_enough_money_click(message))
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_click(message.from_user.id, file_readed):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, file_readed)
                        rec_file.append_click(message.from_user.id, 1, file_readed)
                        a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                if message_text[1] == "все" or message_text[1] == "всё":
                    if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_click(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_click(message))
                    while rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_click(message.from_user.id, file_readed):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, file_readed)
                        rec_file.append_click(message.from_user.id, 1, file_readed)
                        a += 1
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                elif (len(message_text) >= 3):
                    try:
                        if message_text[1][0] == "(" and message_text[2][-1] == ")":
                            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_click(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_click(message))
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_click(message.from_user.id, file_readed), file_readed)
                            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_click(message.from_user.id, file_readed)
                            rec_file.append_click(message.from_user.id, 1, file_readed)
                            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                        else:
                            bot.send_message(message.chat.id, "Неверный параметр +клик [кол-во апгрейдов]")
                    except:
                        pass
    def buy_skidka(message, message_text):
        if rec_file.get_skidka(message.from_user.id, file_readed) >= 25: return bot.send_message(message.chat.id, message_max_skidka())
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_skidka(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_skidka(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, file_readed), file_readed)
            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, file_readed)
            rec_file.append_skidka(message.from_user.id, 1, file_readed)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_skidka(message.from_user.id, file_readed) < 25:
                        if rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_skidka(message.from_user.id, file_readed):
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, file_readed), file_readed)
                            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, file_readed)
                            rec_file.append_skidka(message.from_user.id, 1, file_readed)
                            a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                if message_text[1] == "все" or message_text[1] == "всё":
                    if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_skidka(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_skidka(message))
                    while rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_skidka(message.from_user.id, file_readed) and rec_file.get_skidka(message.from_user.id, file_readed) < 25:
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, file_readed)
                        rec_file.append_skidka(message.from_user.id, 1, file_readed)
                        a += 1
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                else: bot.send_message(message.chat.id, "Неверный параметр +скидка [кол-во апгрейдов]")
    def buy_skidka_2(message, message_text):
        if rec_file.get_skidka(message.from_user.id, file_readed) >= 25: return bot.send_message(message.chat.id, message_max_skidka())
        if len(message_text) >= 4:
            if message_text[1] == 'скидки':
                try:
                    if message_text[2][0] == "(" and message_text[3][-1] == ")":
                        if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_skidka(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_skidka(message))
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_skidka(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_skidka(message.from_user.id, file_readed)
                        rec_file.append_skidka(message.from_user.id, 1, file_readed)
                        sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                except: pass
    def price(message, message_text):
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: цена <сек/клик/скидка>")
        if message_text[1] == "сек" or message_text[1] == "+сек": bot.send_message(message.chat.id, f"Цена за {file_readed['users'][str(message.from_user.id)]['sec'] + 1} апгрейд +сек со скидкой {rec_file.get_skidka(message.from_user.id, file_readed)}%: {rec_file.ob_chisla(rec_file.cal_boost_sec(message.from_user.id, file_readed))} КШ")
        elif message_text[1] == "клик" or message_text[1] == "+клик": bot.send_message(message.chat.id, f"Цена за {file_readed['users'][str(message.from_user.id)]['click'] + 1} апгрейд +клик со скидкой {rec_file.get_skidka(message.from_user.id, file_readed)}%: {rec_file.ob_chisla(rec_file.cal_boost_click(message.from_user.id, file_readed))} КШ")
        elif message_text[1] == "скидка" or message_text[1] == "+скидка" or message_text[1] == "скидки" or message_text[1] == "+скидки":
            if rec_file.get_skidka(message.from_user.id, file_readed) < 25: bot.send_message(message.chat.id, f"Цена за {rec_file.get_skidka(message.from_user.id, file_readed) + 1} апгрейд со скидкой {rec_file.get_skidka(message.from_user.id, file_readed)}%: {rec_file.ob_chisla(rec_file.cal_boost_skidka(message.from_user.id, file_readed))} КШ")
            else: bot.send_message(message.chat.id, message_max_skidka())
        elif message_text[1] == "бб" or message_text[1] == "+бб" or message_text[1] == "баланс" or message_text[1] == "баланса" or message_text[1] == "+баланса" or message_text[1] == "+баланс" or message_text[1] == "баланс/день" or message_text[1] == "+баланс/день":
            if rec_file.get_boost_balance(message.from_user.id, file_readed) < 15: bot.send_message(message.chat.id, f"Цена за {rec_file.get_boost_balance(message.from_user.id, file_readed) + 1} апгрейд со скидкой {rec_file.get_skidka(message.from_user.id, file_readed)}%: {rec_file.ob_chisla(rec_file.cal_boost_balance(message.from_user.id, file_readed))} КШ")
            else: bot.send_message(message.chat.id, message_max_boost_balance())
        else: bot.send_message(message.chat.id, "Неизвестный тип")
    def add_money(message, message_text):
        if rec_file.get_admin(message.from_user.id, file_readed) == True:
            if len(message_text) <= 2: return bot.send_message(message.chat.id, "Использование: добавить <id/себе> <сумма>")
            try:
                sum = rec_file.ob_k_chisla(message_text[2])
                if message_text[1] == "_":
                    userid = message.reply_to_message
                    if userid != None: userid = userid.from_user.id
                    else: userid = 0
                else: userid = int(message_text[1])
                if userid not in rec_file.get_ids(file_readed): return bot.send_message(message.chat.id, "Юзер не найден!")
                rec_file.append_balance(userid, int(rec_file.ob_k_chisla(sum)), file_readed)
                file_readed["users"][str(userid)]["othersProceeds"] += int(rec_file.ob_k_chisla(sum))
                bot.send_message(message.chat.id, f"Пользователю `{userid}` начислено {rec_file.ob_chisla(sum)} КШ")
                bot.send_message(userid, f"Вам начислено {rec_file.ob_chisla(sum)} КШ администратором")
            except ValueError:
                try:
                    if message_text[1] == "себе":
                        rec_file.append_balance(message.from_user.id, int(rec_file.ob_k_chisla(sum)), file_readed)
                        file_readed["users"][str(message.from_user.id)]["othersProceeds"] += int(rec_file.ob_k_chisla(sum))
                        bot.send_message(message.chat.id, f"Вам начислено {rec_file.ob_chisla(sum)} КШ")
                    else: bot.send_message(message.chat.id, "Юзер не найден!")
                except ValueError:
                    bot.send_message(message.chat.id, "Использование: добавить <id/себе> <сумма>")
        else:
            pass
    def balance(message, message_text):
        if len(message_text) == 1: bot.send_message(message.chat.id, f"id: `{message.from_user.id}`\nАпгрейды: {file_readed['users'][str(message.from_user.id)]['sec']}/сек; {file_readed['users'][str(message.from_user.id)]['click']}/клик; {rec_file.get_skidka(message.from_user.id, file_readed)}% скидки; {rec_file.get_boost_balance(message.from_user.id, file_readed)}% баланса/день\nБаланс: {rec_file.ob_chisla(file_readed['users'][str(message.from_user.id)]['balance'])} КШ")
        elif len(message_text) >= 2:
            try:
                if message_text[1] == "_":
                    userid = message.reply_to_message
                    if userid != None: userid = userid.from_user.id
                    else: userid = 0
                else: userid = int(message_text[1])
                if userid not in rec_file.get_ids(file_readed): return bot.send_message(message.chat.id, "id не найден")
                bot.send_message(message.chat.id, f"id: `{userid}`\nАпгрейды: {file_readed['users'][str(userid)]['sec']}/сек; {file_readed['users'][str(userid)]['click']}/клик; {rec_file.get_skidka(userid, file_readed)}% скидки; {rec_file.get_boost_balance(userid, file_readed)}% баланса/день\nБаланс: {rec_file.ob_chisla(file_readed['users'][str(userid)]['balance'])} КШ")
            except ValueError: bot.send_message(message.chat.id, "Использование: Баланс/б [id]")
    def upgrades(message, message_text):
        rec_file.set_active_passive_keyboard(message.chat.id, True, bot.get_chat(message.chat.id).type, file_readed)
        if (bot.get_chat(message.chat.id).type == "private"):
            if rec_file.get_keyboard(message.from_user.id, file_readed) == True:
                bot.send_message(message.chat.id, "Открыто меню апгрейдов", reply_markup=upgades_buttons(message.from_user.id))
            elif rec_file.get_keyboard(message.from_user.id, file_readed) == False:
                bot.send_message(message.chat.id, "Открыто меню апгрейдов")
        else:
            if (file_readed["groups"][str(message.chat.id)]["keyboard"]):
                bot.send_message(message.chat.id, "Открыто меню апгрейдов", reply_markup=upgades_buttons(message.from_user.id))
            if (file_readed["groups"][str(message.chat.id)]["keyboard"] == False):
                bot.send_message(message.chat.id, "Открыто меню апгрейдов")
    def back(message, message_text):
        if (bot.get_chat(message.chat.id).type == "private"):
            if rec_file.get_keyboard(message.from_user.id, file_readed): bot.send_message(message.chat.id, "Вы вышли из меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Вы вышли из меню")
        else:
            if (file_readed["groups"][str(message.chat.id)]["keyboard"]): bot.send_message(message.chat.id, "Вы вышли из меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Вы вышли из меню")
        rec_file.set_active_passive_keyboard(message.chat.id, False, bot.get_chat(message.chat.id).type, file_readed)
    def moneta(message, message_text):
        if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: монета <ставка/всё> <орел/решка>")
        if message_text[1] == "все": bot.send_message(message.chat.id, rec_file.moneta_stavka(message.from_user.id, str(rec_file.get_balance(message.from_user.id, file_readed)), message_text[2], file_readed))
        else:
            sum = rec_file.ob_k_chisla(message_text[1])
            bot.send_message(message.chat.id, rec_file.moneta_stavka(message.from_user.id, sum, message_text[2], file_readed))
    def reset(message, message_text):
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: сброс <подтвердить/справка>")
        if message_text[1] == "подтвердить":
            rec_file.clear_id(message.from_user.id, file_readed)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, "Ваш прогресс сброшен!")
        elif message_text[1] == "справка": bot.send_message(message.chat.id, "А нет её ещё, не запилили!")
        else:
            if rec_file.get_admin(message.from_user.id, file_readed):
                try:
                    if message_text[1] == "_":
                        a = message.reply_to_message
                        if a != None: a = a.from_user.id
                        else: a = 0
                    else: a = int(message_text[1])
                    if a not in rec_file.get_ids(file_readed): return bot.send_message(message.chat.id, "Такой id не найден!")
                    rec_file.clear_id(a, file_readed)
                    bot.send_message(message.chat.id, f"Прогресс пользователя `{a}` успешно сброшен!")
                    sendmessage_check_active_keyboard(a, a, bot.get_chat(message.chat.id).type, "Ваш прогресс сброшен администратором!")
                except ValueError: return bot.send_message(message.chat.id, "Использование: сброс <подтвердить/справка/id юзера>")
            if rec_file.get_admin(message.from_user.id, file_readed) == 0: bot.send_message(message.chat.id, "Использование: сброс <подтвердить/справка>")
    def pay(message, message_text):
        if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: перевод <сумма> <id получателя> [комментарий]")
        if (message_text[1] == "#r"): sum = random.randint(1, rec_file.get_balance(message.from_user.id, file_readed))
        else:
            if message_text[1][-1] == "%":
                if 1 <= int(message_text[1][:-1:]) <= 100:
                    try: sum = rec_file.get_balance(message.from_user.id, file_readed)*int(message_text[1][:-1:])//100
                    except: return bot.send_message(message.chat.id, "Неверное использование процентного перевода. Использование: перевод <1%-100%> <id получателя> [комментарий]")
                else: return bot.send_message(message.chat.id, "Неверное использование процентного перевода. Использование: перевод <1%-100%> <id получателя> [комментарий]")
            else:
                try: sum = int(rec_file.ob_k_chisla(message_text[1]))
                except ValueError:
                    if message_text[1] == "все" or message_text[1] == "всё": sum = int(round(rec_file.get_balance(message.from_user.id, file_readed)))
                    else: return bot.send_message(message.chat.id, "Использование: перевод <сумма> <id получателя> *[комментарий]*")
        try:
            if message_text[2] == "#r":
                ids = rec_file.get_ids(file_readed)
                random.shuffle(ids)
                poly4atel = ids[0]
            elif message_text[2] == "_":
                poly4atel = message.reply_to_message
                if poly4atel != None: poly4atel = poly4atel.from_user.id
                else: poly4atel = 0
            else: poly4atel = int(message_text[2])
            if poly4atel not in rec_file.get_ids(file_readed): return bot.send_message(message.chat.id, "Пользователь с таким id не найден!")
            if rec_file.get_balance(message.from_user.id, file_readed) < sum: return bot.send_message(message.chat.id, "Недостаточно средств")
            if sum < 100: return bot.send_message(message.chat.id, "Переводы меньше 100 КШ запрещены")
            rec_file.append_balance(message.from_user.id, -sum, file_readed)
            file_readed["users"][str(message.from_user.id)]["paidKkh"] += sum
            rec_file.append_balance(poly4atel, sum, file_readed)
            file_readed["users"][str(poly4atel)]["receivedKkh"] += sum
            send_message = f"Перевод {rec_file.ob_chisla(sum)} КШ пользователю `{poly4atel}` выполнен успешно!"
            if len(message_text) >= 4:
                comment = message.text.split(" ")
                send_message = f"{send_message}\nКомментарий к переводу: "
                for i in range(3, len(message_text)):
                    send_message += f"{comment[i]} "
            bot.send_message(message.chat.id, send_message)
            send_message = f"Получен перевод {rec_file.ob_chisla(sum)} КШ от пользователя `{message.from_user.id}`"
            if len(message_text) >= 4:
                send_message = f"{send_message}\nСообщение: "
                for i in range(3, len(message_text)):
                    send_message += f"{comment[i]} "
            bot.send_message(poly4atel, send_message) 
        except ValueError: bot.send_message(message.chat.id, "Неверное id получателя! id должно содержать только цифры")
    def admin(message, message_text):
        if message.from_user.id == 357694314:
            if len(message_text) == 1: bot.send_message(message.chat.id, "Использование: админ [добавить/удалить] <id>")
            elif len(message_text) >= 2:
                if message_text[1] == "добавить" or message_text[1] == "назначить":
                    if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: админ добавить <id>")
                    try: user = int(message_text[2])
                    except:
                        if message_text[2] == "себя" or message_text[2] == "себе" or message_text[2] == "я": user = message.from_user.id
                        elif (message_text[2] == "_") and (message.reply_to_message != None): user = message.reply_to_message.from_user.id;
                        else: return bot.send_message(message.chat.id, "Использование: админ добавить <id>")
                    if user not in rec_file.get_ids(file_readed): return bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` не найден")
                    if rec_file.get_admin(user, file_readed): return bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` уже имеет права администратора")
                    rec_file.set_admin(user, file_readed)
                    bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` назначен администратором!")
                    bot.send_message(user, "Вас назначили администратором, ведите себя хорошо!")
                elif message_text[1] == "удалить" or message_text[1] == "снять":
                    if len(message_text) < 3: return bot.send_message(message.chat.id, "Использование: админ удалить <id>")
                    try: user = int(message_text[2])
                    except:
                        if message_text[2] == "себя" or message_text[2] == "себе" or message_text[2] == "я": user = message.from_user.id
                        elif (message_text[2] == "_") and (message.reply_to_message != None): user = message.reply_to_message.from_user.id;
                        else: return bot.send_message(message.chat.id, "Использование: админ удалить <id>")
                    if user not in rec_file.get_ids(file_readed): return bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` не найден")
                    if rec_file.get_admin(user, file_readed) == False: return bot.send_message(message.chat.id, f"Пользователь `{message_text[2]}` не имеет прав администратора!")
                    rec_file.unset_admin(user, file_readed)
                    bot.send_message(message.chat.id, f"С пользователя `{message_text[2]}` сняты права администратора!")
                    bot.send_message(user, "С вас сняты права администатора!")  
                else: bot.send_message(message.chat.id, "Использование: админ [добавить/удалить] <id>")
        else:
            if rec_file.get_admin(message.from_user.id, file_readed) == True: bot.send_message(message.chat.id, "Ты админ")
            else: bot.send_message(message.chat.id, "Ты не админ")
    def bonus(message, message_text):
        if rec_file.get_time_now() - rec_file.get_time_give_bonus(message.from_user.id, file_readed) < 86400: return bot.send_message(message.chat.id, f"Ежедневный бонус уже был получен сегодня\nДо следующего бонуса: {rec_file.ob_vremeni_bonusa(rec_file.get_time_give_bonus(message.from_user.id, file_readed) + 86400 - rec_file.get_time_now())}")
        rec_file.set_time_give_bonus(message.from_user.id, message.date, file_readed)
        bot.send_message(message.chat.id, rec_file.give_bonus(message.from_user.id, file_readed))
    def bonus2(message, message_text):
        if (rec_file.get_time_now() - rec_file.get_time_give_bonus2(message.from_user.id, file_readed)) < 28800: return bot.send_message(message.chat.id, f"Бонус2 можно получать каждые 8 часов\nДо следующего бонуса2: {rec_file.ob_vremeni_bonusa(rec_file.get_time_give_bonus2(message.from_user.id, file_readed) + 28800 - rec_file.get_time_now())}")
        rec_file.set_time_give_bonus2(message.from_user.id, message.date, file_readed)
        bot.send_message(message.chat.id, rec_file.give_bonus2(message.from_user.id, file_readed))
    def activate_promo(message, message_text):
        global file_readed
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: промо <код>")
        file_readed, inf_message = rec_file.activation_promo(message.from_user.id, message_text[1], file_readed)
        bot.send_message(message.chat.id, inf_message)
    def keyboard(message, message_text):
        if len(message_text) == 2:
            if message_text[1] == "нет" or message_text[1] == "выключить":
                rec_file.keyboard_off(message.chat.id, bot.get_chat(message.chat.id).type, file_readed)
                bot.send_message(message.chat.id, "Клавиатура отключена", reply_markup=types.ReplyKeyboardRemove())
            elif message_text[1] == "да" or message_text[1] == "включить":
                rec_file.keyboard_on(message.chat.id, bot.get_chat(message.chat.id).type, file_readed)
                bot.send_message(message.chat.id, "Клавиатура включена", reply_markup=main_menu_buttons())
        else:
            bot.send_message(message.chat.id, "Использование: Клавиатура <да/нет>")
    def rassilka(message, message_text):
        if len(message_text) >= 3:
            if rec_file.get_admin(message.from_user.id, file_readed) == True:
                if message_text[1] == "создать":
                    message_text = message.text.split(" ")
                    msg = message_text[2::]
                    send_message = ""
                    for i in msg:
                        send_message += i + " "
                    send_message += "\n____\nДля отключения рассылки введите рассылка нет"
                    for i in rec_file.get_ids(file_readed):
                        if rec_file.get_rassilka(i, file_readed) == True:
                            try:
                                bot.send_message(i, send_message, parse_mode="HTML")
                            except: pass
                    bot.send_message(message.chat.id, send_message, parse_mode="HTML")
                else: bot.send_message(message.chat.id, "Использовние: рассылка <создать> <сообщение>")
            else: bot.send_message(message.chat.id, "Использовние: рассылка <да/нет>")
        elif len(message_text) == 2 and (message_text[1] == "да" or message_text[1] == "нет"):
            if message_text[1] == "да":
                rec_file.set_rassilka(message.from_user.id, True, file_readed)
                bot.send_message(message.chat.id, "Рассылка включена.\nДля отключения введите рассылка нет")
            elif message_text[1] == "нет":
                rec_file.set_rassilka(message.from_user.id, False, file_readed)
                bot.send_message(message.chat.id, "Рассылка отключена.\nДля включения введите рассылка да")
            else: bot.send_message(message.chat.id, "Использовние: рассылка <да/нет>")
        else:
            if rec_file.get_admin(message.from_user.id, file_readed) == True: bot.send_message(message.chat.id, "Использовние: рассылка <да/нет> или рассылка <создать> <сообщение>")
            else: bot.send_message(message.chat.id, "Использовние: рассылка <да/нет>")
    def backup(message, message_text):
        if rec_file.get_admin(message.from_user.id, file_readed) == True:
            if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: бэкап <создать>\nСоздаёт бэкап в папку с бекапами и загружает в облако.")
            if message_text[1] == "создать": bot.send_message(message.chat.id, manual_backup())
            else: bot.send_message(message.chat.id, "Использование: бэкап <создать>")
    def buy_procent_balance(message, message_text):
        if rec_file.get_boost_balance(message.from_user.id, file_readed) >= 15: return bot.send_message(message.chat.id, message_max_boost_balance())
        if len(message_text) == 1:
            if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_balance(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, file_readed), file_readed)
            rec_file.append_boost_balance(message.from_user.id, 1, file_readed)
            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
        elif len(message_text) >= 2:
            if rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_balance(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
            a = 0
            try:
                for i in range(0, int(message_text[1])):
                    if rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_balance(message.from_user.id, file_readed):
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
                        rec_file.append_boost_balance(message.from_user.id, 1, file_readed)
                        a += 1
                sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
            except:
                try:
                    if message_text[1][0] == "(" and message_text[2][-1] == ")":
                        if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_balance(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
                        rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, file_readed), file_readed)
                        file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
                        rec_file.append_boost_balance(message.from_user.id, 1, file_readed)
                        sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                    elif message_text[1] == "все" or message_text[1] == "всё":
                        print(rec_file.cal_boost_balance(message.from_user.id, file_readed))
                        if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_balance(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
                        while rec_file.get_balance(message.from_user.id, file_readed) >= rec_file.cal_boost_balance(message.from_user.id, file_readed):
                            rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, file_readed), file_readed)
                            file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
                            rec_file.append_boost_balance(message.from_user.id, 1, file_readed)
                            a += 1
                            sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, a))
                    else:
                        sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, "Неверный параметр +сек [кол-во апгрейдов]")
                except:
                    pass
    def buy_procent_balance_2(message, message_text):
        if rec_file.get_boost_balance(message.from_user.id, file_readed) >= 15: return bot.send_message(message.chat.id, message_max_boost_balance())
        if len(message_text) >= 2:
            if message_text[1] == "баланса/день":
                try:
                    if rec_file.get_balance(message.from_user.id, file_readed) < rec_file.cal_boost_balance(message.from_user.id, file_readed): return bot.send_message(message.chat.id, message_not_enough_money_boost_balance(message))
                    rec_file.append_balance(message.from_user.id, -rec_file.cal_boost_balance(message.from_user.id, file_readed), file_readed)
                    file_readed["users"][str(message.from_user.id)]["spendKkhUpgrades"] += rec_file.cal_boost_balance(message.from_user.id, file_readed)
                    rec_file.append_boost_balance(message.from_user.id, 1, file_readed)
                    sendmessage_check_active_keyboard(message.chat.id, message.from_user.id, bot.get_chat(message.chat.id).type, message_bought_upgrade(message, 1))
                except: pass
    def main_menu(message, message_text):
        if (bot.get_chat(message.chat.id).type == "private"):
            if rec_file.get_keyboard(message.from_user.id, file_readed) == True: bot.send_message(message.chat.id, "Открыто главное меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Открыто главное меню")
        else:
            if (file_readed["groups"][str(message.chat.id)]["keyboard"]): bot.send_message(message.chat.id, "Открыто главное меню", reply_markup=main_menu_buttons())
            else: bot.send_message(message.chat.id, "Открыто главное меню")
        rec_file.set_active_passive_keyboard(message.chat.id, False, bot.get_chat(message.chat.id).type, file_readed)
    def full_inf_user(message, message_text):
        if rec_file.get_admin(message.from_user.id, file_readed) == True:
            if len(message_text) >= 2:
                try:
                    id = int(message_text[1])
                except:
                    if message_text[1] == "_":
                        id = message.reply_to_message
                        if id != None: id = id.from_user.id
                        else: id = 0
                    else: id = 0
                if (id == 0): id = message.from_user.id
                if id != 0:
                    name = file_readed["users"][str(id)]["firstName"]
                    if (file_readed["users"][str(id)]["lastName"] != None):
                        name += file_readed["users"][str(id)]["lastName"]
                    bot.send_message(message.chat.id, f"Имя: {name};\nБаланс: {rec_file.ob_chisla(file_readed['users'][str(id)]['balance'])};\nКлик: {file_readed['users'][str(id)]['click']};\nСек: {file_readed['users'][str(id)]['sec']};\nКлавиатура: {file_readed['users'][str(id)]['keyboard']};\nСкидка: {100 - int(file_readed['users'][str(id)]['sale'])};\nАдмин: {file_readed['users'][str(id)]['isAdmin']};\nМножитель ежедневного бонуса: {file_readed['users'][str(id)]['multiplier']};\nКлавиатура апгрейды: {file_readed['users'][str(id)]['activeKeyboard']};\nРассылка: {file_readed['users'][str(id)]['mails']};\nВремя получения бонуса: {rec_file.ob_vremeni(file_readed['users'][str(id)]['timeLastBonus'])};\nБуст баланса: {file_readed['users'][str(id)]['balanceBoost']};\nПоследняя команда: {file_readed['users'][str(id)]['lastCommand']} в {rec_file.ob_vremeni(file_readed['users'][str(id)]['timeLastCommand'])};\nВремя получения бонуса2: {rec_file.ob_vremeni(file_readed['users'][str(id)]['timeLastSecondBonus'])};\nАктивированные промокоды: {file_readed['users'][str(id)]['activatedPromos']};\nДата регистрации: {rec_file.ob_vremeni(file_readed['users'][str(id)]['registerTime'])}", parse_mode="HTML")
    def del_user(message, message_text):
        if rec_file.get_admin(message.from_user.id, file_readed) == False: return
        if len(message_text) < 2: return bot.send_message(message.chat.id, "Использование: дюзер <id>")
        try: id = int(message_text[1])
        except ValueError:
            if message_text[1] == "_":
                if (message.reply_to_message != None): id = message.reply_to_message.from_user.id;
                else: return bot.send_message(message.chat.id, "ID дожден состоять только из цифр!")
            return bot.send_message(message.chat.id, "ID дожден состоять только из цифр!")
        if id not in rec_file.get_ids(file_readed): return bot.send_message(message.chat.id, "ID не найден")
        rec_file.remove_id(id, file_readed)
        bot.send_message(message.chat.id, "ID удалён из бд")
    def userlist(message, message_text):
        if rec_file.get_admin(message.from_user.id, file_readed) == False: return
        send_message = f"Вот id всех {len(file_readed['users'].keys()) - 1} пользователей:"
        for i in file_readed["users"].keys():
            if (i != "default"):
                name = f"{bot.get_chat(i).first_name}"
                if (bot.get_chat(i).last_name != None):
                    name += f" {bot.get_chat(i).last_name}"
                send_message += f"\n{i} ({name}), "
        send_message = send_message[:-2:]
        bot.send_message(message.chat.id, send_message)
    def manual_write_file(message, message_text):
        rec_file.write(file_readed)
        bot.send_message(message.chat.id, "БД записана")
    def addPromo(message, message_text):
        if (rec_file.get_admin(message.from_user.id, file_readed) == False): return;
        paramsPromos = rec_file.promo_read("default");
        paramsPromos.pop("activationLimit");
        paramsPromos.pop("activatedTimes");
        paramsPromos.pop("validity");
        if (len(message_text) == 2):
            bot.send_message(message.chat.id, f"Использование: промо добавить <название> <params({paramsPromos})> <кол-во активаций> <время действия>");
        elif (len(message_text) >= 3) and (message_text[2] == "помощь"):
            bot.send_message(message.chat.id, f"Использование: промо добавить <название> <params({paramsPromos})> <кол-во активаций> <время действия>");
        elif (len(message_text) >= 6):
            name = message_text[2];
            paramsDictSTR = message_text[3];
            try: paramsDict = json.loads(paramsDictSTR.replace("'",'"'))
            except: return bot.send_message(message.chat.id, "Произошла ошибка, попробуйте ещё раз!")
            activationLimit = int(message_text[4]);
            durationTime = message_text[5];
            bot.send_message(message.chat.id, rec_file.promo_append(name, paramsDict, activationLimit, durationTime, file_readed));
            #except: return bot.send_message(message.chat.id, f"Использование: промо добавить <название> <params({paramsPromos})> <кол-во активаций> <время действия>")
    def commandsList(message, message_text):
        if (rec_file.get_admin(message.from_user.id, file_readed)): bot.send_message(message.chat.id, config["messages"]["commandsList"], parse_mode="HTML");
        else: bot.send_message(message.chat.id, config["messages"]["commandsListUser"], parse_mode="HTML");
    def helpCommand(message, message_text):
        if (len(message_text) < 2): return bot.send_message(message.chat.id, "Использование: команда <команда>");
        if (message_text[1] == "бэкап"):
            bot.send_message(message.chat.id, "Использование: бэкап <создать>\nСоздаёт бэкап в папку с бекапами и загружает в облако.");
        elif (message_text[1] == "бдзапись"):
            bot.send_message(message.chat.id, "Записывает бд в файл");
        elif (message_text[1] == "кмд"):
            bot.send_message(message.chat.id, "Отправляет команду от имени другого юзера\nКмд <id юзера> <команда> *[аргументы команды]*");
        elif (message_text[1] == "команды"):
            bot.send_message(message.chat.id, "Показывает список команд\nКоманды");
        elif (message_text[1] == "команда"):
            bot.send_message(message.chat.id, "Показывает справку по использованию команды\nКоманда <команда>");
        elif (len(message_text) > 2) and (message_text[1] == "главное") and (message_text[2] == "меню"):
            bot.send_message(message.chat.id, "Открывает главное меню\nГлавное меню");
        elif (message_text[1] == "апгрейды"):
            bot.send_message(message.chat.id, "Открывает меню апгрейдов\nАпгрейды");
        elif (message_text[1] == "бонус"):
            bot.send_message(message.chat.id, "Забрать ежедневный бонус\nБонус");
        elif (message_text[1] == "клик"):
            bot.send_message(message.chat.id, "Добавляет к балансу количество \клик\nКлик");
        elif (message_text[1] == "цена"):
            bot.send_message(message.chat.id, "Показывает цену апгрейда\nЦена <апгрейд>");
        elif (message_text[1] == "клавиатура"):
            bot.send_message(message.chat.id, "Включает/выключает клавиатуру на экране\nКлавиатура <да/нет>");
        elif (message_text[1] == "промо"):
            bot.send_message(message.chat.id, "Активирует промокод\nПромо <промокод>");
        elif (message_text[1] == "рассылка"):
            bot.send_message(message.chat.id, "Включает/выключает получение рассылки\nРассылка <да/нет>");
        elif (message_text[1] == "перевод"):
            bot.send_message(message.chat.id, "Переводит деньги пользователю\nПеревод <сумма> <id получателя> *[комментарий]*");
        elif (message_text[1] == "инфо"):
            bot.send_message(message.chat.id, "Выдает полную информацию о пользователе из бд\nИнфо <id юзера>");
        elif (message_text[1] == "дюзер"):
            bot.send_message(message.chat.id, "Удаляет пользователя из бд\nДюзер <id пользователя>");
        elif (message_text[1] == "баланс"):
            bot.send_message(message.chat.id, "Показать информацию о пользователе\nБаланс *[id пользователя]*");
        elif (message_text[1] == "бонус2"):
            bot.send_message(message.chat.id, "Забрать бонус2\nБонус2");
        elif (message_text[1] == "монета"):
            bot.send_message(message.chat.id, "Играть в монету на деньги\nМонета <ставка> <орел/решка>");
        elif (message_text[1] == "админ"):
            bot.send_message(message.chat.id, "Проверка на админа\nАдмин");
        elif (message_text[1] == "юзерслист"):
            bot.send_message(message.chat.id, "Передаёт id всех юзеров\nЮзерслист");
        elif (message_text[1] == "послать"):
            bot.send_message(message.chat.id, "Посылает игрока (1.000.000 КШ)\nПослать <id пользователя>");
        elif (message_text[1] == "послатьанон"):
            bot.send_message(message.chat.id, "Анонимно посылает игрока (3.000.000 КШ)\nПослатьанон <id пользователя>");
        elif (message_text[1] == "chatinfo"):
            bot.send_message(message.chat.id, "Передаёт всю информацию о чате\nchatinfo <id чата>");
        elif (message_text[1] == "топ"):
            bot.send_message(message.chat.id, "Выдаёт топ всех пользователей\nТоп [<b>баланс</b>/клик/сек] [страница]", parse_mode="HTML");
    def delPromo(message, message_text):
        if (rec_file.get_admin(message.from_user.id, file_readed) == False): return;
        if (len(message_text) < 3): return bot.send_message(message.chat.id, "Использование: промо удалить <название>");
        bot.send_message(message.chat.id, rec_file.promo_remove(message_text[2], file_readed));
    def sendUser(message, message_text):
        if (len(message_text) < 2) and (message_text[0] == "послать"): return bot.send_message(message.chat.id, "Послать пользователя (1.000.000 КШ): Послать <id юзера>");
        if (len(message_text) < 2) and (message_text[0] == "послатьанон"): return bot.send_message(message.chat.id, "Анонимно послать пользователя (3.000.000 КШ): Послатьанон <id юзера>");
        try: id = int(message_text[1]);
        except: 
            if (message_text[1] == "_"):
                if (message.reply_to_message != None): id = message.reply_to_message.from_user.id;
                else: return bot.send_message(message.chat.id, "При использовании _ вам необходимо ответить на сообщение юзера");
            else: return bot.send_message(message.chat.id, "ID пользователя должен состоять только из цифр!");
        if (message_text[0] == "послать"):
            if (rec_file.get_balance(message.from_user.id, file_readed) < 1000000): return bot.send_message(message.chat.id, "У вас недостаточно КШ!");
            rec_file.append_balance(message.from_user.id, -1000000, file_readed);
            file_readed["users"][str(message.from_user.id)]["othersSpends"] += 1000000
            bot.send_message(id, f"Вас послал нахуй пользователь `{message.from_user.id}`");
            bot.send_message(message.chat.id, f"Вы послали нахуй игрока `{id}`");
        elif (message_text[0] == "послатьанон"):
            if (rec_file.get_balance(message.from_user.id, file_readed) < 3000000): return bot.send_message(message.chat.id, "У вас недостаточно КШ!");
            rec_file.append_balance(message.from_user.id, -3000000, file_readed);
            file_readed["users"][str(message.from_user.id)]["othersSpends"] += 3000000
            bot.send_message(id, f"Вас анонимно послали нахуй");
            bot.send_message(message.chat.id, f"Вы анонимно послали нахуй игрока `{id}`");
    def promoInf(message, message_text):
        if (rec_file.get_admin(message.from_user.id, file_readed) == False): return
        if (len(message_text) < 3): return bot.send_message(message.chat.id, "Использование: промо инфо <название промокода>")
        if (rec_file.promo_check(message_text[2]) == False): return bot.send_message(message.chat.id, f"Промокод {message_text[2]} не найден!")
        bot.send_message(message.chat.id, rec_file.promo_info(message_text[2]))
    def promoList(message, message_text):
        if (rec_file.get_admin(message.from_user.id, file_readed) == False): return
        bot.send_message(message.chat.id, rec_file.promo_list())
    def userTop(message, message_text):
        if (len(message_text) < 2) or ((len(message_text) >= 2) and message_text[1] == "баланс"):
            if (len(message_text) < 3): bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "б", message.from_user.id, 1), parse_mode="HTML")
            else: 
                try:
                    page = int(message_text[2])
                    bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "б", message.from_user.id, page), parse_mode="HTML")
                except Exception as e:
                    print(e)
                    bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "б", message.from_user.id, 1), parse_mode="HTML")
        elif (len(message_text) >= 2) and (message_text[1] == "клик"):
            if (len(message_text) < 3): bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "к", message.from_user.id, 1), parse_mode="HTML")
            else: 
                try:
                    page = int(message_text[2])
                    bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "к", message.from_user.id, page), parse_mode="HTML")
                except: bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "к", message.from_user.id, 1), parse_mode="HTML")
        elif (len(message_text) >= 2) and (message_text[1] == "сек"):
            if (len(message_text) < 3): bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "с", message.from_user.id, 1), parse_mode="HTML")
            else: 
                try:
                    page = int(message_text[2])
                    bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "с", message.from_user.id, page), parse_mode="HTML")
                except: bot.send_message(message.chat.id, rec_file.leaderboard(file_readed, "с", message.from_user.id, 1), parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Использование: топ [<b>баланс</b>/клик/сек] [страница]", parse_mode="HTML")
    def chatInfo(message, message_text):
        if (rec_file.get_admin(message.from_user.id, file_readed)):
            if (len(message_text) < 2): return bot.reply_to(message, "Использование: chatinfo <chatid>")
            try: id = int(message_text[1])
            except: return bot.reply_to(message, "Неверное id чата!")
            bot.reply_to(message, bot.get_chat(id), parse_mode="HTML")

bot.polling(none_stop=True, interval=1, timeout=123)
#962 -> 630
