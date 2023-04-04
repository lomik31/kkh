const { randomInt } = require('crypto');
const fs = require('fs');
const schedule = require('node-schedule');
const data = require('./usrs.json');
const config = require("./config.json");
const http = require("http");
const { request } = require('https');
const { parse } = require('url');
const { upload } = require("ya-disk");
const express = require("express");
const WebSocket = require("ws");
const app = express();
const server = http.createServer(app);
const webSocketServer = new WebSocket.Server({ server });
const request1 = require('request');
const { COMMANDS } = require("./commands");
const dateFormat = require('dateformat');

let CLIENTS = {};
webSocketServer.on('connection', (ws, req) => {
    ws.on('message', m => dispatchEvent(m, ws));
    let name = req.url.replace('/?client=', '');
    CLIENTS[name] = ws;
    CLIENTS[name].sendData = ws.send;
    CLIENTS[name].send = (data) => {
        if (!data.serverId) delete data.serverId;
        ws.sendData(JSON.stringify(data))
    }
    CLIENTS[name].sendMessage = ({chatId, serverId = undefined, text, parseMode = undefined, keyboard = undefined}) => {
        let message = {};
        if (serverId) message.serverId = serverId;
        message.chatId = chatId;
        message.text = text;
        if (parseMode) message.parseMode = parseMode;
        if (keyboard) message.keyboard = keyboard;
        CLIENTS[name].send({event: "sendMessage", message})
    }
    console.log(`New connection: ${name}. All connections: ${Object.keys(CLIENTS)}`);
    ws.on("error", e => {
        throw new Error(e);
    });
    ws.on("close", (code, reason) => {
        delete CLIENTS[name]
        console.log(`Client ${name} disconnected. All connections: ${Object.keys(CLIENTS)}`);
        
    })
});
const dispatchEvent = (message, ws) => {
    const json = JSON.parse(message);
    if (json.event == "newMessage") textReceiver(json.message, json.client);
    if (json.event == "newCommand") commandReceiver(json.message, json.client);
}
server.listen(3200, () => console.log("Server started"))

function commandReceiver(message, client) {
    if (message.text == "/start") {
        if (get.id(message.from_user.id)) {
            if (message.chat.type == "private") CLIENTS[client].sendMessage({chatId: message.chat.id, text: "Привет. Это бот-кликер.\nСделали: [@lomik31](tg://user?id=357694314), [@Discord Nitra MV](tg://user?id=1160222752).\nЕсли ты Игорькартошка или Денисизюм, то тебе [сюда](https://docs.google.com/document/d/15a6S5F26kxRn103Yboknpogu-tJtIoxin2G9tBjY65A).\nПо вопросам обращаться к ним.\n[Планы на будущее и то, что в разработке](https://trello.com/b/kfVkY65h/%D0%BA%D0%BA%D1%88)\nНаш канал с новостями: [@kkh_news] (t.me/kkh_news)\nДля списка всех команд введите `команды`.\nЕсли у вас есть промо-код, можете ввести его при помощи `промо <код>`\nНаша беседа: [тык](t.me/+_VgA7r0PfWZiMGFi)\n\n*По вопросам пишите* [@lomik31](tg://user?id=357694314)", parseMode: "MARKDOWN"});
            else CLIENTS[client].sendMessage({chatId: message.chat.id, text:  "Эту команду можно использовать только в личных сообщениях с ботом!"});
            return;
        }
        if (message.chat.type == "private") append.appendId("private", message.chat.id, message.chat.first_name, message.chat.last_name);
        else append.appendId(message.chat.type, message.chat.id);
        CLIENTS[client].sendMessage({chatId: message.chat.id, text: "Привет. Это бот-кликер.\nСделали: [@lomik31](tg://user?id=357694314), [@Discord Nitra MV](tg://user?id=1160222752).\nЕсли ты Игорькартошка или Денисизюм, то тебе [сюда](https://docs.google.com/document/d/15a6S5F26kxRn103Yboknpogu-tJtIoxin2G9tBjY65A).\nПо вопросам обращаться к ним.\n[Планы на будущее и то, что в разработке](https://trello.com/b/kfVkY65h/%D0%BA%D0%BA%D1%88)\nНаш канал с новостями: [@kkh_news] (t.me/kkh_news)\nДля списка всех команд введите `команды`.\nЕсли у вас есть промо-код, можете ввести его при помощи `промо <код>`\nНаша беседа: [тык](t.me/+_VgA7r0PfWZiMGFi)\n\n*По вопросам пишите* [@lomik31](tg://user?id=357694314)", parseMode: "MARKDOWN"});
    }
}
function textReceiver(message, client) {
    if (!get.id(message.from_user.id)) return CLIENTS[client].sendMessage({chatId: message.chat.id, text: "Для взаимодействия с ботом вам необходимо сначала активировать его. Напишите боту *в ЛС* команду /start!", parseMode: "MARKDOWN"})
    let message_text = message.text.toLowerCase().split(" ");
    if (!(["кмд", "_"].includes(message_text[0]) || (message_text[0][0] == "+"))) {
        let i = 0;
        let checkCommand = message_text[0];
        while (true) {
            if (i > 3) return;
            if (Object.keys(COMMANDS).includes(checkCommand)) {
                if (Object.keys(COMMANDS[checkCommand]).includes("link")) checkCommand = COMMANDS[checkCommand].link;
                if (COMMANDS[checkCommand].permissions == "admin" && !get.get(message.from_user.id, "isAdmin")) return;
                if (COMMANDS[checkCommand].permissions == "owner" && message.from_user.id != 357694314) return; //ВНИМАНИЕ БЛЯТЬ
                //лог
                eval(COMMANDS[checkCommand]["action"]);
                break;
            }
            i++;
            if (i > message_text.length - 1 ) return;
            checkCommand += ` ${message_text[i]}`
        }
    }
    else if (message_text[0] == "кмд") {
        if (!get.get(message.from_user.id, "isAdmin")) return;
        if (message_text.length < 3) {
            message.text = "команда кмд";
            return textReceiver(message, client);
        }
        if (message_text[1] == "_" && message.reply_to_message) userId = message.reply_to_message.from_user.id;
        else userId = message_text[1];
        if (!get.id(userId)) return CLIENTS[client].sendMessage({chatId: message.chat.id, text: "Id не найден"});
        if (message_text[2] == "кмд") return CLIENTS[client].sendMessage({chatId: message.chat.id, text: "э, так нельзя, бан"});
        if (get.get(userId, "isAdmin") && message.from_user.id != 357694314) return CLIENTS[client].sendMessage({chatId: message.chat.id, text: "Невозможно выполнить кмд для этого юзера!"});
        new kmd(message, message_text);
        message.from_user.id = userId;
        let a = message.text.split(" ").slice(2);
        message.text = "";
        let b = 0;
        for (i of a) {
            b = a.length - 1;
            if (b == 0) message.text += i;
            else message.text += `${i} `;
        }
        message.text = message.text.slice(0, -1);
        textReceiver(message, client);
    }
    else if (message_text[0] == "_") {
        let command = get.get(message.from_user.id, "lastCommand");
        if (command == "") return CLIENTS[client].sendMessage({chatId: message.chat.id, text: "Последняя команда не обнаружена"});
        message.text = command;
        textReceiver(message, client);
    }
    else if (message_text[0][0] == "+") {
        let loxtext = message.text;
        let r = new RegExp(/ \(\d+[\.\d]* КШ\)/);
        if (r.test(message.text)) message.text = message.text.replace(r, "");
        message.text = message.text.slice(1);
        message_text = message.text.toLowerCase().split(" ");
        let a = [];
        let t = "";
        for (let i of message_text) {
            a.push(i);
            t = a.join(" ");
            if (["сек", "клик", "скидка", "1% скидки", "банк"].includes(t)) return new kmd(message, client, loxtext).buyBoost(t);
        }
        return CLIENTS[client].sendMessage({chatId: message.chat.id, text: "Неверный тип апгрейда"});
    }
}
function choose(choices) {
    return choices[Math.floor(Math.random() * choices.length)];
}

