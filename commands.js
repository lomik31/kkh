exports.COMMANDS = {
    "бэкап": {
        description: "Создаёт бэкап в папку с бэкапами и загружает в облако",
        action: "new kmd(message, client).backup()",
        usage: "бэкап <создать>",
        permissions: "admin"
    },
    "🔮": {
        link: "клик"
    },
    "б": {
        link: "баланс"
    },
    "бдзапись": {
        description: "Записывает бд в файл",
        action: "new kmd(message, client).dbWrite()",
        usage: "бдзапись",
        permissions: "admin",
        links: ["записьбд"]
    },
    "записьбд": {
        link: "бдзапись"
    },
    "кмд": {
        description: "Отправляет команду от имени другого юзера",
        action: "",
        usage: "кмд <id юзера> <команда> [...аргументы команды]",
        permissions: "admin"
    },
    "_": {
        description: "Повторить последнюю выполненную команду",
        action: "",
        usage: "_",
        permissions: "user"

    },
    "команды": {
        description: "Показывает список команд",
        action: "new kmd(message, client).commandsList()",
        usage: "команды",
        permissions: "user"
    },
    "команда": {
        description: "Показывает справку по использованию команды",
        action: "new kmd(message, client).helpCommand()",
        usage: "команда <команда>",
        permissions: "user"
    },
    "главное меню": {
        description: "Открывает главное меню",
        action: "kmd.main_menu(message, message_text)",
        usage: "главное меню",
        permissions: "user"
    },
    "апгрейды": {
        description: "Открывает меню апгрейдов",
        action: "kmd.upgrades(message, message_text)",
        usage: "апгрейды",
        permissions: "user"
    },
    "бонус": {
        description: "Забрать ежедневный бонус",
        action: "new kmd(message, client).bonus()",
        usage: "бонус",
        permissions: "user"
    },
    "клик": {
        description: "Добавляет к балансу количество \клик",
        action: "new kmd(message, client).click()",
        links: ["🔮"],
        usage: "клик",
        permissions: "user"
    },
    "цена": {
        description: "Показывает цену апгрейда",
        action: "new kmd(message, client).price()",
        usage: "цена <апгрейд>",
        permissions: "user"
    },
    "клавиатура": {
        description: "Включает/выключает клавиатуру на экране",
        action: "kmd.keyboard(message, message_text)",
        usage: "клавиатура <да/нет>",
        permissions: "user"
    },
    "промо": {
        description: "Активирует промокод",
        action: "kmd.activate_promo(message, message_text)",
        usage: "промо <промокод>",
        permissions: "user"
    },
    "рассылка": {
        description: "Включает/выключает получение рассылки",
        action: "kmd.rassilka(message, message_text)",
        usage: "рассылка <да/нет>",
        permissions: "user"
    },
    "перевод": {
        description: "Переводит деньги пользователю",
        action: "new kmd(message, client).pay()",
        usage: "перевод <сумма> <id получателя> [комментарий]",
        permissions: "user"
    },
    "инфо": {
        description: "Выдает полную информацию о пользователе из бд",
        action: "kmd.full_inf_user(message, message_text)",
        usage: "инфо <id юзера>",
        permissions: "admin"
    },
    "дюзер": {
        description: "Удаляет пользователя из бд",
        action: "kmd.del_user(message, message_text)",
        usage: "дюзер <id пользователя>",
        permissions: "admin"
    },
    "баланс": {
        description: "Показать информацию о пользователе",
        action: "new kmd(message, client).balance()",
        links: ["б"],
        usage: "баланс [id пользователя]",
        permissions: "user"
        },
    "бонус2": {
        description: "Забрать бонус2",
        action: "new kmd(message, client).bonus2()",
        usage: "бонус2",
        permissions: "user"
    },
    "монета": {
        description: "Играть в монету на деньги",
        action: "kmd.moneta(message, message_text)",
        usage: "монета <ставка> <орел/решка>",
        permissions: "user",
        links: ["монетка"]
    },
    "юзерслист": {
        description: "Передаёт id всех юзеров",
        action: "kmd.userlist(message, message_text)",
        usage: "юзерслист",
        permissions: "admin"
    },
    "послать": {
        description: "Посылает игрока (1.000.000 КШ)",
        action: "new kmd(message, client).sendUser()",
        usage: "послать <id пользователя>",
        permissions: "user"
    },
    "послатьанон": {
        description: "Анонимно посылает игрока (3.000.000 КШ)",
        action: "new kmd(message, client).sendUser()",
        usage: "послатьанон <id пользователя>",
        permissions: "user"
    },
    "топ": {
        description: "Показывает топ пользователей по параметру",
        action: "new kmd(message, client).top()",
        usage: "топ [<b>баланс</b>/клик/сек/буст баланса/рег/банк/деньги] [страница]",
        parse: "HTML",
        permissions: "user"
    },
    "всетоп": {
        description: "Показывает топ всех пользователей по параметру",
        action: "new kmd(message, client).top()",
        usage: "топ [<b>баланс</b>/клик/сек] [страница]",
        parse: "HTML",
        permissions: "user"
    },
    "бит": {
        description: "Ставка на курс биткоина",
        action: "kmd.btcBet(message, message_text)",
        usage: "бит <ставка> <вверх/вниз>",
        permissions: "user"
    },
    "монетарозыгрыш": {
        description: "Принудительно проводит еженедельный розыгрыш проигранных денег в монете",
        action: "weeklyLotteryLostMoneyCoin()",
        usage: "монетарозыгрыш",
        permissions: "admin"
    },
    "банк": {
        description: "Перевод КШ в банк/из банка",
        action: "",
        usage: "+банк [сумма] / -банк [сумма]",
        permissions: "user"
    },
    "+банк": {
        description: "Перевод КШ в банк",
        action: "kmd.bankPut(message, message_text)",
        usage: "+банк [сумма]",
        permissions: "user"
    },
    "-банк": {
        description: "Вывод КШ из банка",
        action: "kmd.bankTake(message, message_text)",
        usage: "-банк [сумма]",
        permissions: "user"
    },
    "назад": {
        description: "Выйти из меню",
        action: "kmd.back(message, message_text)",
        usage: "назад",
        permissions: "user",
        links: ["выйти"]
    },
    "выйти": {
        link: "назад"
    },
    "монетка": {
        link: "монета"
    },
    "сброс": {
        description: "Вы начинаете игру заново. Для дополнительной информации воспользуйтесь командой `сброс справка`",
        action: "kmd.reset(message, message_text)",
        usage: "сброс [справка/подтвердить]",
        permissions: "user",
        parse: "Markdown"
    },
    "админ": {
        description: "проверка на админа",
        action: "kmd.admin(message, message_text)",
        usage: "админ",
        permissions: "user"
    },
    "нпромо": {
        description: "Добавить новый промокод",
        action: "kmd.addPromo(message, message_text)",
        usage: "нпромо <название> <params({'balance':0, 'click':0, 'sec':0, 'sale':0, 'multiplier':0, 'balanceBoost':0})> <кол-во активаций> <время действия>",
        permissions: "admin"
    },
    "дпромо": {
        description: "Удалить промокод",
        action: "kmd.delPromo(message, message_text)",
        usage: "дпромо <название>",
        permissions: "admin"
    },
    "ипромо": {
        description: "Показать информацию по промокоду",
        action: "kmd.promoInf(message, message_text)",
        usage: "ипромо <название>",
        permissions: "user"
    },
    "лпромо": {
        description: "Показать список промокодов",
        action: "kmd.promoList(message, message_text)",
        usage: "лпромо",
        permissions: "admin"
    }
}