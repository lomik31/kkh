const { randomInt } = require('crypto');
const fs = require('fs');
const schedule = require('node-schedule');
const data = require('./usrs.json');
const config = require("./config.json");
const http = require("http");
const { request } = require('https');
const { parse } = require('url');
const { upload } = require("ya-disk");
const express = require( "express");
const WebSocket = require("ws");
const { getTime } = require('date-fns');
const app = express();
const server = http.createServer(app);
const webSocketServer = new WebSocket.Server({ server });
const request1 = require('request');

let CLIENTS = {};
webSocketServer.on('connection', (ws, req) => {
    ws.on('message', m => dispatchEvent(m, ws));
    let name = req.url.replace('/?client=', '');
    CLIENTS[name] = ws;
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
    if (json.action && json.id && json.action.function) {
        let data;
        console.log(json);
        if (json.action.args) {
            if (typeof json.action.args == "object") data = eval(json.action.function)(...json.action.args)
            else data = eval(json.action.function)(json.action.args)
        }
        else if (json.action.function == "backup") return eval(json.action.function)(ws, json.id)
        else data = eval(json.action.function)()
        data.id = json.id;
        ws.send(JSON.stringify(data))
    }
    else if (json.action == "test" && json.data) {
        console.log("your data is", json.data);
        data = randomNumber()
        data.id = json.id
        ws.send(JSON.stringify(data))
    }
    else console.log(json);
}
server.listen(3200, () => console.log("Server started"))


function choose(choices) {
    return choices[Math.floor(Math.random() * choices.length)];
}


let accrual = {
    sec: function () {
        for(i in data.users) {
            data.users[i].balance += data.users[i].sec;
            data.users[i].earnedKkh += data.users[i].sec;
        };
        file.write();
    },
    click: function (userId) {
        data.users[userId].balance += data.users[userId].click;
        data.users[userId].earnedKkh += data.users[userId].click;
    },
    balanceBoost: function () {
        for(i in data.users) {
            data.users[i].balance += data.users[i].balance * (data.users[i].balanceBoost / 100);
            data.users[i].earnedKkh += data.users[i].balance * (data.users[i].balanceBoost / 100);
        }
    },
    bank: function() {
        let getRandomFloat = function (min, max) {
            const str = (Math.random() * (max - min) + min);
            return parseFloat(str);
        }
        for (let i of Object.keys(data.users)) {
            let add = Math.round(data.users[i].bank * getRandomFloat(0.0002, 0.001466666666666667));
            data.users[i].bank += add;
            data.users[i].earnedKkh += add;
        }
    }
}
function removeId(toRemove) {
    if (!get.id(toRemove).data) return {success: false, message: `Пользователя ${toRemove} не существует`}
    delete data.users[toRemove];
    return {success: true}
}
function resetId(toReset, type, id = 0) {
    if (!get.id(toReset).data) return {success: false, message: `Пользователя ${toReset} не существует`}
    if (type == 1) {}
    else if (type == 2 && get.get(toReset, "isAdmin").data && id != 357694314) return {success: false, message: "Невозможно сбросить прогресс этого пользователя"}
    for (i in data.users[toReset]) if (data.doNotClear.indexOf(i) === -1) data.users[toReset][i] = data.users.default[i]; //ВНИМАНИЕ БЛЯТЬ удаляется default при сбросе пофиксить
    return {success: true}
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
            if (get.id(appendId).data) return {success: false, message: `Пользователь ${appendId} уже существует`} 
            data.users[appendId] = data.users.default;
            console.log(data.users[appendId]);
            data.users[appendId].firstName = firstName;
            data.users[appendId].registerTime = get.time();
            if (lastName != null) data.users[appendId].lastName = lastName;
            return {success: true}
        }
        else if (appendId in data.groups) return {success: false, message: `Группа ${appendId} уже существует`} 
        data.groups[appendId] = data.groups.default;
        return {success: true}
    },
    appendToUser: function (userId, toAppend, appendAmount) {
        let appendVariables = ["balance", "click", "sec", "sale", "balanceBoost", "lastCommand", "bank"];
        if (appendVariables.indexOf(toAppend) === -1) return {success: false, message: `Параметр ${toAppend} не найден`};
        appendAmount = obrabotka.kChisla(appendAmount);
        if (typeof data.users[userId][toAppend] != typeof appendAmount || isNaN(appendAmount)) return {success: false, message: "Ошибка типа"};
        if (toAppend === "lastCommand") {
            data.users[userId][toAppend] = appendAmount;
            data.users[userId]["timeLastCommand"] = get.time();
        }
        else if (toAppend == "sale") data.users[userId][toAppend] -= appendAmount
        else data.users[userId][toAppend] += appendAmount;
        return {success: true}
    }
}
let get = {
    get: function (id, toGet) {
        let getValues = ["balance", "click", "sec", "balanceBoost", "keyboard", "sale", "isAdmin",
        "activeKeyboard", "mails", "timeLastBonus", "timeLastSecondBonus", "lastCommand", "bank",
        "multiplier", "receiver"]
        if (!get.id(id).data) return {success: false, message: "Неверный пользователь"};
        if (toGet == "all") return {success: true, data: data.users[id]}
        else if (toGet == "fullName") {
            let name = data.users[id]["firstName"];
            if (data.users[id]["lastName"] !== null) name += ` ${data.users[id]["lastName"]}`;
            return {success: true, data: name};
        }
        else if (toGet == "sale") return {success: true, data: 100 - data.users[id][toGet]};
        if (getValues.indexOf(toGet) == -1) return {success: false, message: "Данный параметр не найден"};
        let toReturn = data.users[id][toGet];
        return {success: true, data: toReturn, id};
        
    },
    ids: function () {
        let ids = Object.keys(data.users);
        ids.splice(ids.indexOf('default'), 1);
        return {success: true, data: ids};
    },
    id: function (id, type = "private") {
        if (type == "private" && id in data.users) return {success: true, data: true}
        if (id in data.groups) return {success: true, data: true} 
        return {success: true, data: false}
    },
    time: function () {
        return Number(Math.floor(Date.now() / 1000))
    },
    keyboardCosts: function (id) {
        if (!get.id(id)) return {success: false, message: "Id не найден"};
        let sec = obrabotka.chisla(calc.boost(id, "sec").cost);
        let click = obrabotka.chisla(calc.boost(id, "click").cost);
        let sale = function () {
            a = calc.boost(id, "sale");
            if (a.success) return `+1% скидки (${obrabotka.chisla(a.cost)} КШ)`
            else return a.message
        }();
        let balanceBoost = function() {
            a = calc.boost(id, "balanceBoost");
            if (a.success) return `+1% баланса/день (${obrabotka.chisla(a.cost)} КШ)`
            else return a.message
        }();
        return {success: true, data: [sec, click, sale, balanceBoost]}
    },
    keyboard: function (id, keyboardType, chatType = "private") {
        if (chatType == "private") {
            d = get.get(id, keyboardType)
            if (d.success) return {success: true, data: d.data}
            return {success: false, message: d.message}
        }
        else {
            if (!get.id(id, chatType).data) return {success: false, message: "Id не найден"}
            return {success: true, data: data.groups[id][keyboardType]}
        }
    },
    data: function (id) {
        if (!get.id(id).data) return {success: false, data: "Пользователь не найден"};
        return {success: true, data: data.users[id]};
    }
}
let calc = {
    boost: function (id, boost) {
        if (boost == "click") {
            var nac_cena = 100; //изначальная цена
            var procent = 15; //процент стоимости следующего буста
            var limit = -1;
        }
        else if (boost == "sec") {
            var nac_cena = 300; //изначальная цена
            var procent = 15; //процент стоимости следующего буста
            var limit = -1;
        }
        else if (boost == "sale") {
            var nac_cena = 7500; //изначальная цена
            var procent = 15; //процент стоимости следующего буста
            var limit = 45;
        }
        else if (boost == "balanceBoost") {
            var nac_cena = 13000000; //изначальная цена
            var procent = 35; //процент стоимости следующего буста
            var limit = 10;
        }
        else return {success: false, message: "Неверный параметр boost"}
        if (!get.id(id).data) return {success: false, message: `Пользователя с id ${id} не существует`}
        let boost_level = data.users[id][boost];
        if (boost != "sale" && boost_level >= limit && limit != -1) return {success: false, message: `Достигнут максимум апгрейдов этого типа`}
        else if (boost == "sale" && 100 - boost_level >= limit) return {success: false, message: `Достигнут максимум апгрейдов этого типа`}
        let skidka = data.users[id].sale;
        if (boost == "sale") boost_level = 100 - boost_level
        // if (skidka == 0) {
        //     if (boost_level == 0) return {success: true, cost: nac_cena, data: `Цена за ${boost_level + 1} апгрейд со скидкой ${100 - skidka}%: ${obrabotka.chisla(nac_cena)} КШ`};
        //     for (let i = 0; i < boost_level; i++) nac_cena = Math.floor(nac_cena * (100 + procent) / 100);
        //     return {success: true, cost: nac_cena, data: `Цена за ${boost_level + 1} апгрейд со скидкой ${100 - skidka}%: ${obrabotka.chisla(nac_cena)} КШ`};
        // }
        // if (boost_level == 1) {
        //     nac_cena = Math.floor(nac_cena * skidka / 100);
        //     return {success: true, cost: nac_cena, data: `Цена за ${boost_level + 1} апгрейд со скидкой ${100 - skidka}%: ${obrabotka.chisla(nac_cena)} КШ`};
        // }
        for (let i = 0; i < boost_level; i++) nac_cena = Math.floor(nac_cena * (100 + procent) / 100);
        nac_cena = Math.floor(nac_cena * skidka / 100);
        return {success: true, cost: nac_cena, data: `Цена за ${boost_level + 1} апгрейд со скидкой ${100 - skidka}%: ${obrabotka.chisla(nac_cena)} КШ`};

    }
}
let keyboard = {

}
let obrabotka = {
    chisla: function (chislo_okda) {
        let t_result = ""
        let result = ""
        chislo_okda = String(chislo_okda)
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
        let t = new Date((vremya_okda + 10800) * 1000);
        let td = t.toISOString()
        return `${td.slice(8, 10)}.${td.slice(5, 7)}.${td.slice(2, 4)} ${t.getUTCHours()}:${t.getUTCMinutes()}:${t.getUTCSeconds()}`;
    },
    vremeniBonusa: function(vremya_okda) {
        let t = new Date(vremya_okda * 1000);
        return `${t.getUTCHours()}:${t.getUTCMinutes()}:${t.getUTCSeconds()}`;
    }
}
let give = {
    bonus: function (id) {
        if (get.time() - get.get(id, "timeLastBonus").data < 86400) return {success: false, message: `Ежедневный бонус уже был получен сегодня\nДо следующего бонуса: ${obrabotka.vremeniBonusa(get.get(id, "timeLastBonus").data + 86400 - get.time())}`};
        let mnoz = data.users[id].multiplier;
        let mnoz2 = 0;
        let t = get.time();
        for (let i of data.users[id].timeLast3Bonus) {
            if (t - i >= 172800) break
            t = i;
            mnoz2++;
        }
        let bonus = Math.round(get.get(id, "sec").data * 4000 + get.get(id, "click").data * 6500 + get.get(id, "balanceBoost").data * 500000 + 1.135**get.get(id, "sec").data + 1.145**get.get(id, "click").data + 1.22**get.get(id, "balanceBoost").data + 1.14**get.get(id, "sale").data) * (mnoz + mnoz2);
        append.appendToUser(id, "balance", bonus);
        data.users[id].othersProceeds += bonus;
        data.users[id].timeLastBonus = get.time();
        data.users[id].timeLast3Bonus.splice(0, 0, get.time())
        data.users[id].timeLast3Bonus = data.users[id].timeLast3Bonus.slice(0, -1)
        let msg = `Вы забрали ежедневный бонус ${obrabotka.chisla(bonus)} КШ\n`;
        if (mnoz > 1) msg += `(Стандартный множитель - x${mnoz})\n`
        if (mnoz2 > 0) msg += `(Множитель за ежедневную активность - x${mnoz2})\n`
        if (mnoz + mnoz2 > 1) msg += `Суммарный множитель - x${mnoz + mnoz2}\n`
        msg += `Баланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`
        return {success: true, data: msg};
    },
    bonus2: function (id) {
        if (get.time() - get.get(id, "timeLastSecondBonus").data < 28800) return {success: false, message: `Бонус2 можно получать каждые 8 часов\nДо следующего бонуса2: ${obrabotka.vremeniBonusa(get.get(id, "timeLastSecondBonus").data + 28800 - get.time())}`}
        let bonus = randomInt(10000, (get.get(id, "sec").data * 3600 + get.get(id, "click").data * 5400 + get.get(id, "balanceBoost").data * 500000) + 10000);
        append.appendToUser(id, "balance", bonus);
        data.users[id].othersProceeds += bonus;
        data.users[id].timeLastSecondBonus = get.time();
        return {success: true, data: 'Вы получили случайный бонус2  в размере ' + obrabotka.chisla(bonus) + ' КШ\nБаланс: ' + obrabotka.chisla(get.get(id, "balance").data) + ' КШ'};

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
        let setValues = ["isAdmin", "multiplier", "mails", "balance", "click", "sec", "sale", "balanceBoost", "bank", "timeLastBonus", "keyboard", "activeKeyboard"];
        if (setValues.indexOf(toSet) == -1) return {success: false, message: `Невозможно изменить значение ${toSet}`};
        if (["string", "number"].indexOf(typeof value) != -1) value = obrabotka.kChisla(value)
        if (typeof data.users[id][toSet] != typeof value || isNaN(value)) return {success: false, message: "Ошибка типа"};
        if (toSet == "sale") data.users[id][toSet] = 100 - value;
        else data.users[id][toSet] = value;
        return {success: true};
    },
    keyboard: {
        passive: function (id, type, state) {
            if (type == "private") {
                if (!get.id(id).data) return {success: false, message: "Неверный пользователь"};
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
                if (!get.id(id).data) return {success: false, message: "Неверный пользователь"};
                data.users[id].activeKeyboard = state;
                {success: true}
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
        return {success: true, data: msg};
    },
    fInfo: function (promo_okda) {
        let promos = require("./promos.json");
        if (!promo.check(promo_okda)) return {success: false, message: "Промокода не существует!"};
        return {success: true, data: JSON.stringify(promos.allPromos[promo_okda], null, "    "), dta: promos.allPromos[promo_okda]};
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
        return {success: true, data: `Промокод даёт: ${msg}`};
    },
    add: function (name, data, activationLimit, validity) {
        if (promo.check(name)) return {success: false, message: "Промокод уже существует"};
        delete data.validity;
        delete data.activationLimit;
        delete data.activatedTimes;
        for (let i of Object.keys(data)) if (Object.keys(promo.fInfo("default").dta).indexOf(i) == -1) return {success: false, message: "Введено недопустимое значение! Операция отменена"}
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
        console.log(promos.allPromos[name]);
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
        if (promo.fInfo(name).dta.validity < get.time() &&promo.fInfo(name).dta.validity != -1) return {success: false, message: "Истекло время активации промокода"};
        if (promo.fInfo(name).dta.activatedTimes >= promo.fInfo(name).dta.activationLimit && promo.fInfo(name).dta.activationLimit != -1) return {success: false, message: "Превышено число активаций промокода"};
        let promos = require("./promos.json");
        let message = "";
        let value;
        for (let i of Object.keys(promos.allPromos[name])) {
            if (["activationLimit", "activatedTimes", "validity"].indexOf(i) != -1) continue;
            if (i != "sale") data.users[userId][i] += promos.allPromos[name][i];
            else if (data.users[userId][i] < 100) data.users[userId][i] -= promos.allPromos[name][i];
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
        return {success: true, data: message};
    }
}
let game = {
    coin: function (id, stavka, or_or_re) {
        if (stavka == "#r") stavka = randomInt(1, get.get(id, "balance").data);
        else if (stavka == "все" || stavka == "всё") stavka = get.get(id, "balance").data;
        else {
            if (isNaN(parseInt(stavka))) return {success: false, message: "Неверный параметр ставка\nИспользование: монета <ставка/всё> <орел/решка>"};
            if (stavka.slice(-1) == "%") {
                stavka = stavka.slice(0, -1);
                if (stavka > 100 || stavka < 1) return {success: false, message: "Неверное использование процентной ставки. Процент должен быть от 1 до 100"}
                stavka = Math.round(stavka / 100 * get.get(id, "balance").data);
            }
            else stavka = obrabotka.kChisla(stavka);
        }
        if (stavka > get.get(id, "balance").data || stavka <= 0) return {success: false, message: "Неверная ставка (меньше нуля или больше вашего баланса)"}
        if (or_or_re == "#r") or_or_re = randomInt(1, 3);
        else if (or_or_re == "орел" || or_or_re == "орёл") or_or_re = 1;
        else if (or_or_re == "решка") or_or_re = 2;
        else return {success: false, message: "Использование: монета <ставка/всё> <орел/решка>"}
        let result = randomInt(1, 3);
        if (result == or_or_re) {
            data.users[id].balance += stavka;
            data.users[id].wonMoneta += stavka;
            return {success: true, data: `Вы выиграли! Ваш выигрыш: ${obrabotka.chisla(stavka)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`};
        }
        else {
            data.users[id].balance -= stavka;
            data.users[id].wonMoneta -= stavka;
            return {success: true, data: `Вы проиграли. Проиграно ${obrabotka.chisla(stavka)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`};
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
        if (!get.id(id).data) return {success: false, message: "Id не найден"};
        if (amount == "#r") amount = randomInt(1, get.get(id, "balance").data);
        else if (amount == "все" || amount == "всё") amount = get.get(id, "balance").data;
        else {
            if (isNaN(parseInt(amount))) return {success: false, message: "Неверный параметр ставка\nИспользование: бит <ставка/всё> <вверх/вниз>"};
            if (amount.slice(-1) == "%") {
                amount = amount.slice(0, -1);
                if (amount > 100 || amount < 1) return {success: false, message: "Неверное использование процентной ставки. Процент должен быть от 1 до 100"}
                amount = Math.round(amount / 100 * get.get(id, "balance").data);
            }
            else amount = obrabotka.kChisla(amount);
        };
        if (amount > get.get(id, "balance").data || amount <= 0) return {success: false, message: "Неверная ставка (меньше нуля или больше вашего баланса)"};
        if (["вверх", "вниз"].indexOf(bet) == -1) return {success: false, message: "Использование: бит <ставка/всё> <вверх/вниз>"};
        let error;
        append.appendToUser(id, "balance", -amount);
        CLIENTS[client].send(JSON.stringify({action: "sendMessage", data: {chatId, text: `Ваша ставка ${obrabotka.chisla(amount)} КШ, ждем минуту.`}}))
        request1("https://blockchain.info/ticker", function (err, res, body) {
            if (err) return error = err;
            let startPrice = JSON.parse(body).RUB.sell;
            CLIENTS[client].send(JSON.stringify({action: "sendMessage", data: {chatId, text: `Debug: startPrice = ${startPrice}`}}));
            setTimeout(() => {
                request1("https://blockchain.info/ticker", function (err, res, body) {
                    if (err) return error = err;
                    let endPrice = JSON.parse(body).RUB.sell;
                    CLIENTS[client].send(JSON.stringify({action: "sendMessage", data: {chatId, text: `Debug: endPrice = ${endPrice}`}}));
                    if ((startPrice < endPrice && bet == "вверх") || (startPrice > endPrice && bet == "вниз")) {
                        append.appendToUser(id, "balance", amount * 2);
                        data.users[id].wonBtcBets += amount;
                        CLIENTS[client].send(JSON.stringify({action: "sendMessage", data: {chatId, text: `Вы выиграли!\nКурс BTC изменился на ${(endPrice - startPrice).toFixed(2)} RUB.\nВаш выигрыш: ${obrabotka.chisla(amount)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`}}));
                    }
                    else {
                        data.users[id].lostBtcBets += amount;
                        CLIENTS[client].send(JSON.stringify({action: "sendMessage", data: {chatId, text: `Вы проиграли.\nКурс BTC изменился на ${(endPrice - startPrice).toFixed(2)} RUB.\nПроиграно ${obrabotka.chisla(amount)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`}}));
                    }
                });
            }, 60000);
        });
        // ВНИМАНИЕ БЛЯТЬ это не работает из-за того, что ошибка создается позже проверки на ошибку (в асинке)
        if (error) {
            append.appendToUser(id, "balance", amount);
            return {success: false, message: "Произошла ошибка! Сообщите об этом разработчику!"};
        }
        return {success: true};
    }
}
let kmd = {
    leaderboard: function (mode, active_top, caller_id, page) {
        console.log({mode, active_top, caller_id, page});
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
            to_append = [place, sorted[i][0], get.get(sorted[i][0], "fullName").data];
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
        let order = ["balance", "sec", "click", "balanceBoost"] 
        let order_words = [" КШ", "/сек", "/клик", "% баланса/день"]
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
            order = ["bank", "balance", "sec", "click", "balanceBoost"]
            order_words = [" КШ в банке", " КШ", "/сек", "/клик", "% баланса/день"]
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
        let highlights_names = ["Баланс", "Клик", "Сек", "Буст баланса", "Регистрация", "Банк", "Деньги"]
        let highlights_pos = {"balance": 0, "click": 1, "sec": 2, "balanceBoost": 3, "registerTime": 4, "bank": 5, "money": 6}
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
            for (let user = start_user; user < end_user; user++) msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${top[user][2]}, ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[user][1]][order[2]])}${order_words[2]}\n`
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${top[caller_place][2]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[2]])}${order_words[2]}\n`
        
        }
        else if (mode == "bank") {
            for (let user = start_user; user < end_user; user++) msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${obrabotka.chisla(data.users[top[user][1]][order[0]])}${order_words[0]}, ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}, ${data.users[top[user][1]][order[2]]}${order_words[2]}, ${data.users[top[user][1]][order[3]]}${order_words[3]}, ${data.users[top[user][1]][order[4]]}${order_words[4]}\n`
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${data.users[top[caller_place][1]][order[0]]}${order_words[0]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[2]])}${order_words[2]}, ${data.users[top[caller_place][1]][order[3]]}${order_words[3]}, ${data.users[top[caller_place][1]][order[4]]}${order_words[4]}\n`
        }
        else if (mode == "registerTime") {
            for (let user = start_user; user < end_user; user++) msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${data.users[top[user][1]][order[0]]}${order_words[0]}, ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}\n`
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${data.users[top[caller_place][1]][order[0]]}${order_words[0]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}\n`
    
        }
        else {
            for (let user = start_user; user < end_user; user++) {
                msg += `#${top[user][0]}: <a href='tg://user?id=${top[user][1]}'>${top[user][2]}</a>: ${obrabotka.chisla(data.users[top[user][1]][order[0]])}${order_words[0]}, ${obrabotka.chisla(data.users[top[user][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[user][1]][order[2]])}${order_words[2]}, ${obrabotka.chisla(data.users[top[user][1]][order[3]])}${order_words[3]}\n`
            }
            msg += "__________\n"
            msg += `Вы: #${top[caller_place][0]}: ${obrabotka.chisla(data.users[top[caller_place][1]][order[0]])}${order_words[0]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[1]])}${order_words[1]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[2]])}${order_words[2]}, ${obrabotka.chisla(data.users[top[caller_place][1]][order[3]])}${order_words[3]}\n`
        }
        msg += "\nСтраница " + page + " из " + Math.floor(top.length / 10)
        return {success: true, data: msg}
    },
    click: function (userId) {
        if (!get.id(userId).data) return {success: false, message: "Id не найден"}
        accrual.click(userId);
        return {success: true, data: `Коллекция кристальных шаров пополнена!\nБаланс: ${obrabotka.chisla(get.get(userId, "balance").data)} КШ`}
    },
    balance: function (userId) {
        if (!get.id(userId).data) return {success: false, message: "Id не найден"}
        return {success: true, data: `Имя: ${get.get(userId, "fullName").data}\nid: \`${userId}\`\nАпгрейды: ${get.get(userId, "sec").data}/сек; ${get.get(userId, "click").data}/клик; ${get.get(userId, "sale").data}% скидки; ${get.get(userId, "balanceBoost").data}% баланса/день\nБаланс: ${obrabotka.chisla(get.get(userId, "balance").data)} КШ\nВ банке: ${obrabotka.chisla(get.get(userId, "bank").data)} КШ`}
    },
    resetMessage: function () {return {success: true, data: "Обнуляет прогресс и вы начинаете игру заново.\nЧтобы сбросить прогресс, введите `сброс подтвердить`"}},
    pay: function(from, to, amount, comment = undefined) {
        if (amount == "#r") amount = randomInt(1, get.get(from, "balance").data);
        else if (amount.slice(-1) == "%") {
            amount = obrabotka.kChisla(amount.slice(0, -1));
            if (isNaN(amount)) return {success: false, message: "Неверный тип суммы\nИспользование: перевод <сумма> <id получателя> [комментарий]"};
            if (!(amount >= 1 && amount <= 100)) return {success: false, message: "Неверное использование процентного перевода.\nИспользование: перевод <1%-100%> <id получателя> [комментарий]"};
            amount = Math.round(get.get(from, "balance").data * amount / 100);
        }
        else if (["все", "всё"].indexOf(amount) != -1) amount = get.get(from, "balance").data
        else {
            amount = obrabotka.kChisla(amount);
            if (isNaN(amount)) return {success: false, message: "Неверное значение параметра суммы\nИспользование: перевод <сумма> <id получателя> [комментарий]"};
        }
        if (to == "#r") {
            keys = Object.keys(data.users);
            to = keys[randomInt(0, keys.length)];
            delete keys;
        }
        if (!get.id(to).data) return {success: false, message: `Id ${to} не существует`}
        if (amount < 100) return {success: false, message: "Переводы меньше 100 КШ запрещены"}
        if (amount > get.get(from, "balance").data) return {success: false, message: "Недостаточно средств"}
        append.appendToUser(from, "balance", -amount);
        data.users[from].paidKkh += amount;
        append.appendToUser(to, "balance", amount);
        data.users[to].receivedKkh += amount;
        if (comment) {
            CLIENTS[get.get(to, "receiver").data].send(JSON.stringify({action: "sendMessage", data: {chatId: to, text: `Получен перевод ${obrabotka.chisla(amount)} КШ от пользователя ${get.get(from, "fullName").data} (${from})\nСообщение: ${comment}`}}));
            return {success: true, data: `Перевод ${obrabotka.chisla(amount)} КШ пользователю ${get.get(to, "fullName").data} (${to}) выполнен успешно!\nКомментарий к переводу: ${comment}`};
        }
        else {
            CLIENTS[get.get(to, "receiver").data].send(JSON.stringify({action: "sendMessage", data: {chatId: to, text: `Получен перевод ${obrabotka.chisla(amount)} КШ от пользователя ${get.get(from, "fullName").data} (${from})`}}));
            return {success: true, data: `Перевод ${obrabotka.chisla(amount)} КШ пользователю ${get.get(to, "fullName").data} (${to}) выполнен успешно!`};
        }
    },
    buyBoost: function(id, boost, amount = 1) {
        if (!get.id(id).data) return {success: false, message: "Пользователь не существует"};
        let cost = calc.boost(id, boost);
        if (cost.cost == undefined) return cost;
        cost = cost.cost;
        let balance = get.get(id, "balance").data;
        let i;
        for (i = 0; (i < amount || amount == -1) && balance >= cost && cost != undefined; i++) {
            append.appendToUser(id, boost, 1);
            append.appendToUser(id, "balance", -cost);
            balance = get.get(id, "balance").data;
            cost = calc.boost(id, boost).cost;
        }
        if (i == 0) return {success: false, message: `Недостаточно средств. Для покупки ещё необходимо ${obrabotka.chisla(cost - balance)}`};
        else return {success: true, data: `Успешно куплено Успешно куплено апгрейдов: ${i}\nid: <code>${id}</code>
Апгрейды: ${get.get(id, "sec").data}/сек; ${get.get(id, "click").data}/клик; ${get.get(id, "sale").data}% скидки; ${get.get(id, "balanceBoost").data}% баланса/день
Баланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`};
    },
    sendUser: function(from, to, type) {
        if (!get.id(from).data || !get.id(to).data) return {success: false, message: "Id не найден"};
        cost = {
            normal: 1_000_000,
            anonymous: 3_000_000
        };
        if (get.get(from, "balance").data < cost[type]) return {success: false, message: "Недостаточно средств"};
        if (!append.appendToUser(from, "balance", cost[type]).success) return {success: false, message: "Ошибка"};
        data.users[from].othersSpends += cost[type];
        if (type == "anonymous") {
            CLIENTS[get.get(to, "receiver").data].send(JSON.stringify({action: "sendMessage", data: {chatId: to, text: "Вас анонимно послали нахуй"}}));
            return {success: true, data: `Вы анонимно послали нахуй игрока ${get.get(to, "fullName").data} (${to})\nЗабрано ${obrabotka.chisla(cost[type])} КШ`};
        }
        else if (type == "normal") {
            CLIENTS[get.get(to, "receiver").data].send(JSON.stringify({action: "sendMessage", data: {chatId: to, text: `Вас послал нахуй пользователь ${get.get(from, "fullName").data} (${from})`}}));
            return {success: true, data: `Вы послали нахуй игрока ${get.get(to, "fullName").data} (${to})\nЗабрано ${obrabotka.chisla(cost[type])} КШ`};
        }

        
    },
    bankTransfer: function(id, action, value = -1) {
        console.log(value);
        let fee = 0.2//% (комиссия)
        if (value == "#r") value = randomInt(1, get.get(id, "balance").data)
        else if (value == "все" || value == "всё" || value == -1) {
            if (action == "put") value = get.get(id, "balance").data
            else if (action == "take") value = get.get(id, "bank").data
        }
        else {
            if (isNaN(parseInt(value))) return {success: false, message: "Неверный параметр суммы\nИспользование: +банк/-банк [сумма]"};
            if (value.slice(-1) == "%") {
                value = value.slice(0, -1);
                if (value > 100 || value < 1) return {success: false, message: "Неверное использование процентного числа. Процентное число должно быть не менее 1 и не более 100% от вашего баланса!"}
                value = Math.round(value / 100 * get.get(id, "balance").data);
            }
            else value = obrabotka.kChisla(value);
        }
        console.log(value);
        if ((action == "put" && value > get.get(id, "balance").data) || (action == "take" && value > get.get(id, "bank")) || value <= 0) return {success: false, message: "Неверное значение (меньше нуля или больше вашего баланса)"}
        
        let feeSum = Math.round(value*fee/100)
        if (!get.get(id)) return {success: false, message: "Id не найден"}
        if (action == "put") {
            append.appendToUser(id, "bank", value-feeSum);
            append.appendToUser(id, "balance", -value);
            data.users[id].paidKkh += feeSum;
            return {success: true, data: `Переведено ${obrabotka.chisla(value-feeSum)} КШ в банк\nКомиссия ${obrabotka.chisla(feeSum)} КШ (${fee}%)\nВ банке: ${obrabotka.chisla(get.get(id, "bank").data)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`};
        }
        else if (action == "take") {
            append.appendToUser(id, "bank", -value);
            append.appendToUser(id, "balance", value-feeSum);
            data.users[id].paidKkh += feeSum;
            return {success: true, data: `Выведено ${obrabotka.chisla(value-feeSum)} КШ из банка\nКомиссия ${obrabotka.chisla(feeSum)} КШ (${fee}%)\nВ банке: ${obrabotka.chisla(get.get(id, "bank").data)} КШ\nБаланс: ${obrabotka.chisla(get.get(id, "balance").data)} КШ`};

        }
    },
    mailingSend: function (text) {
        text += "\n\n____\nДля отключения рассылки введите рассылка нет"
        for (let i of get.ids().data) {
            if (get.get(i, "mails").data) {
                if (i != "default") CLIENTS[get.get(i, "receiver").data].send(JSON.stringify({action: "sendMessage", data: {chatId: i, text}}));
            }
        }
        return {success: true}
    },
    set: function (caller, id, toSet, value) {
        if (!get.get(caller, "isAdmin").data) return {success: false};
        if (!get.id(id).data) return {success: false, message: "Пользователь не существует"};
        if (["isAdmin", "mails", "timeLastBonus", "keyboard", "activeKeyboard", "receiver"].indexOf(toSet) != -1 && caller != 357694314) return {success: false, message: "Недостаточно прав"};
        let ret;
        if (typeof value == "string" && ["-", "+"].indexOf(value[0]) != -1) ret = append.appendToUser(id, toSet, value);
        else ret = set.set(id, toSet, value);
        if (!ret.success) return ret;
        CLIENTS[get.get(id, "receiver").data].send(JSON.stringify({action: "sendMessage", data: {chatId: id, text: `Вам установлено ${value} значение ${toSet} администратором`}}));
        return {success: true, data:`Пользователю ${get.get(id, "fullName").data} установлено ${value} значение ${toSet}`};
    },
    getIds: function (caller) {
        if (!get.get(caller, "isAdmin")) return {success: false}
        let text = "";
        let ids = get.ids().data;
        ids.forEach(i => {
            text += `${get.get(i, "fullName").data} (${i})\n`
        });
        return {success: true, data: `Вот список всех ${ids.length - 1} пользователей:\n${text.slice(0, -1)}`};
    },
    commandsList: function (id) {
        if (!get.id(id).data) return {success: false, message: "id не найден"}
        if (get.get(id, "isAdmin").data) return {success: true, data: config.messages.commandsList}
        else return {success: true, data: config.messages.commandsListUser}
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
    schedule.scheduleJob("* * */2 * *", () => backup()),
    schedule.scheduleJob("*/1 * * * * *", () => accrual.sec()),
    schedule.scheduleJob({minute: 0}, () => accrual.bank()),
    schedule.scheduleJob({hour: 0, minute: 0}, () => accrual.balanceBoost())
]