let accrual = {
    sec: function () {
        for (let i in data.users) {
            if (data.users[i].bank + data.users[i].sec < data.users[i].bankMax) {
                data.users[i].bank += data.users[i].sec;
                data.users[i].earnedKkh += data.users[i].sec;
            }
            else if (data.users[i].bank < data.users[i].bankMax) {
                data.users[i].earnedKkh += data.users[i].bankMax - data.users[i].bank;
                data.users[i].bank = data.users[i].bankMax;
                
            }
        };
        file.write();
    },
    click: function (userId) {
        data.users[userId].balance += data.users[userId].click;
        data.users[userId].earnedKkh += data.users[userId].click;
    }
}
let file = {
    write: function () {
        fs.writeFile("usrs.json", JSON.stringify(data, null, "    "), (err) => {if (err) console.error(err)});
    },
    read: function () {
        data = require("usrs.json");
    }
}
let append = {
    appendId: function (appendType, appendId, firstName = null, lastName = null) {
        if (appendType === "private") {
            if (get.id(appendId)) return {success: false, message: `Пользователь ${appendId} уже существует`} 
            data.users[appendId] = structuredClone(data.users.default);
            data.users[appendId].firstName = firstName;
            data.users[appendId].registerTime = get.time();
            if (lastName != null) data.users[appendId].lastName = lastName;
            return {success: true}
        }
        else if (appendId in data.groups) return {success: false, message: `Группа ${appendId} уже существует`} 
        data.groups[appendId] = structuredClone(data.groups.default);
        return {success: true}
    },
    appendToUser: function (userId, toAppend, appendAmount) {
        let appendVariables = ["balance", "click", "sec", "sale", "bankMax", "lastCommand", "bank"];
        if (appendVariables.indexOf(toAppend) === -1) return {success: false, message: `Параметр ${toAppend} не найден`};
        appendAmount = obrabotka.kChisla(appendAmount);
        if (typeof data.users[userId][toAppend] != typeof appendAmount || isNaN(appendAmount)) return {success: false, message: "Ошибка типа"};
        if (toAppend === "lastCommand") {
            data.users[userId][toAppend] = appendAmount;
            data.users[userId]["timeLastCommand"] = get.time();
        }
        else data.users[userId][toAppend] += appendAmount;
        return {success: true}
    }
}
let get = {
    get: function (id, toGet) {
        let getValues = ["balance", "click", "sec", "keyboard", "sale", "isAdmin",
        "activeKeyboard", "mails", "timeLastBonus", "timeLastSecondBonus", "lastCommand", "bank",
        "multiplier", "receiver", "bankMax", "rewards"]
        if (toGet == "all") return data.users[id]
        else if (toGet == "fullName") {
            let name = data.users[id]["firstName"];
            if (data.users[id]["lastName"] !== null) name += ` ${data.users[id]["lastName"]}`;
            return name;
        }
        else if (toGet == "rewards") return Object.keys(data.users[id].rewards);
        if (getValues.indexOf(toGet) == -1) return {success: false, message: "Данный параметр не найден"};
        let toReturn = data.users[id][toGet];
        return toReturn;
        
    },
    ids: function () {
        let ids = Object.keys(data.users);
        ids.splice(ids.indexOf('default'), 1);
        return ids;
    },
    id: function (id, type = "private") {
        if (type == "private" && id in data.users) return true
        if (id in data.groups) return true
        return false
    },
    time: function () {
        return Number(Math.floor(Date.now() / 1000))
    },
    keyboardCosts: function (id) {
        let sec = obrabotka.chisla(calc.boost(id, "sec").cost);
        let click = obrabotka.chisla(calc.boost(id, "click").cost);
        let sale = function () {
            let a = calc.boost(id, "sale");
            if (a.success) return `+1% скидки (${obrabotka.chisla(a.cost)} КШ)`
            else return a.message
        }();
        let bankMax = obrabotka.chisla(calc.boost(id, "bankMax").cost);
        return {sec, click, sale, bankMax};
    },
    keyboard: function (id, keyboardType, chatType = "private") {
        if (chatType == "private") {
            return get.get(id, keyboardType)
        }
        else return data.groups[id][keyboardType]
    },
    data: (id) => data.users[id]
}
let calc = {
    boost: function (id, boost) {
        let nac_cena, procent, limit;
        if (boost == "click") {
            nac_cena = 100; //изначальная цена
            procent = 15; //процент стоимости следующего буста
            limit = -1;
        }
        else if (boost == "sec") {
            nac_cena = 300; //изначальная цена
            procent = 15; //процент стоимости следующего буста
            limit = -1;
        }
        else if (boost == "sale") {
            nac_cena = 7500; //изначальная цена
            procent = 15; //процент стоимости следующего буста
            limit = 45;
        }
        else if (boost == "bankMax") {
            nac_cena = 3498; //изначальная цена
            procent = 0.06; //процент стоимости следующего буста
            limit = 5_000_000;
        }
        else return {success: false, message: "Неверный параметр boost"}
        let boost_level = get.get(id, boost);
        if (boost == "bankMax") boost_level = Math.floor(boost_level/1000)
        if (boost_level >= limit && limit != -1) return {success: false, message: `Достигнут максимум апгрейдов этого типа`}
        let skidka = get.get(id, "sale");
        for (let i = 0; i < boost_level; i++) nac_cena = nac_cena * (100 + procent) / 100;
        nac_cena = Math.floor(nac_cena * (100 - skidka) / 100);
        return {success: true, cost: nac_cena, data: `Цена за ${boost_level + 1} апгрейд со скидкой ${skidka}%: ${obrabotka.chisla(nac_cena)} КШ`};

    }
}
let keyboard = {
    upgrade: function(userId) {
        if (!get.id(userId)) return {success: false, message: "Id не найден"};
        let res = get.keyboardCosts(userId);
        let keyboard = [[`+сек (${res.sec} КШ)`, `+клик (${res.click} КШ)`], [res.sale, `+банк (${res.bankMax} КШ)`], ["Назад"]];
        return keyboard;
    },
    mainMenu: [["🔮"], ["Апгрейды", "Баланс"], ["Сброс"]]
}
let obrabotka = {
    chisla: function (chislo_okda) {
        let t_result = ""
        let result = ""
        chislo_okda = String(chislo_okda)
        if (chislo_okda[0] == "-") {
            result += "-";
            chislo_okda = chislo_okda.slice(1);
        }
        let counter=0
        for (let i = 1; i <= chislo_okda.length; i++) {
            if (counter % 3 == 0 && counter != 0) t_result += ".";
            t_result += chislo_okda[chislo_okda.length - i];
            counter = counter + 1;
        }
        for (let i = 1; i <= t_result.length; i++) result += t_result[t_result.length - i];
        return result
    },
    obratnoChisla: function (chislo_okda) {
        if (typeof chislo_okda == "number") return chislo_okda
        result = ""
        for (let i = 0; i < chislo_okda.length; i++)
            if (chislo_okda[i] != "." && chislo_okda[i] != ",") result += chislo_okda[i]
        return result
    },
    kChisla: function (chislo_okda) {
        chislo_okda = obrabotka.obratnoChisla(chislo_okda)
        if (typeof chislo_okda == "number") return chislo_okda
        let chislo_oknet = "";
        for (let i of chislo_okda) {
            if (!isNaN(Number(i))) chislo_oknet += i;
            else if (i == "к" || i == "k") chislo_oknet += "000";
            else if (i=="м" || i=="m") chislo_oknet += "000000";
            else if (i == "-") chislo_oknet += "-"
        }
        return Number(chislo_oknet)
        // for (let i = 0; i < chislo_okda; i++) {
        //     if (i=="k" || i == "к") chislo_oknet += "000"
        //     else if (i=="m" || i=="м") chislo_oknet += "000000"
        // }
        // return chislo_oknet
    },
    vremeni: function (vremya_okda) {
        return dateFormat(vremya_okda*1000, "dd.mm.yyyy HH:MM:ss");
    },
    vremeniBonusa: function(vremya_okda) {
        return `${dateFormat(vremya_okda*1000, "HH:MM:ss")}`;
    }
}
let give = {
    bonus: function (id) {
        if (get.time() - get.get(id, "timeLastBonus") < 86400) return {success: false, message: `Ежедневный бонус уже был получен сегодня\nДо следующего бонуса: ${obrabotka.vremeniBonusa(get.get(id, "timeLastBonus") + 86400 - get.time() - 10800)}`};
        let mnoz = data.users[id].multiplier;
        let mnoz2 = 0;
        let t = get.time();
        for (let i of data.users[id].timeLast3Bonus) {
            if (t - i >= 172800) break
            t = i;
            mnoz2++;
        }
        let bonus = Math.round(get.get(id, "sec") * 4000 + get.get(id, "click") * 6500 + 1.135**get.get(id, "sec") + 1.145**get.get(id, "click") + 1.14**get.get(id, "sale")) * (mnoz + mnoz2);
        append.appendToUser(id, "balance", bonus);
        data.users[id].othersProceeds += bonus;
        data.users[id].timeLastBonus = get.time();
        data.users[id].timeLast3Bonus.splice(0, 0, get.time())
        data.users[id].timeLast3Bonus = data.users[id].timeLast3Bonus.slice(0, -1)
        let msg = `Вы забрали ежедневный бонус ${obrabotka.chisla(bonus)} КШ\n`;
        if (mnoz > 1) msg += `(Стандартный множитель - x${mnoz})\n`
        if (mnoz2 > 0) msg += `(Множитель за ежедневную активность - x${mnoz2})\n`
        if (mnoz + mnoz2 > 1) msg += `Суммарный множитель - x${mnoz + mnoz2}\n`
        msg += `Баланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ`
        return {success: true, data: msg};
    },
    bonus2: function (id) {
        if (get.time() - get.get(id, "timeLastSecondBonus") < 28800) return {success: false, message: `Бонус2 можно получать каждые 8 часов\nДо следующего бонуса2: ${obrabotka.vremeniBonusa(get.get(id, "timeLastSecondBonus") + 28800 - get.time() - 10800)}`}
        let bonus = randomInt(10000, (get.get(id, "sec") * 3600 + get.get(id, "click") * 5400) + 10000);
        append.appendToUser(id, "balance", bonus);
        data.users[id].othersProceeds += bonus;
        data.users[id].timeLastSecondBonus = get.time();
        return {success: true, data: 'Вы получили случайный бонус2  в размере ' + obrabotka.chisla(bonus) + ' КШ\nБаланс: ' + obrabotka.chisla(get.get(id, "balance")) + ' КШ'};
    }
}
let set = {
    lastCommand: function (id, command) {
        if (!get.id(id)) return {success: false};
        data.users[id].lastCommand = command;
        data.users[id].timeLastCommand = get.time();
        return {success: true};
    },
    set: function (id, toSet, value) {
        let setValues = ["isAdmin", "multiplier", "mails", "balance", "click", "sec", "sale", "bankMax", "bank", "timeLastBonus", "keyboard", "activeKeyboard"];
        if (setValues.indexOf(toSet) == -1) return {success: false, message: `Невозможно изменить значение ${toSet}`};
        if (["string", "number"].indexOf(typeof value) != -1) value = obrabotka.kChisla(value)
        if (typeof data.users[id][toSet] != typeof value || isNaN(value)) return {success: false, message: "Ошибка типа"};
        data.users[id][toSet] = value;
        return {success: true};
    },
    keyboard: {
        passive: function (id, type, state) {
            if (type == "private") {
                if (!get.id(id)) return {success: false, message: "Неверный пользователь"};
                data.users[id].keyboard = state;
                return {success: true}
            }
            else {
                if (!(id in data.groups)) return {success: false, message: "Неверная группа"};
                data.groups[id].keyboard = state;
                return {success: true}
            }
        },
        active: function (id, type, state) {
            if (type == "private") {
                if (!get.id(id)) return {success: false, message: "Неверный пользователь"};
                data.users[id].activeKeyboard = state;
                return {success: true}
            }
            else {
                if (!(id in data.groups)) return {success: false, message: "Неверная группа"};
                data.groups[id].activeKeyboard = state;
                return {success: true}
            }
        }
    }
}
let promo = {
    list: function () {
        let promos = require("./promos.json");
        msg = `Список промокодов: ${Object.keys(promos.allPromos).filter((f) => f != "default").join(", ")}`;
        promos = null;
        return {success: true, message: msg};
    },
    fInfo: function (promo_okda) {
        let promos = require("./promos.json");
        if (!promo.check(promo_okda)) return {success: false, message: "Промокода не существует!"};
        return {success: true, message: JSON.stringify(promos.allPromos[promo_okda], null, "    "), data: promos.allPromos[promo_okda]};
    },
    delete: function (promo_okda) {
        let promos = require("./promos.json");
        if (!promo.check(promo_okda)) return {success: false, message: "Промокода не существует!"};
        delete promos.allPromos[promo_okda];
        promo.writeFile(promos);
        for (let i of Object.keys(data.users)) {
            if (data.users[i].activatedPromos.indexOf(promo_okda) != -1) data.users[i].activatedPromos.splice(data.users[i].activatedPromos.indexOf(promo_okda), 1);
        }
        return {success: true};
    },
    writeFile: function (promoFile) {
        fs.writeFile("promos.json", JSON.stringify(promoFile, null, "    "), (err) => {if (err) console.error(err)});
    },
    check: function (promo_okda) {
        let promos = require("./promos.json");
        if (promos.allPromos[promo_okda] == undefined) return false;
        return true;
    },
    info: function (promo_okda) {
        if (!promo.check(promo_okda)) return {success: false, message: "Промокод не найден!"};
        let promos = require("./promos.json");
        let ebp = Object.keys(promos.allPromos[promo_okda]).filter((i) => !(i in ["activationLimit", "activatedTimes", "validity"]));
        msg = "";
        for (let i of ebp) {
            if (promos.allPromos[promo_okda][i] == 0) continue;
            if (i == "balance") msg += `${promos.allPromos[promo_okda][i]} КШ, `
            else if (i == "click") msg += `+ ${promos.allPromos[promo_okda][i]} КШ за клик, `
            else if (i == "sec") msg += `+ ${promos.allPromos[promo_okda][i]} КШ за секунду, `
            else if (i == "sale") msg += `+ ${promos.allPromos[promo_okda][i]}% скидки, `
            else if (i == "multiplier") msg += `+ ${promos.allPromos[promo_okda][i]}x бонуса, `
            else if (i=="balanceBoost") msg += `+ ${promos.allPromos[promo_okda][i]} буста баланса, `
        }
        msg = msg.slice(0, msg.length - 2);
        if (msg == "") return {success: false, message: "Промокод не найден!"};
        return {success: true, message: `Промокод даёт: ${msg}`};
    },
    add: function (name, data, activationLimit, validity) {
        if (promo.check(name)) return {success: false, message: "Промокод уже существует"};
        delete data.validity;
        delete data.activationLimit;
        delete data.activatedTimes;
        for (let i of Object.keys(data)) {
            if (Object.keys(promo.fInfo("default").data).indexOf(i) == -1) return {success: false, message: "Введено недопустимое значение! Операция отменена"}
        }
        activationLimit = Number(activationLimit);
        if (isNaN(activationLimit)) return {success: false, message: "Неверный параметр кол-во активаций"};
        if (activationLimit < -1 || activationLimit == 0) activationLimit = -1;
        if (isNaN(Number(validity))) {
            let a;
            for (let i in validity) {
                if (isNaN(Number(validity[i]))) {
                    a = i;
                    break;
                }
            }
            if (a === 0 || validity.length - a > 3) return {success: false, message: "Неверное значение времени действия"};
            a = validity.slice(a);
            validity = parseInt(validity);
            if (a == "s" || a == "с") validity *= 1;
            else if (a == "m" || a == "мин") validity *= 60;
            else if (a == "h" || a == "ч") validity *= 3600;
            else if (a == "d" || a == "д") validity *= 86400;
            else if (a == "w" || a == "нед") validity *= 604800;
            else if (a == "mo" || a == "мес") validity *= 2592000;
            else if (a == "y" || a == "г") validity *= 31536000;
            else return {success: false, message: "Неверное значение времени действия"};
            validity += get.time();
        }
        else {
            validity = Number(validity);
            if (validity < (get.time() - 5)) validity = -1;
        }
        let promos = require("./promos.json");
        promos.allPromos[name] = structuredClone(promos.allPromos.default);
        Object.keys(data).forEach(i => promos.allPromos[name][i] = data[i]);
        promos.allPromos[name]["activationLimit"] = activationLimit;
        promos.allPromos[name]["validity"] = validity;
        fs.writeFileSync("./promos.json", JSON.stringify(promos, null, "    "));
        if (promo.check(name)) return {success: true};
        else return {success: false, message: "Произошла ошибка при добавлении промокода"};
    },
    activate: function (userId, name) {
        if (!get.id(userId)) return {success: false, message: "Пользователь не существует"};
        if (name == "default") return {success: false, message: "Ща твой прогресс по дефолту ёбну"};
        if (!promo.check(name)) return {success: false, message: "Промокода не существует!"};
        if (data.users[userId].activatedPromos.indexOf(name) != -1) return {success: false, message: "Промокод уже активирован"};
        if (promo.fInfo(name).data.validity < get.time() &&promo.fInfo(name).data.validity != -1) return {success: false, message: "Истекло время активации промокода"};
        if (promo.fInfo(name).data.activatedTimes >= promo.fInfo(name).data.activationLimit && promo.fInfo(name).data.activationLimit != -1) return {success: false, message: "Превышено число активаций промокода"};
        let promos = require("./promos.json");
        let message = "";
        let value;
        for (let i of Object.keys(promos.allPromos[name])) {
            if (["activationLimit", "activatedTimes", "validity"].indexOf(i) != -1) continue;
            if (i != "sale" || (i == "sale" && data.users[userId][i] < 100)) data.users[userId][i] += promos.allPromos[name][i];
            if (promos.allPromos[name][i] != 0) {
                if (promos.allPromos[name][i] < 0) value = promos.allPromos[name][i];
                else value = `+${promos.allPromos[name][i]}`;
                message += "\n";
                switch (i) {
                    case "balance":
                        message += `${obrabotka.chisla(promos.allPromos[name][i])} КШ`;
                        data.users[userId].othersProceeds += promos.allPromos[name][i];
                        break;
                    case "click":
                        message += `${value}/клик`;
                        break;
                    case "sec":
                        message += `${value}/сек`;
                        break;
                    case "sale":
                        message += `${value}% скидки`;
                        break;
                    case "multiplier":
                        message += `${value}x множитель ежедневного бонуса`;
                        break;
                    case "balanceBoost":
                        message += `${value}% баланса/день`;
                        break;
                    default:
                        return {success: false, message: "Произошла неизвестная ошибка"};
                }
            }
        }
        if (message == "") message = "Активирован пустой промокод.";
        else message = "Промокод активирован. Вам начислено:" + message;
        promos.allPromos[name].activatedTimes += 1;
        data.users[userId].activatedPromos.push(name);
        fs.writeFileSync("./promos.json", JSON.stringify(promos, null, "    "));
        file.write();
        return {success: true, message};
    }
}
let game = {
    coin: function (id, stavka, or_or_re) {
        if (stavka == "#r") stavka = randomInt(1, get.get(id, "balance"));
        else if (stavka == "все" || stavka == "всё") stavka = get.get(id, "balance");
        else {
            if (isNaN(parseInt(stavka))) return {success: false, message: "Неверный параметр ставка\nИспользование: монета <ставка/всё> <орел/решка>"};
            if (stavka.slice(-1) == "%") {
                stavka = stavka.slice(0, -1);
                if (stavka > 100 || stavka < 1) return {success: false, message: "Неверное использование процентной ставки. Процент должен быть от 1 до 100"}
                stavka = Math.round(stavka / 100 * get.get(id, "balance"));
            }
            else stavka = obrabotka.kChisla(stavka);
        }
        if (stavka > get.get(id, "balance") || stavka <= 0) return {success: false, message: "Неверная ставка (меньше нуля или больше вашего баланса)"}
        if (stavka < get.get(id, "balance") / 100) return {success: false, message: "Ставка должна быть не меньше 1% от вашего баланса"};
        if (or_or_re == "#r") or_or_re = randomInt(1, 3);
        else if (or_or_re == "орел" || or_or_re == "орёл") or_or_re = 1;
        else if (or_or_re == "решка") or_or_re = 2;
        else return {success: false, message: "Использование: монета <ставка/всё> <орел/решка>"}
        let result = randomInt(1, 3);
        if (result == or_or_re) {
            data.users[id].balance += stavka;
            data.users[id].wonMoneta += stavka;
            return {success: true, message: `Вы выиграли! Ваш выигрыш: ${obrabotka.chisla(stavka)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ`};
        }
        else {
            data.users[id].balance -= stavka;
            data.users[id].wonMoneta -= stavka;
            return {success: true, message: `Вы проиграли. Проиграно ${obrabotka.chisla(stavka)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ`};
        }
    },
    // roulette: {
    //     bets: {
    //         // "1:3":      [],
    //         // "1:3(2)":   [],
    //         // "1:3(3)":   [],
    //         // "1st12":    [],
    //         // "2nd12":    [],
    //         // "3rd12":    [],
    //         // "1to18":    [],
    //         // "19to36":   [],
    //         // "even":     [],
    //         // "odd":      [],
    //         // "red":      [],
    //         // "black":    [],
    //         // 1: []
        
    //     },
    //     bet: function (id, bet, amount, client, chatId) {
    //         if (bet == "#r") bet = randomInt(0, 37);
    //         else if (["1:3", "1:3(2)", "1:3(3)", "1st12", "2nd12", "3rd12", "1to18", "19to36", "even", "odd", "red", "black"].includes(bet)) {}
    //         else {
    //             bet = Number(bet);
    //             if (isNaN(bet) || bet < 0 || bet > 36) return { success: false, message: "Неправильный парамет ставка" };
    //         }
    //         let a = Object.keys(game.roulette.bets).length;
    //         if (game.roulette.bets[bet] == undefined) game.roulette.bets[bet] = [{id, amount}];
    //         else game.roulette.bets[bet].push({id, amount});
    //         if (a == 0) game.roulette.thread();
    //         return
    //     },
    //     spin: function () {

    //     },
    //     thread: async function () {
            
    //     }
    // },
    btcBet: function (client, chatId, id, amount, bet) {
        if (amount == "#r") amount = randomInt(1, get.get(id, "balance"));
        else if (amount == "все" || amount == "всё") amount = get.get(id, "balance");
        else {
            if (isNaN(parseInt(amount))) return {success: false, message: "Неверный параметр ставка\nИспользование: бит <ставка/всё> <вверх/вниз>"};
            if (amount.slice(-1) == "%") {
                amount = amount.slice(0, -1);
                if (amount > 100 || amount < 1) return {success: false, message: "Неверное использование процентной ставки. Процент должен быть от 1 до 100"}
                amount = Math.round(amount / 100 * get.get(id, "balance"));
            }
            else amount = obrabotka.kChisla(amount);
        };
        if (amount > get.get(id, "balance") || amount <= 0) return {success: false, message: "Неверная ставка (меньше нуля или больше вашего баланса)"};
        if (["вверх", "вниз"].indexOf(bet) == -1) return {success: false, message: "Использование: бит <ставка/всё> <вверх/вниз>"};
        append.appendToUser(id, "balance", -amount);
        CLIENTS[client].send(JSON.stringify({action: "sendMessage", data: {chatId, text: `Ваша ставка ${obrabotka.chisla(amount)} КШ, ждем минуту.`}}))
        request1("https://blockchain.info/ticker", function (err, res, body) {
            if (err) {
                append.appendToUser(id, "balance", amount);
                return CLIENTS[client].sendMessage({chatId, text: "Произошла ошибка! Сообщите об этом разработчику!"});
            }
            let startPrice = JSON.parse(body).RUB.sell;
            CLIENTS[client].sendMessage({chatId, text: `Debug: startPrice = ${startPrice}`});
            setTimeout(() => {
                request1("https://blockchain.info/ticker", function (err, res, body) {
                    if (err) {
                        append.appendToUser(id, "balance", amount);
                        return CLIENTS[client].sendMessage({chatId, text: "Произошла ошибка! Сообщите об этом разработчику!"});
                    }
                    let endPrice = JSON.parse(body).RUB.sell;
                    CLIENTS[client].sendMessage({chatId, text: `Debug: endPrice = ${endPrice}`});
                    if ((startPrice < endPrice && bet == "вверх") || (startPrice > endPrice && bet == "вниз")) {
                        append.appendToUser(id, "balance", amount * 2);
                        data.users[id].wonBtcBets += amount;
                        CLIENTS[client].sendMessage({chatId, text: `Вы выиграли!\nКурс BTC изменился на ${(endPrice - startPrice).toFixed(2)} RUB.\nВаш выигрыш: ${obrabotka.chisla(amount)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ`});
                    }
                    else {
                        data.users[id].lostBtcBets += amount;
                        CLIENTS[client].sendMessage({chatId, text: `Вы проиграли.\nКурс BTC изменился на ${(endPrice - startPrice).toFixed(2)} RUB.\nПроиграно ${obrabotka.chisla(amount)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ`});
                    }
                });
            }, 60000);
        });
    }
}
let reward = {
    read: function() {
        return structuredClone(require("./rewards.json"));
    },
    write: function(data) {
        fs.writeFile("rewards.json", JSON.stringify(data, null, "    "), (err) => {if (err) console.error(err)});
    },
    check: function(reward) {
        let rewards = this.read();
        delete rewards.default;
        return reward in rewards;
    },
    list: function() {
        return Object.keys(this.read()).filter(i => i != "default");
    },
    info: function(reward) {
        let rewards = this.read();
        if (!this.check(reward)) return {success: false, message: "Такой награды не существует"};
        return `${reward}:\n${rewards[reward].name}\n${rewards[reward].description}`;
    },
    give: function(id, reward) {
        if (!this.check(reward)) return {success: false, message: "Такой награды не существует"};
        if (reward in get.get(id, "rewards")) return {success: false, message: `Награда уже была выдана ${obrabotka.vremeni(get.get(id, "rewards")[reward])}`}
        data.users[id].rewards[reward] = get.time();
        let rewards = this.read();
        rewards[reward].count += 1;
        return {success: true};
    },
    revoke: function(id, reward) {
        if (!this.check(reward)) return {success: false, message: "Такой награды не существует"};
        if (reward in get.get(id, "rewards")) return {success: false, message: "Такая награда отсутствует у пользователя"}
        delete data.users[id].rewards[reward];
        let rewards = this.read();
        rewards[reward].count -= 1;
        return {success: true};
    },
    add: function(reward, name, description) {
        if (this.check(reward)) return {success: false, message: "Такая награда уже существует"};
        let rewards = this.read();
        rewards[reward] = structuredClone(rewards.default);
        rewards[reward].name = name;
        rewards[reward].description = description;
        this.write(rewards);
        return {success: true};
    },
    remove: function(reward) {
        if (!this.check(reward)) return {success: false, message: "Такой награды не существует"};
        Object.keys(data.users).forEach(i => {
            if (reward in data.users[i].rewards) delete data.users[i].rewards[reward];
        })
        let rewards = this.read();
        delete rewards[reward];
        this.write(rewards);
        return {success: true};
    },
    infoList: function(rewards, peopleCountPercent, peopleCount) {
        if (rewards.length == 0) return "";
        let data = this.read();
        let res = "";
        rewards.forEach(i => {
            res += this.info(i);
            if (peopleCountPercent) {
                res += `\nЕсть у ${(data[i].count / get.ids().length * 100).toFixed(2)}%`;
                if (peopleCount) res += ` (${data[i].count}) пользователей\n\n`;
                else res += " пользователей\n\n"
            }
        });
        if (peopleCountPercent) return res.slice(0, -2);
        return res;
    }
}

