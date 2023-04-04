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
        action: "new kmd(message, client).backKeyboardMenu()",
        usage: "главное меню",
        permissions: "user"
    },
    "апгрейды": {
        description: "Открывает меню апгрейдов",
        action: "new kmd(message, client).upgrades()",
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
        action: "new kmd(message, client).keyboardSet()",
        usage: "клавиатура <да/нет>",
        permissions: "user"
    },
    "промо": {
        description: "Активирует промокод",
        action: "new kmd(message, client).promoActivate()",
        usage: "промо <промокод>",
        permissions: "user"
    },
    "рассылка": {
        description: "Включает/выключает получение рассылки",
        action: "new kmd(message, client).mailing()",
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
        action: "new kmd(message, client).getUserInfo()",
        usage: "инфо <id юзера>",
        permissions: "admin"
    },
    "дюзер": {
        description: "Удаляет пользователя из бд",
        action: "new kmd(message, client).removeId()",
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
        action: "new kmd(message, client).coin()",
        usage: "монета <ставка> <орел/решка>",
        permissions: "user",
        links: ["монетка"]
    },
    "юзерслист": {
        description: "Передаёт id всех юзеров",
        action: "new kmd(message, client).usersList()",
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
        action: "new kmd(message, client).btcBet()",
        usage: "бит <ставка> <вверх/вниз>",
        permissions: "user"
    },
    "банк": {
        description: "Перевод КШ в банк/из банка",
        action: "new kmd(message, client).bankTransfer()",
        usage: "+банк [сумма] / -банк [сумма]",
        permissions: "user",
        links: ["+банк", "-банк"]
    },
    "+банк": {
        link: "банк"
    },
    "-банк": {
        link: "банк"
    },
    "назад": {
        description: "Выйти из меню",
        action: "new kmd(message, client).backKeyboardMenu()",
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
        action: "new kmd(message, client).resetId()",
        usage: "сброс [справка/подтвердить]",
        permissions: "user",
        parse: "Markdown"
    },
    "админ": {
        description: "проверка на админа",
        action: "new kmd(message, client).admin()",
        usage: "админ",
        permissions: "user"
    },
    "нпромо": {
        description: "Добавить новый промокод",
        action: "new kmd(message, client).promoAdd()",
        usage: "нпромо <название> <params({'balance':0, 'click':0, 'sec':0, 'sale':0, 'multiplier':0, 'balanceBoost':0})> <кол-во активаций> <время действия>",
        permissions: "admin"
    },
    "дпромо": {
        description: "Удалить промокод",
        action: "new kmd(message, client).promoDelete()",
        usage: "дпромо <название>",
        permissions: "admin"
    },
    "ипромо": {
        description: "Показать информацию по промокоду",
        action: "new kmd(message, client).promoInfo()",
        usage: "ипромо <название>",
        permissions: "user"
    },
    "лпромо": {
        description: "Показать список промокодов",
        action: "new kmd(message, client).promoList()",
        usage: "лпромо",
        permissions: "admin"
    },
    "фипромо": {
        description: "Показать полную информацию о промокоде",
        action: "new kmd(message, client).promoFullInfo()",
        usage: "фипромо <название>",
        permissions: "admin"
    },
    "set": {
        description: "Установить значение пользователю",
        action: "new kmd(message, client).set()",
        usage: "set <id> <параметр> <значение>",
        permissions: "admin"
    },
    "dot": {
        description: "Разделить число по разрядам",
        action: "new kmd(message, client).dotValue()",
        usage: "dot <число>",
        permissions: "admin"
    },
    "нревард": {
        description: "Добавить новую награду",
        action: "new kmd(message, client).rewardAdd()",
        usage: "нревард <смайлик награды> <название...> || <описание...>",
        permissions: "admin"
    }
}