function backup(ws = undefined, id = undefined) {
    let t = new Date((get.time() + 10800) * 1000);
    let td = t.toISOString()
    let name = `backup-${td.slice(0, 4)}-${td.slice(5, 7)}-${td.slice(8, 10)}_${t.getUTCHours()}.${t.getUTCMinutes()}.${t.getUTCSeconds()}.json`;
    let error;
    fs.copyFile("usrs.json", `backups/${name}`, (err) => {if (err) {
        console.log(err);
        error = err;
    }});
    (async () => {
        try {
            const { href, method } = await upload.link(config.tokens.yadisk, `disk:/kkh_backups/${name}`, true);
            const fileStream = fs.createReadStream(`backups/${name}`);
            const uploadStream = request({ ...parse(href), method });
            fileStream.pipe(uploadStream);
            fileStream.on('end', () => uploadStream.end());
        }
        catch (err) {
            error = err;
            console.error(err);
        }
        if (!ws & !id) return
        let data = {id}
        if (error) data.success = false, data.message = error
        else data.success = true, data.data = "Бэкап успешно выполнен и выгружен в облако!"
        ws.send(JSON.stringify(data))
    })();
}
function dbWrite() {
    let t = new Date((get.time() + 10800) * 1000);
    let td = t.toISOString()
    let name = `backup-${td.slice(0, 4)}-${td.slice(5, 7)}-${td.slice(8, 10)}_${t.getUTCHours()}.${t.getUTCMinutes()}.${t.getUTCSeconds()}.json`;
    // let error;
    fs.copyFileSync("usrs.json", `backups/${name}`);
    // if (error) return {success: false, message: error}
    return {success: true, data: "БД записана"}
}