class kmd {
    constructor(message, client, customCommand = undefined) {
        this.message = message;
        this.message_text = message.text.toLowerCase().split(" ");
        this.client = client;
        let command = message.text;
        if (customCommand) command = customCommand;
        set.lastCommand(message.from_user.id, command);
    }
    top() {
        let top = {mode: "balance", active_top: true, caller_id: this.message.from_user.id, page: 1};
        if (this.message_text[0] == "всетоп") top.active_top = false;
        if (this.message_text.length >= 2) {
            if (["клик", "к", "click"].includes(this.message_text[1])) top.mode = "click";
            else if (["сек", "с", "sec"].includes(this.message_text[1])) top.mode = "sec";
            else if (["регистрация", "р", "рег", "register", "registerTime"].includes(this.message_text[1])) top.mode = "registerTime";
            else if (["банк", "bank"].includes(this.message_text[1])) top.mode = "bank";
            else if (["д", "деньги", "money"].includes(this.message_text[1])) top.mode = "money";
            if (this.message_text.length >= 3) {
                let a = Number(this.message_text[2]);
                if (!isNaN(a)) top.page = a;
            }
        }
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: others.leaderbord(top), parseMode: "HTML"});
    }
    buyBoost(boost) {
        let id = this.message.from_user.id;
        let args = this.message_text.filter((i) => !boost.split(" ").includes(i));
        if (boost == "клик") boost = "click";
        else if (boost == "сек") boost = "sec";
        else if (["скидка", "1% скидки"].includes(boost)) boost = "sale";
        else if (boost == "банк") boost = "bankMax";
        else return CLIENTS[this.client]
        let amount = 1;
        if (args.length > 0) {
            if (["все", "всё"].includes(args[0])) amount = -1;
            else amount = args[0];
        }
        let cost = calc.boost(id, boost);
        if (cost.cost == undefined) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: cost.message});
        //^^^: Отправка пользователю сообщения об ошибке покупки по причине достижения лимита ибо cost.cost == undefined только если
        //произошло достижение лимита либо неверно выбран апгрейд
        cost = cost.cost;
        let balance = get.get(id, "balance");
        let i;
        for (i = 0; (i < amount || amount == -1) && balance >= cost && cost != undefined; i++) {
            if (boost == "bankMax") append.appendToUser(id, boost, 1000);
            else append.appendToUser(id, boost, 1);
            append.appendToUser(id, "balance", -cost);
            balance = get.get(id, "balance");
            cost = calc.boost(id, boost).cost;
        }
        if (i == 0) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Недостаточно средств. Для покупки ещё необходимо ${obrabotka.chisla(cost - balance)} КШ`});
        else {
            if (get.keyboard(this.message.chat.id, "activeKeyboard", this.message.chat.type)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Успешно куплено Успешно куплено апгрейдов: ${i}\nid: <code>${id}</code>
Апгрейды: ${get.get(id, "sec")}/сек; ${get.get(id, "click")}/клик; ${get.get(id, "sale")}% скидки
Баланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ
В банке: ${obrabotka.chisla(get.get(id, "bank"))}/ ${obrabotka.chisla(get.get(id, "bankMax"))} КШ`, parseMode: "HTML", keyboard: keyboard.upgrade(this.message.from_user.id)});

            return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Успешно куплено Успешно куплено апгрейдов: ${i}\nid: <code>${id}</code>
Апгрейды: ${get.get(id, "sec")}/сек; ${get.get(id, "click")}/клик; ${get.get(id, "sale")}% скидки
Баланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ
В банке: ${obrabotka.chisla(get.get(id, "bank"))}/ ${obrabotka.chisla(get.get(id, "bankMax"))} КШ`, parseMode: "HTML"});
        }
    }
    click() {
        let userId = this.message.from_user.id;
        accrual.click(userId);
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Коллекция кристальных шаров пополнена!\nБаланс: ${obrabotka.chisla(get.get(userId, "balance"))} КШ`});
    }
    balance() {
        let userId;
        if (this.message_text.length > 1) {
            if (this.message_text[1] == "_" && this.message.reply_to_message) userId = this.message.reply_to_message.from_user.id;
            else {
                userId = this.message_text[1];
                if (!get.id(userId)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Id не найден"});
            }
        }
        else userId = this.message.from_user.id;
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Имя: ${get.get(userId, "fullName")}\nid: \`${userId}\`\nАпгрейды: ${get.get(userId, "sec")}/сек; ${get.get(userId, "click")}/клик; ${get.get(userId, "sale")}% скидки\nБаланс: ${obrabotka.chisla(get.get(userId, "balance"))} КШ\nВ банке: ${obrabotka.chisla(get.get(userId, "bank"))}/${obrabotka.chisla(get.get(userId, "bankMax"))} КШ`, parseMode: "MARKDOWN"})
    }
    helpCommand() {
        if (this.message_text.length < 2) {
            this.message.text = "команда команда"
            return new kmd(this.message, this.client);
        }
        this.message.text = this.message.text.slice(8);
        this.message_text = this.message_text.splice(1, 1);
        let i = 0;
        let checkCommand = this.message_text[0];
        while (true) {
            if (i > 3) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Команда не найдена"});
            if (Object.keys(COMMANDS).includes(checkCommand)) {
                if (Object.keys(COMMANDS[checkCommand]).includes("link")) checkCommand = COMMANDS[checkCommand].link;
                if (COMMANDS[checkCommand].permissions == "admin" && !get.get(this.message.from_user.id, "isAdmin")) return;
                if (COMMANDS[checkCommand].permissions == "owner" && this.message.from_user.id != 357694314) return; //ВНИМАНИЕ БЛЯТЬ
                break
            }
            i++;
            if (i != this.message_text.length - 1) return;
            checkCommand += ` ${this.message_text[i]}`;
        }
        let msg = `${checkCommand} `;
        if (Object.keys(COMMANDS[checkCommand]).includes("links")) COMMANDS[checkCommand].links.forEach((i) => msg += `/ ${i} `);
        msg = msg.slice(0, -1) + `: ${COMMANDS[checkCommand].description}\nИспользование: ${COMMANDS[checkCommand].usage}`;
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: msg});
    }
    sendUser() {
        if (this.message_text.length < 2) {
            this.message.text = "команда " + this.message.text;
            new kmd(this.message, this.client).helpCommand();
        }
        let from = this.message.from_user.id;
        let to;
        if (this.message_text[1] == "_" && this.message.reply_to_message) to = this.message.reply_to_message.from_user.id;
        else {
            to = this.message_text[1];
            if (!get.id(to)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Id не найден"});
        }
        let type;
        if (this.message_text[0] == "послать") type = "normal";
        else if (this.message_text[0] == "послатьанон") type = "anonymous";
        let cost = {
            normal: 1_000_000,
            anonymous: 3_000_000
        };
        if (get.get(from, "balance") < cost[type]) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Недостаточно средств"});
        append.appendToUser(from, "balance", -cost[type]);
        data.users[from].othersSpends += cost[type];
        if (type == "anonymous") {
            CLIENTS[get.get(to, "receiver")].sendMessage({chatId: to, text: "Вас анонимно послали нахуй"});
            return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Вы анонимно послали нахуй игрока ${get.get(to, "fullName")} (${to})\nЗабрано ${obrabotka.chisla(cost[type])} КШ`});
        }
        else if (type == "normal") {
            CLIENTS[get.get(to, "receiver")].sendMessage({chatId: to, text: `Вас послал нахуй пользователь ${get.get(from, "fullName")} (${from})`});
            return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Вы послали нахуй игрока ${get.get(to, "fullName")} (${to})\nЗабрано ${obrabotka.chisla(cost[type])} КШ`});
        }
    }
    backup() {
        if (this.message_text.length < 2 || this.message_text[1] != "создать") {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let name = `backup-${dateFormat(get.time()*1000, "yyyy-mm-dd_HH.MM.ss")}.json`;
        fs.copyFileSync("usrs.json", `backups/${name}`);
        (async () => {
            try {
                const { href, method } = await upload.link(config.tokens.yadisk, `disk:/kkh_backups/${name}`, true);
                const fileStream = fs.createReadStream(`backups/${name}`);
                const uploadStream = request({ ...parse(href), method });
                fileStream.pipe(uploadStream);
                fileStream.on('end', () => uploadStream.end());
                CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Бэкап успешно выполнен и выгружен в облако!"});
            }
            catch (err) {
                CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `При выгрузке бэкапа возникла ошибка:\n${err}`});
            }
        })();
    }
    dbWrite() {
        fs.copyFileSync("usrs.json", `backups/${`backup-${dateFormat(get.time()*1000, "yyyy-mm-dd_HH.MM.ss")}.json`}`);
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "БД записана"});
    }
    commandsList() {
        let userId = this.message.from_user.id;
        let commands = [];
        if (userId == 357694314) Object.keys(COMMANDS).forEach((i) => {
            if (!COMMANDS[i].link) commands.push([i, COMMANDS[i].description]);
        });
        else if (get.get(userId, "isAdmin")) Object.keys(COMMANDS).forEach((i) => {
            if (COMMANDS[i].permissions != "owner" && !COMMANDS[i].link) commands.push([i, COMMANDS[i].description]);
        });
        else Object.keys(COMMANDS).forEach((i) => {
            if (COMMANDS[i].permissions == "user" && !COMMANDS[i].link) commands.push([i, COMMANDS[i].description]);
        });
        let msg = "";
        commands.forEach((i) => {
            msg += `${i[0].charAt(0).toUpperCase() + i[0].slice(1)}: ${i[1]}\n`
        });
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: msg});
    }
    bonus() {
        let res = give.bonus(this.message.from_user.id);
        if (res.success) CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.data});
        else CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    bonus2() {
        let res = give.bonus2(this.message.from_user.id);
        if (res.success) CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.data});
        else CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    resetId() {
        if (this.message_text.length == 1 || (this.message_text.length > 1 && this.message_text[1] == "справка")) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Обнуляет прогресс и вы начинаете игру заново.\nЧтобы сбросить прогресс, введите `сброс подтвердить`"});
        let toReset = 0;
        let type = 0;
        if (this.message_text[1] == "подтвердить") {
            toReset = this.message.from_user.id;
            type = 0;
        }
        else {
            if (!get.get(this.message.from_user.id, "isAdmin")) {
                this.message.text = "команда " + this.message.text;
                return new kmd(this.message, this.client).helpCommand();
            }
            toReset = this.message_text[1];
            if (toReset == "_" && this.message.reply_to_message) toReset = this.message.reply_to_message.from_user.id;
            if (!get.id(toReset)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Пользователя ${toReset} не существует`});
            if (get.get(toReset, "isAdmin") && this.message.from_user.id != 357694314) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Невозможно сбросить прогресс этого пользователя"});
            type = 1;
        }
        for (let i in data.users[toReset]) if (!data.doNotClear.includes(i)) data.users[toReset][i] = structuredClone(data.users.default[i]); //ВНИМАНИЕ БЛЯТЬ удаляется default при сбросе пофиксить
        if (type == 0) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Ваш прогресс сброшен!"});
        CLIENTS[get.get(toReset, "receiver")].sendMessage({chatId: toReset, text: "Ваш прогресс сброшен администратором!"});
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Прогресс пользователя ${get.get(toReset, "fullName")} (\`${toReset}\`) успешно сброшен!`})
    }
    pay() {
        if (this.message_text.length < 3) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let from = this.message.from_user.id;
        let to;
        if (this.message_text[2] == "_" && this.message.reply_to_message) to = this.message.reply_to_message.from_user.id;
        else {
            to = this.message_text[2];
            if (!get.id(to)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Id не найден"});
        }
        let comment;
        if (this.message_text.length > 3) comment = this.message.text.split(" ").slice(3).join(" ");
        let res = others.pay(from, to, this.message_text[1], comment);
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    price() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let upgrade = this.message.text.slice(5).replace("+", "");
        if (upgrade == "клик") upgrade = "click";
        else if (upgrade == "сек") upgrade = "sec";
        else if (["скидка", "скидки"].includes(upgrade)) upgrade = "sale";
        else if (["банк", "+банк"].includes(upgrade)) upgrade = "bankMax";
        if (!["click", "sec", "sale", "bankMax"].includes(upgrade)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Неверный апгрейд"});
        let res = calc.boost(this.message.from_user.id, upgrade);
        if (res.success) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.data});
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    set() {
        if (this.message_text.length < 4) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let value = this.message_text[3];
        let toSet = this.message.text.split(" ")[2];
        let to;
        if (this.message_text[1] == "_" && this.message.reply_to_message) to = this.message.reply_to_message.from_user.id;
        else {
            to = this.message_text[1];
            if (!get.id(to)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Id не найден"});
        }
        if (value == "true") value = true;
        else if (value == "false") value = false;
        if (["isAdmin", "mails", "timeLastBonus", "keyboard", "activeKeyboard", "receiver"].indexOf(toSet) != -1 && this.message.from_user.id != 357694314) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Недостаточно прав"});
        let ret, msg1, msg2;
        if (value == "reward" && ["-", "+"].includes(value[0])) {
            // TODO
        }
        else {
            if (typeof value == "string" && ["-", "+"].includes(value[0])) ret = append.appendToUser(to, toSet, value);
            else ret = set.set(to, toSet, value);
            if (!ret.success) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: ret.message});
            msg1 = `Вам установлено ${value} значение ${toSet} администратором`;
            msg2 = `Пользователю ${get.get(to, "fullName")} установлено ${value} значение ${toSet}`;
        }
        if (msg1 && msg2) {
            CLIENTS[get.get(to, "receiver")].sendMessage({chatId: to, text: msg1});
            CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: msg2});
        }
    }
    coin() {
        if (this.message_text.length < 3) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let bet = this.message_text[1];
        let side = this.message_text[2];
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: game.coin(this.message.from_user.id, bet, side).message});
    }
    bankTransfer() {
        let action;
        let value = -1;
        if (this.message_text[0] == "-банк") action = "take";
        else if (this.message_text[0] == "банк") {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        if (this.message_text.length > 1) value = this.message_text[1];
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: others.bankTransfer(this.message.from_user.id, action, value).message});
    }
    mailing() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let state;
        if (this.message_text[1] == "да") state = true;
        else if (this.message_text[1] == "нет") state = false;
        if (state != undefined) {
            let res = set.set(this.message.from_user.id, "mails", state);
            if (!res.success) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
            if (state) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Рассылка включена.\nДля отключения введите рассылка нет"});
            return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Рассылка отключена.\nДля включения введите рассылка да"});
        }
        else if (this.message_text[1] == "создать") {
            if (!get.get(this.message.from_user.id, "isAdmin")) return;
            if (this.message_text.length < 3) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Использование: рассылка создать <текст>"});
            let text = this.message.text.split(" ").slice(2).join(" ");
            text += "\n\n____\nДля отключения рассылки введите рассылка нет";
            for (let i of get.ids()) {
                if (get.get(i, "mails") && i != "default") CLIENTS[get.get(i, "receiver")].sendMessage({chatId: i, text});
            }
            CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Рассылка отправлена"});
        }
    }
    promoList() {
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: promo.list().message});
    }
    promoInfo() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let promoName = this.message.text.split(" ").slice(1).join(" ");
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: promo.info(promoName).message});
    }
    promoFullInfo() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let promoName = this.message.text.split(" ").slice(1).join(" ");
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: promo.fInfo(promoName).message});
    }
    promoDelete() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let promoName = this.message.text.split(" ").slice(1).join(" ");
        let res = promo.delete(promoName);
        if (res.success) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Промокод удален"});
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    promoAdd() {
        if (this.message_text.length < 5) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let a = this.message.text.split("{", 2);
        let b = a[1].split("}", 2);
        let c = b[1].slice(1).split(" ");
        let paramsObj;
        try {paramsObj = JSON.parse(`{${b[0]}}`.replaceAll("'", '"'))}
        catch (e) {return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text:`Произошла ошибка, попробуйте ещё раз!\n${e}`})}
        let res = promo.add(this.message_text[1], paramsObj, c[0], c[1]);
        if (res.success) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Промокод успешно добавлен"});
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    promoActivate() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let res = promo.activate(this.message.from_user.id, this.message.text.slice(this.message.text.indexOf(" ") + 1));
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    keyboardSet() {
        if (this.message_text.length < 2 || !["да", "нет"].includes(this.message_text[1])) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let state;
        if (this.message_text[1] == "да") state = true;
        else if (this.message_text[1] == "нет") state = false;
        let type = this.message.chat.type;
        let res = set.keyboard.passive(this.message.chat.id, type, state);
        if (!res) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
        if (state) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Клавиатура включена", keyboard: keyboard.mainMenu});
        set.keyboard.active(this.message.chat.id, type, false);
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Клавиатура отключена", keyboard: -1});
    }
    getUserInfo() {
        let userId;
        if (this.message_text.length < 2) userId = this.message.from_user.id;
        else if (this.message_text[1] == "_" && this.message.reply_to_message) userId = this.message.reply_to_message.from_user.id;
        else userId = this.message_text[1];
        if (!get.id(userId)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Id ${userId} не найден`});
        let res = get.data(userId);
        if (res.success == false) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: JSON.stringify(res, null, "    ")});
    }
    dotValue() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: obrabotka.chisla(this.message_text[1])});
    }
    admin() {
        let res = get.get(this.message.from_user.id, "isAdmin");
        if (res) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Вы админ"});
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Вы не админ"});
    }
    removeId() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let userId;
        if (this.message_text[1] == "_" && this.message.reply_to_message) userId = this.message.reply_to_message.from_user.id;
        else userId = this.message_text[1];
        if (!get.id(userId)) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Id ${userId} не найден`});
        if (get.get(userId, "isAdmin")) CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Невозможно удалить администратора"});
        delete data.users[userId];
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Пользователь успешно удален"});
    }
    usersList() {
        let text = "";
        let ids = get.ids();
        ids.forEach(i => {
            text += `${get.get(i, "fullName")} (${i})\n`
        });
        return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: `Вот список всех ${ids.length} пользователей:\n${text.slice(0, -1)}`});
    }
    btcBet() {
        if (this.message_text.length < 3) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let res = game.btcBet(this.client, this.message.chat.id, this.message.from_user.id, this.message_text[1], this.message_text[2]);
        if (!res.success) CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
    }
    upgrades() {
        let type = this.message.chat.type;
        let keyboardState = get.keyboard(this.message.chat.id, "keyboard", type);
        if (!keyboardState) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Открыто меню апгрейдов"});
        set.keyboard.active(this.message.chat.id, type, true);
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Открыто меню апгрейдов", keyboard: keyboard.upgrade(this.message.from_user.id)});
    }
    backKeyboardMenu() {
        let type = this.message.chat.type;
        if (get.keyboard(this.message.chat.id, "activeKeyboard", type)) {
            set.keyboard.active(this.message.chat.id, type, false);
            CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Вы вышли из меню", keyboard: keyboard.mainMenu});
        }
        else CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Вы вышли из меню"});
    }
    rewardAdd() {
        if (this.message_text.length < 5 || !this.message_text.includes("||")) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let emoji = this.message_text[1];
        let a = this.message.text.split(" || ");
        if (a.length > 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let name = a[0].split(" ").slice(2).join(" ");
        let description = a[1];
        let res;
        if (emoji && name && description) res = reward.add(emoji, name, description);
        else {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        if (!res.success) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Награда успешно добавлена"});
    }
    rewardRemove() {
        if (this.message_text.length < 2) {
            let text = this.message.text;
            this.message.text = "команда " + this.message.text;
            return new kmd(this.message, this.client, text).helpCommand();
        }
        let res = reward.remove(this.message_text[1]);
        if (!res.success) return CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: res.message});
        CLIENTS[this.client].sendMessage({chatId: this.message.chat.id, text: "Награда успешно удалена"});
    }
}
let others = {
    leaderbord: function ({mode, active_top, caller_id, page}) {
        let lb_data = data;
        let inverse;
        let sorted = [];
        delete lb_data.users["default"];
        inverse = mode == "registerTime";
        for (key in lb_data.users) {
            if (active_top && get.time() - lb_data.users[key].timeLastCommand > 181440000) delete lb_data.users[key]
            else {
                if (mode != "money") sorted.push([key, lb_data.users[key][mode]])
                else sorted.push([key, lb_data.users[key]["balance"] + lb_data.users[key]["bank"]])
            }
        }
        if (Object.keys(lb_data.users).length == 0) return {success: false, message: "Активных пользователей нет :("}
        for (let i = 0; i < Object.keys(lb_data.users).length - 1; i++) {
            for (let j = 0; j < Object.keys(lb_data.users).length - 1; j++) {
                if ((!inverse && sorted[j][1] < sorted[j + 1][1]) || (inverse && sorted[j][1] > sorted[j + 1][1])) {
                    let tmp = sorted[j]
                    sorted[j] = sorted[j + 1]
                    sorted[j + 1] = tmp
                }
            }
        }
        let top = [];
        let caller_place = 0;
        let place = 1;
        let to_append = [];
        for (let i = 0; i < Object.keys(lb_data.users).length; i++) {
            to_append = [place, sorted[i][0], get.get(sorted[i][0], "fullName")];
            if (to_append[1] == caller_id) caller_place = place - 1
            if (i != 0) {
                if (sorted[i - 1][1] == sorted[i][1]) {
                    to_append[0] = top[i - 1][0];
                    place--
                }
            }
            top.push(to_append)
            place++
        }
        let msg = ""
        let start_user = 0
        let end_user = 0
        if (page == 2281337) {
            msg = "Ты нахуй страницу отладки открыл а\n"
            msg += "\n"
            start_user = 0
            end_user = top.length
        }
        if (active_top) msg += "Топ активных пользователей (для общего топа есть команда \"всетоп\")\n"
        else msg += "Топ всех пользователей (для топа активных есть команда \"топ\")\n"
        //стандартное расположение значений топа
        let order = ["balance", "sec", "click"] 
        let order_words = [" КШ", "/сек", "/клик"]
        if (page != 2281337) {
            start_user = (page - 1) * 10
            end_user = page * 10
        }
        if (top.length == 0) return {success: false, message: "Активных пользователей нет :("}
        else if ((page <= 0 || start_user >= top.length) && page != 2281337) return "Неверная страница"
        if (end_user >= top.length) end_user = top.length
        if (mode == "money") { //акак какать
            order = ["", "balance", "bank"]
            order_words = [" всего", " КШ", " КШ в банке"]
        } else if (mode == "bank") { //в банке знаешь типо
            order = ["bank", "balance", "sec", "click"]
            order_words = [" КШ в банке", " КШ", "/сек", "/клик"]
        } else if (mode == "registerTime") {
            order = ["registerTime", "balance"]
            order_words = ["", " КШ"]
        } else { //вынос значения топа вперёд (обычные)
            let index = order.indexOf(mode)
            order.splice(index, 1)
            order.unshift(mode)
            let w = order_words[index]
            order_words.splice(index, 1)
            order_words.unshift(w)
        }
        //пошёл нахуй Баланс | Клик | Сек | Буст баланса | Регистрация | Банк | Деньги
        let highlights_names = ["Баланс", "Клик", "Сек", "Регистрация", "Банк", "Деньги"]
        let highlights_pos = {"balance": 0, "click": 1, "sec": 2, "registerTime": 3, "bank": 4, "money": 5}
        msg += "|"
        let highlight_pos = highlights_pos[mode]
        for (i = 0; i < highlights_names.length; i++) {
            msg += " "
            if (i == highlight_pos) msg += "("
            msg += highlights_names[i]
            if (i == highlight_pos) msg += ")"
            msg += " |"
        }
        msg += "\n\n"
        if (mode == "money") {
            for (let user = start_user; user < end_user; user++) msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[user][1]][order[2]])}/${obrabotka.chisla(data.users[top[user][1]]["bankMax"])}${order_words[2]}\n`
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${top[caller_place][2]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[2]])}/${obrabotka.chisla(data.users[top[caller_place][1]]["bankMax"])}${order_words[2]}\n`
        
        }
        else if (mode == "bank") {
            for (let user = start_user; user < end_user; user++) msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${obrabotka.chisla(data.users[top[user][1]][order[0]])}/${obrabotka.chisla(data.users[top[user][1]]["bankMax"])}${order_words[0]}, ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}, ${data.users[top[user][1]][order[2]]}${order_words[2]}, ${data.users[top[user][1]][order[3]]}${order_words[3]}\n`
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${data.users[top[caller_place][1]][order[0]]}/${obrabotka.chisla(data.users[top[caller_place][1]]["bankMax"])}${order_words[0]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[2]])}${order_words[2]}, ${data.users[top[caller_place][1]][order[3]]}${order_words[3]}\n`
        }
        else if (mode == "registerTime") {
            for (let user = start_user; user < end_user; user++) msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${obrabotka.vremeni(data.users[top[user][1]][order[0]])}${order_words[0]}, ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}\n`
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${obrabotka.vremeni(data.users[top[caller_place][1]][order[0]])}${order_words[0]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}\n`
    
        }
        else {
            for (let user = start_user; user < end_user; user++) {
                msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${obrabotka.chisla(data.users[top[user][1]][order[0]])}${order_words[0]}, ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[user][1]][order[2]])}${order_words[2]}\n`
            }
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${obrabotka.chisla(data.users[top[caller_place][1]][order[0]])}${order_words[0]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[2]])}${order_words[2]}\n`
        }
        msg += `\nСтраница ${page} из ${Math.ceil(top.length / 10)}`
        return msg
    },
    pay: function(from, to, amount, comment = undefined) {
        if (amount == "#r") amount = randomInt(1, get.get(from, "balance"));
        else if (amount.slice(-1) == "%") {
            amount = obrabotka.kChisla(amount.slice(0, -1));
            if (isNaN(amount)) return {success: false, message: "Неверный тип суммы\nИспользование: перевод <сумма> <id получателя> [комментарий]"};
            if (!(amount >= 1 && amount <= 100)) return {success: false, message: "Неверное использование процентного перевода.\nИспользование: перевод <1%-100%> <id получателя> [комментарий]"};
            amount = Math.round(get.get(from, "balance") * amount / 100);
        }
        else if (["все", "всё"].indexOf(amount) != -1) amount = get.get(from, "balance")
        else {
            amount = obrabotka.kChisla(amount);
            if (isNaN(amount)) return {success: false, message: "Неверное значение параметра суммы\nИспользование: перевод <сумма> <id получателя> [комментарий]"};
        }
        if (to == "#r") {
            keys = Object.keys(data.users);
            to = keys[randomInt(0, keys.length)];
            delete keys;
        }
        if (amount < 100) return {success: false, message: "Переводы меньше 100 КШ запрещены"}
        if (amount > get.get(from, "balance")) return {success: false, message: "Недостаточно средств"}
        append.appendToUser(from, "balance", -amount);
        data.users[from].paidKkh += amount;
        append.appendToUser(to, "balance", amount);
        data.users[to].receivedKkh += amount;
        if (comment) {
            CLIENTS[get.get(to, "receiver")].sendMessage({chatId: to, text: `Получен перевод ${obrabotka.chisla(amount)} КШ от пользователя ${get.get(from, "fullName")} (${from})\nСообщение: ${comment}`});
            return {success: true, message: `Перевод ${obrabotka.chisla(amount)} КШ пользователю ${get.get(to, "fullName")} (${to}) выполнен успешно!\nКомментарий к переводу: ${comment}`};
        }
        else {
            CLIENTS[get.get(to, "receiver")].sendMessage({chatId: to, text: `Получен перевод ${obrabotka.chisla(amount)} КШ от пользователя ${get.get(from, "fullName")} (${from})`});
            return {success: true, message: `Перевод ${obrabotka.chisla(amount)} КШ пользователю ${get.get(to, "fullName")} (${to}) выполнен успешно!`};
        }
    },
    bankTransfer: function(id, action, value = -1) {
        let fee = 0.2//% (комиссия)
        if (value == "#r") value = randomInt(1, get.get(id, "balance"))
        else if (value == "все" || value == "всё" || value == -1) {
            if (action == "take") value = get.get(id, "bank")
        }
        else {
            if (isNaN(parseInt(value))) return {success: false, message: "Неверный параметр суммы\nИспользование: -банк [сумма]"};
            if (value.slice(-1) == "%") {
                value = value.slice(0, -1);
                if (value > 100 || value < 1) return {success: false, message: "Неверное использование процентного числа. Процентное число должно быть не менее 1 и не более 100% от вашего баланса!"}
                value = Math.round(value / 100 * get.get(id, "balance"));
            }
            else value = obrabotka.kChisla(value);
        }
        if ((action == "take" && value > get.get(id, "bank")) || value <= 0) return {success: false, message: "Неверное значение (меньше нуля или больше баланса в банке)"}
        
        let feeSum = Math.round(value*fee/100)
        if (!get.get(id)) return {success: false, message: "Id не найден"}
        if (action == "take") {
            append.appendToUser(id, "bank", -value);
            append.appendToUser(id, "balance", value-feeSum);
            data.users[id].paidKkh += feeSum;
            return {success: true, message: `Выведено ${obrabotka.chisla(value-feeSum)} КШ из банка\nКомиссия ${obrabotka.chisla(feeSum)} КШ (${fee}%)\nВ банке: ${obrabotka.chisla(get.get(id, "bank"))}/ ${obrabotka.chisla(get.get(id, "bankMax"))} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance"))} КШ`};

        }
    }
}

let onSchedule = {  
    // coinLottery: {
    //     main: function () {
    //         let lastWeekCoinSum = data.sharedData.weeklyData.lostCoin - data.sharedData.weeklyData.winCoin;
    //         data.sharedData.weeklyData.winCoin = 0;
    //         data.sharedData.weeklyData.lostCoin;
    //         for (let i of Object.keys(data.users)) {
    //             data.sharedData.weeklyData.winCoin += data.users[i].wonMoneta;
    //             data.sharedData.weeklyData.lostCoin += data.users[i].lostMoneta;
    //         }
    //         let thisWeekCoinSum = data.sharedData.weeklyData.lostCoin - data.sharedData.weeklyData.winCoin - lastWeekCoinSum;
    //         if (thisWeekCoinSum <= 0) return;
    //         for (let i of [0.3, 0.25, 0.2, 0.15, 0.1]) {
    //             let id = this.chooseNewWinner(604800);
    //             sum = Number(thisWeekCoinSum * i);
    //             append.appendToUser(id, "balance", sum);
    //             // TODO: try: bot.send_message(id, f"Поздравляем!\nВы выиграли в еженедельном конкурсе {rec_file.ob_chisla(sum)} КШ!\nБаланс: {rec_file.ob_chisla(rec_file.get_balance(id, data.} КШ"   .       }
    //         }

    //     },
    //     chooseNewWinner: function (timeLastActivity) {
    //         timeLastActivity = Number(timeLastActivity);
    //         if (isNaN(timeLastActivity)) return;
    //         let winnerId = choose(Object.keys(data.users));
    //         if (winnerId != "default" && (get.time() - data.users[winnerId].timeLastCommand) < timeLastActivity && !isNaN(winnerId)) return Number(winnerId);
    //         return this.chooseNewWinner(timeLastActivity);
    //     }
    // }
}

const jobs = [
    // schedule.scheduleJob({hour: 0, minute: 0, dayOfWeek: 1}, () => onSchedule.coinLottery()),
    setInterval(() => {
        let name = `backup-${dateFormat(get.time()*1000, "yyyy-mm-dd_HH.MM.ss")}.json`;
        fs.copyFileSync("usrs.json", `backups/${name}`);
        (async () => {
            try {
                const { href, method } = await upload.link(config.tokens.yadisk, `disk:/kkh_backups/${name}`, true);
                const fileStream = fs.createReadStream(`backups/${name}`);
                const uploadStream = request({ ...parse(href), method });
                fileStream.pipe(uploadStream);
                fileStream.on('end', () => uploadStream.end());
            }
            catch (err) {
                console.log(err);
            }
        })();
    }, 1000 * 60 * 60 * 2),
    schedule.scheduleJob("*/1 * * * * *", () => accrual.sec())
]