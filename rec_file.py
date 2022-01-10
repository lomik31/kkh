# -*- coding: utf-8 -*-
#test
import random
import time
import json
import copy
def read_file():
    with open('usrs.json', encoding="utf-8") as fileRead:
        fileRead = json.load(fileRead)
    return fileRead
def time_nachislenie(fileRead):
    for i in fileRead["users"]:
        fileRead["users"][i]["balance"] += fileRead["users"][i]["sec"]
        fileRead["users"][i]["earnedKkh"] += fileRead["users"][i]["sec"]
    with open('usrs.json', 'w', encoding="utf-8") as outfile:
        json.dump(fileRead, outfile, ensure_ascii=False, indent=4)
    return fileRead
def bank_nachislenie(fileRead):
    for i in fileRead["users"]:
        add = int(fileRead["users"][i]["bank"] * random.uniform(0.002, 0.025))
        fileRead["users"][i]["bank"] += add
        fileRead["users"][i]["earnedKkh"] += add
    return fileRead
def click_nachislenie(id,fileRead):
    fileRead["users"][str(id)]["balance"] += fileRead["users"][str(id)]["click"]
    fileRead["users"][str(id)]["earnedKkh"] += int(fileRead["users"][str(id)]["click"])
    return fileRead
def balance_boost_nachislenie(fileRead):
    for i in fileRead["users"]:
        fileRead["users"][i]["balance"] += fileRead["users"][i]["balance"]*fileRead["users"][i]["balanceBoost"]//100
        fileRead["users"][i]["earnedKkh"] += fileRead["users"][i]["balance"]*fileRead["users"][i]["balanceBoost"]//100
    return fileRead
#write
def write(fileRead):
    with open('usrs.json', 'w', encoding="utf-8") as outfile:
        json.dump(fileRead, outfile, ensure_ascii=False, indent=4)
#remove
def remove_id(id,fileRead):
    del fileRead["users"][str(id)]
    return fileRead
#clear
def clear_id(id,fileRead):
    for i in fileRead["users"][str(id)]:
        a = 0
        for j in fileRead["doNotClear"]:
            if (i != j): a += 1
        if (a == len(fileRead["doNotClear"])): fileRead["users"][str(id)][i] = copy.copy(fileRead["users"]["default"][i])
    return fileRead
#append
def append_id(id,userOrGroup,firstName,lastName,fileRead):
    if (userOrGroup == "private"):
        fileRead["users"][str(id)]=copy.copy(fileRead["users"]["default"])
        fileRead["users"][str(id)]["firstName"] = firstName
        if (lastName != None):
            fileRead["users"][str(id)]["lastName"] = lastName
        fileRead["users"][str(id)]["registerTime"] = int(time.time())
    else:
        fileRead["groups"][str(id)]=copy.copy(fileRead["groups"]["default"])
    return fileRead
def append_balance(id,bappend,fileRead):
    fileRead["users"][str(id)]["balance"]=fileRead["users"][str(id)]["balance"]+bappend
    return fileRead
def append_click(id,cappend,fileRead):
    fileRead["users"][str(id)]["click"]=fileRead["users"][str(id)]["click"]+cappend
    return fileRead
def append_sec(id,sappend,fileRead):
    fileRead["users"][str(id)]["sec"]=fileRead["users"][str(id)]["sec"]+sappend
    return fileRead
def append_skidka(id,skidka,fileRead):
    fileRead["users"][str(id)]["sale"]=fileRead["users"][str(id)]["sale"]-skidka
    return fileRead
def append_boost_balance(id,fappend,fileRead):
    fileRead["users"][str(id)]["balanceBoost"]=fileRead["users"][str(id)]["balanceBoost"]+fappend
    return fileRead
def append_last_command(id, command, fileRead):
    fileRead["users"][str(id)]["lastCommand"]=command
    fileRead["users"][str(id)]["timeLastCommand"]=int(time.time())
    return fileRead
def updateUserName(fileRead):
    dict = []
    for i in fileRead["users"].keys():
        if (i != "default"):
            dict.append([i, fileRead["users"][i]["firstName"], fileRead["users"][i]["lastName"]])
    return dict
def updateUserNameWrite(dict, fileRead):
    for i in dict:
        fileRead["users"][i[0]]["firstName"] = i[1]
        fileRead["users"][i[0]]["lastName"] = i[2]
    return fileRead
#get
def get_balance(id,fileRead): return int(fileRead["users"][str(id)]["balance"])
def get_click(id,fileRead): return int(fileRead["users"][str(id)]["click"])
def get_sec(id,fileRead): return int(fileRead["users"][str(id)]["sec"])
def get_boost_balance(id, fileRead): return int(fileRead["users"][str(id)]["balanceBoost"])
def get_all(id,fileRead):
    keys=[]
    data=[]
    for i in fileRead["users"][str(id)].keys():
        if (i!="default"):
            keys.append(i)
    for i in keys:
        data.append(fileRead["users"][str(id)][i])
    return data
def get_ids(fileRead):
    ids=[]
    for i in fileRead["users"].keys():
        if (i!="default"):
            ids.append(int(i))
    return ids
def get_keyboard(id,fileRead): return fileRead["users"][str(id)]["keyboard"]
def get_skidka(id,fileRead): return 100 - int(fileRead["users"][str(id)]["sale"])
def get_admin(id,fileRead): return fileRead["users"][str(id)]["isAdmin"]
def get_active_passive_keyboard(id,fileRead): return fileRead["users"][str(id)]["activeKeyboard"]
def get_rassilka(id,fileRead): return fileRead["users"][str(id)]["mails"]
def get_time_give_bonus(id,fileRead): return int(fileRead["users"][str(id)]["timeLastBonus"])
def get_time_give_bonus2(id,fileRead): return int(fileRead["users"][str(id)]["timeLastSecondBonus"])
def get_time_now(): return int(round(time.time()))
def get_last_command(id, fileRead): return fileRead["users"][str(id)]["lastCommand"]
def getFullName(id, fileRead):
    name = fileRead["users"][str(id)]["firstName"]
    if (fileRead["users"][str(id)]["lastName"] != None):
        name += " "+fileRead["users"][str(id)]["lastName"]
    return name
def getBank(id, fileRead): return fileRead["users"][str(id)]["bank"]
#boost
def cal_boost_click(id,fileRead):
    nac_cena=100 #изначальная цена
    procent=15 #процент стоимости следующего буста
    boost_level=int(fileRead["users"][str(id)]["click"])
    skidka=int(fileRead["users"][str(id)]["sale"])
    if (skidka==0):
        if (boost_level==0):
            return nac_cena
        for i in range(0,boost_level):
            nac_cena=nac_cena*(100+procent)//100
        return nac_cena
    if (boost_level==1):
        nac_cena=nac_cena*skidka//100
        return nac_cena
    for i in range(0,boost_level):
        nac_cena=nac_cena*(100+procent)//100
    nac_cena=nac_cena*skidka//100
    return nac_cena
def cal_boost_sec(id,fileRead):
    nac_cena=300 #изначальная цена
    procent=15 #процент стоимости следующего буста
    boost_level=int(fileRead["users"][str(id)]["sec"])
    skidka=int(fileRead["users"][str(id)]["sale"])
    if (skidka==0):
        if (boost_level==0):
            return nac_cena
        for i in range(0,boost_level):
            nac_cena=nac_cena*(100+procent)//100
        return nac_cena
    if (boost_level==0):
        nac_cena=nac_cena*skidka//100
        return nac_cena
    for i in range(0,boost_level):
        nac_cena=nac_cena*(100+procent)//100
    nac_cena=nac_cena*skidka//100
    return nac_cena
def cal_boost_skidka(id,fileRead):
    nac_cena=7500 #изначальная цена
    procent=15 #процент стоимости следующего буста
    boost_level=100-int(fileRead["users"][str(id)]["sale"])
    skidka=int(fileRead["users"][str(id)]["sale"])
    if (skidka==0):
        if (boost_level==0):
            return nac_cena
        for i in range(0,boost_level):
            nac_cena=nac_cena*(100+procent)//100
        return nac_cena
    if (boost_level==0):
        nac_cena=nac_cena*skidka//100
        return nac_cena
    for i in range(0,boost_level):
        nac_cena=nac_cena*(100+procent)//100
    nac_cena=nac_cena*skidka//100
    return nac_cena
def cal_boost_balance(id,fileRead):
    nac_cena=5000000 #изначальная цена
    procent=40 #процент стоимости следующего буста
    boost_level=int(fileRead["users"][str(id)]["balanceBoost"])
    skidka=int(fileRead["users"][str(id)]["sale"])
    if (skidka==0):
        if (boost_level==0):
            return nac_cena
        for i in range(0,boost_level):
            nac_cena=nac_cena*(100+procent)//100
        return nac_cena
    if (boost_level==0):
        nac_cena=nac_cena*skidka//100
        return nac_cena
    for i in range(0,boost_level):
        nac_cena=nac_cena*(100+procent)//100
    nac_cena=nac_cena*skidka//100
    return nac_cena
#keyboard
def keyboard_on(id,chatType,fileRead):
    if (chatType == "private"):
        fileRead["users"][str(id)]["keyboard"]=True
    else:
        fileRead["groups"][str(id)]["keyboard"]=True
    return fileRead
def keyboard_off(id,chatType,fileRead):
    if (chatType == "private"):
        fileRead["users"][str(id)]["keyboard"]=False
    else:
        fileRead["groups"][str(id)]["keyboard"]=False
    return fileRead
def set_active_passive_keyboard(id,active_passive,chatType,fileRead):
    if (chatType == "private"):
        fileRead["users"][str(id)]["activeKeyboard"]=active_passive
    else:
        fileRead["groups"][str(id)]["activeKeyboard"]=active_passive
    return fileRead
#admin
def set_admin(id,fileRead):
    fileRead["users"][str(id)]["isAdmin"]=True
    return fileRead
def unset_admin(id,fileRead):
    fileRead["users"][str(id)]["isAdmin"]=False
    return fileRead
#bonus
def set_mnoz_bonus(id,on_off,fileRead):
    if (on_off==1):
        on_off=True
    elif (on_off==0):
        on_off=False
    fileRead["users"][str(id)]["multiplier"]=on_off
    return fileRead
def get_mnoz_bonus(id,fileRead): return fileRead["users"][str(id)]["multiplier"]
def give_bonus(id,fileRead):
    mnoz=get_mnoz_bonus(id,fileRead)
    bonus = (get_sec(id, fileRead) * 3600 + get_click(id, fileRead) * 5400 + get_boost_balance(id, fileRead) * 500000) * mnoz
    append_balance(id,bonus,fileRead)
    fileRead["users"][str(id)]["othersProceeds"] += bonus
    if (mnoz==1):
        return 'Вы забрали ежедневный бонус ' + ob_chisla(bonus) + ' КШ\nБаланс: ' + ob_chisla(get_balance(id, fileRead)) + ' КШ'
    return f"Вы забрали ежедневный бонус {ob_chisla(bonus)} КШ (ваш множитель — x{mnoz})\nБаланс: {ob_chisla(get_balance(id, fileRead))} КШ"
def set_time_give_bonus(id,time,fileRead):
    fileRead["users"][str(id)]["timeLastBonus"] = time
    return fileRead
def set_time_give_bonus2(id,time,fileRead):
    fileRead["users"][str(id)]["timeLastSecondBonus"]=time
    return fileRead
def give_bonus2(id,fileRead):
    bonus = random.randint(10000, (get_sec(id, fileRead) * 3600 + get_click(id, fileRead) * 5400 + get_boost_balance(id, fileRead) * 500000) + 10000)
    append_balance(id,bonus,fileRead)
    fileRead["users"][str(id)]["othersProceeds"] += bonus
    return 'Вы получили случайный бонус2  в размере ' + ob_chisla(bonus) + ' КШ\nБаланс: ' + ob_chisla(get_balance(id, fileRead)) + ' КШ'
#obrabotka
def ob_chisla(chislo_okda):
    t_result=""
    result=""
    chislo_okda=str(chislo_okda)
    counter=0
    for i in range(1,len(chislo_okda)+1):
        if (counter%3==0 and counter!=0):
            t_result=t_result+"."
        t_result=t_result+chislo_okda[-i]
        counter=counter+1
    for i in range(1,len(t_result)+1):
        result=result+t_result[-i]
    return result
def obratno_ob_chisla(chislo_okda):
    result=""
    for i in range(0,len(chislo_okda)):
        if (chislo_okda[i]!="." and chislo_okda[i]!=","):
            result=result+chislo_okda[i]
    return result
def ob_k_chisla(chislo_okda):
    chislo_okda=obratno_ob_chisla(chislo_okda)
    if ("k" not in chislo_okda and "m" not in chislo_okda and "к" not in chislo_okda and "м" not in chislo_okda):
        return chislo_okda
    total=0
    row=1
    for i in range(0,len(chislo_okda)):
        if (chislo_okda[i]=="k" or chislo_okda[i]=="m" or chislo_okda[i]=="к" or chislo_okda[i]=="м"):
            total=total+1
        if (i>=1):
            if ((chislo_okda[i]=="k" or chislo_okda[i]=="m" or chislo_okda[i]=="к" or chislo_okda[i]=="м") and (chislo_okda[i-1]=="k" or chislo_okda[i-1]=="m" or chislo_okda[i-1]=="к" or chislo_okda[i-1]=="м")):
                row=row+1
            else:
                row=1
    if (total!=row):
        return "Число не правильное"
    chislo_oknet=chislo_okda[:-total:]
    try:
        int(chislo_oknet)
    except:
        return "В середине числа не должно быть букв а"
    for i in range(0,len(chislo_okda)):
        if (chislo_okda[i]=="k" or chislo_okda[i]=="к"):
            chislo_oknet=chislo_oknet+"000"
        elif (chislo_okda[i]=="m" or chislo_okda[i]=="м"):
            chislo_oknet=chislo_oknet+"000000"
    return chislo_oknet
def ob_vremeni_bonusa(vremya_okda):
    return time.strftime("%H:%M:%S", time.gmtime(vremya_okda))
def ob_vremeni(vremya_okda):
    return time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(int(vremya_okda)))
#moneta
def moneta_stavka(id,stavka,or_or_re,fileRead):
    perc=0
    try:
        if (stavka=="#r"):
            stavka=random.randint(1,int(fileRead["users"][str(id)]["balance"]))
        else:
            if (stavka[-1]=="%"):
                perc=1
                stavka=stavka[:-1:]
                try:
                    int(stavka)
                except:
                    return ("Неверное использование процентной ставки. Использование: <1%-100%> <орел/решка>")  
                if (len(stavka)>4 or int(stavka)>100 or int(stavka)<1):
                    return ("Неверное использование процентной ставки. Процент должен быть от 1 до 100")
                stavka=get_balance(id, fileRead)*int(stavka)//100
        if (perc==0):
            try:
                int(stavka)
            except:
                return ("Использование: монета <ставка/всё> <орел/решка>")
            stavka=int(stavka)
            if (stavka<=0 or stavka>get_balance(id, fileRead)):
                return ("Неверная ставка (меньше нуля или больше вашего баланса)")
        if (or_or_re=="#r"):
            or_or_re=random.randint(1,2)
        elif (or_or_re=="орёл" or or_or_re=="орел" or or_or_re=="jh`k" or or_or_re=="jhtk" or or_or_re=="1"):
            or_or_re=1
        elif (or_or_re=="решка" or or_or_re=="htirf" or or_or_re=="2"):
            or_or_re=2
        if (or_or_re!=1 and or_or_re!=2):
            return ("Использование: монета <ставка/всё> <орел/решка>")
        result=random.randint(1,2)
        if (result==or_or_re):
            fileRead["users"][str(id)]["balance"]=int(fileRead["users"][str(id)]["balance"])+stavka #fileRead[i][1]=str(int(fileRead[i][1])+stavka)
            fileRead["users"][str(id)]["wonMoneta"] += stavka
            return ('Вы выиграли! '+'Ваш выигрыш: '+str(ob_chisla(stavka))+' КШ'+'\n'+'Баланс: '+str(ob_chisla(get_balance(id, fileRead)))+' КШ')
        elif (result!=or_or_re):
            fileRead["users"][str(id)]["balance"]=int(fileRead["users"][str(id)]["balance"])-stavka #fileRead[i][1]=str(int(fileRead[i][1])-stavka)
            fileRead["users"][str(id)]["lostMoneta"] += stavka
            return ('Вы проиграли. '+'Проиграно '+str(ob_chisla(stavka))+' КШ'+'\n'+'Баланс: '+str(ob_chisla(get_balance(id, fileRead)))+' КШ')
        else:
            return "Ой, что-то пошло не так..."
    except:
        return ("Использование: монета <ставка/всё> <орел/решка>")
#rassilka
def set_rassilka(id,on_off,fileRead):
    if (on_off==1):
        on_off=True
    elif (on_off==0):
        on_off=False
    fileRead["users"][str(id)]["mails"]=on_off
    return fileRead
#promo
def promo_append(promo_okda,znachenie_in_usrs,kol_vo_activacij,vremja_dejstvija,fileRead):
    try:
        if (int(vremja_dejstvija)<=0):
            tm=-1
        else:
            tm=int(vremja_dejstvija)+time.time()
    except:
        try:
            tm = float(vremja_dejstvija[:-1])
            if (vremja_dejstvija[-1:] == "h"):
                tm *= 3600
            elif (vremja_dejstvija[-1:] == "m"):
                tm *= 60
            elif (vremja_dejstvija[-1:] == "s"):
                tm *= 1
            elif (vremja_dejstvija[-1:] == "d"):
                tm *= 86400
            elif (vremja_dejstvija[-1:] == "w"):
                tm *= 604800
            else: return "Использование множителей времени: s, m, h, d, w, mo (писать слитно с цифрами)"
            tm=tm+time.time()
        except ValueError:
            try:
                tm = float(vremja_dejstvija[:-2])
                if (vremja_dejstvija[-1] == "o") and (vremja_dejstvija[-2] == "m"):
                    tm *= 2592000
                else: return "Использование множителей времени: s, m, h, d, w, mo (писать слитно с цифрами)"
                tm=tm+time.time()
            except: return "Использование множителей времени: s, m, h, d, w, mo (писать слитно с цифрами)"
    if (promo_check(str(promo_okda))==False):
        with open('promos.json', encoding="utf-8") as promoRead:
            promoRead = json.load(promoRead)
            promoRead["allPromos"][promo_okda]=copy.copy(promoRead["allPromos"]["default"])
            for i in znachenie_in_usrs.keys():
                if (i not in promoRead["allPromos"]["default"].keys()) or (i=="validity") or (i=="activationLimit") or (i=="activatedTimes"):
                    promo_remove(promo_okda, fileRead)
                    return "Введено недопустимое значение! Операция отменена"
                else:
                    #сюдаблять написать строку добавления значения
                    promoRead["allPromos"][promo_okda][i]=znachenie_in_usrs[i]
            promoRead["allPromos"][promo_okda]["activationLimit"]=kol_vo_activacij
            promoRead["allPromos"][promo_okda]["validity"]=tm
        with open('promos.json', 'w', encoding="utf-8") as outfile:
            json.dump(promoRead, outfile, ensure_ascii=False, indent=4)
        return "Промокод успешно добавлен!"
    else:
        return "Промокод уже существует!"
def promo_check(promo_okda):
    with open('promos.json', encoding="utf-8") as promoRead:
        promoRead = json.load(promoRead)
        try:
            promoRead["allPromos"][promo_okda]
            return True
        except:
            return False
def promo_read(promo_okda):
    with open('promos.json', encoding="utf-8") as promoRead:
        promoRead = json.load(promoRead)
    try:
        return promoRead["allPromos"][promo_okda]
    except:
        return "Промокода не существует!" 
def promo_remove(promo_okda,fileRead):
    with open('promos.json', encoding="utf-8") as promoRead:
        promoRead = json.load(promoRead)
    try:
        del promoRead["allPromos"][promo_okda]
    except:
        return "Промокода не существует!"
    for i in fileRead["users"]:
        if (promo_okda in fileRead["users"][i]["activatedPromos"]):
            fileRead["users"][i]["activatedPromos"].remove(promo_okda)
    with open('promos.json', 'w', encoding="utf-8") as outfile:
        json.dump(promoRead, outfile, ensure_ascii=False, indent=4)
    return "Промокод удален из бд!"
def promo_info(promo_okda):
    with open('promos.json', encoding="utf-8") as promoRead:
        promoRead = json.load(promoRead)
    ebp=[]
    for i in promoRead["allPromos"][promo_okda].keys():
        if (i!="activationLimit" and i!="activatedTimes" and i!="validity"):
            ebp.append(i)
    msg=""
    for i in ebp:
        if (i=="balance"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg}{promoRead['allPromos'][promo_okda][i]} КШ, "
        elif (i=="click"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]} КШ за клик, "
        elif (i=="sek"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]} КШ за секунду, "
        elif (i=="sale"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]}% скидки, "
        elif (i=="multiplier"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]}x бонуса, "
        elif (i=="balanceBoost"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]} буста баланса, "
    msg=msg[:len(msg)-2:]
    return "Промокод даёт: "+msg
def promo_list():
    with open('promos.json', encoding="utf-8") as promoRead:
        promoRead = json.load(promoRead)
    prms=[]
    for i in promoRead["allPromos"].keys():
        prms.append(i)
    msg="Список промокодов: "
    for i in prms:
        if (i!="default"):
            msg=msg+i+", "
    msg=msg[:-2:]
    return msg
#activision blizzard
#promo_okda - название промокода
def activation_promo(id,promo_okda,fileRead):
    if (promo_okda=="default"):
        return fileRead,"Ща твой прогресс по дефолту ёбну"
    id=str(id)
    ebp=[]
    with open('promos.json', encoding="utf-8") as promoRead:
        promoRead = json.load(promoRead)
    promo_susestvuet=False
    if (promo_okda in promoRead["allPromos"].keys()):
        promo_susestvuet=True
    if (promo_susestvuet==False):
        return fileRead,"Промокода не существует!"
    if (promo_okda in fileRead["users"][id]["activatedPromos"]):
        return fileRead,"Промокод уже активирован!"
    if (int(promoRead["allPromos"][promo_okda]["validity"])<time.time() and int(promoRead["allPromos"][promo_okda]["validity"])!=-1):
        return fileRead,"Истекло время активации промокода"
    if (int(promoRead["allPromos"][promo_okda]["activatedTimes"])>=int(promoRead["allPromos"][promo_okda]["activationLimit"]) and int(promoRead["allPromos"][promo_okda]["activationLimit"])!=-1):
        return fileRead,"Превышено число активаций промокода"
    #проверка завершена, начинается активация
    tmp=fileRead["users"][id]["activatedPromos"]
    tmp1=[]
    for i in tmp:
        tmp1.append(i)
    tmp1.append(promo_okda)
    fileRead["users"][id]["activatedPromos"]=copy.copy(tmp1)
    for i in promoRead["allPromos"][promo_okda].keys():
        if (i!="activationLimit" and i!="activatedTimes" and i!="validity"):
            ebp.append(i)
            fileRead["users"][id][i]=fileRead["users"][id][i]+promoRead["allPromos"][promo_okda][i]
        if (i == "balance"):
            fileRead["users"][str(id)]["othersProceeds"] += promoRead["allPromos"][promo_okda][i]
    promoRead["allPromos"][promo_okda]["activatedTimes"]=promoRead["allPromos"][promo_okda]["activatedTimes"]+1
    with open('promos.json', 'w', encoding="utf-8") as outfile:
        json.dump(promoRead, outfile, ensure_ascii=False, indent=4)
    msg=""
    for i in ebp:
        if (i=="balance"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg}{promoRead['allPromos'][promo_okda][i]} КШ, "
        elif (i=="click"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]} КШ за клик, "
        elif (i=="sek"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]} КШ за секунду, "
        elif (i=="sale"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]}% скидки, "
        elif (i=="multiplier"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]}x множитель ежедневного бонуса, "
        elif (i=="balanceBoost"):
            if (promoRead['allPromos'][promo_okda][i]!=0):
                msg=f"{msg} + {promoRead['allPromos'][promo_okda][i]} буста баланса, "
    msg=msg[:len(msg)-2:]
    return fileRead,f"Вам начислено {msg}"
#leaderboard
def sort(sort_massive):
    for i in range(0,len(sort_massive)):
        for j in range(0,len(sort_massive)-1):
            if (sort_massive[j]<sort_massive[j+1]):
                sort_massive[j],sort_massive[j+1]=sort_massive[j+1],sort_massive[j]
    return sort_massive
def l_sort(sort_massive,idlist,inverse):
    otnjat=0
    result_massive=[]
    for i in range(0,len(sort_massive)):
        for j in range(0,len(sort_massive)-1):
            if (not inverse and sort_massive[j]<sort_massive[j+1]):
                sort_massive[j],sort_massive[j+1]=sort_massive[j+1],sort_massive[j]
                idlist[j],idlist[j+1]=idlist[j+1],idlist[j]
            elif (inverse and sort_massive[j]>sort_massive[j+1]):
                sort_massive[j],sort_massive[j+1]=sort_massive[j+1],sort_massive[j]
                idlist[j],idlist[j+1]=idlist[j+1],idlist[j]
    result_massive.append([1,idlist[0]])
    for i in range(1,len(sort_massive)):
        if (sort_massive[i]==sort_massive[i-1]):
            if (i-1>=0):
                result_massive.append([result_massive[i-1][0],idlist[i]])
                otnjat+=1
            else:
                result_massive.append([i-otnjat,idlist[i]])
        else:
            result_massive.append([i+1-otnjat,idlist[i]])
    return result_massive
def leaderboard(fileRead, topmode, caller_id, page, active_top):
    znmas=[]
    idlist=[]
    place=1
    tofind="0"
    inverse=False
    tofind2="0"
    if (topmode=="б" or topmode=="баланс"):
        tofind="balance"
    elif (topmode=="с" or topmode=="сек"):
        tofind="sec"
    elif (topmode=="к" or topmode=="клик"):
        tofind="click"
    elif (topmode=="бб" or topmode=="балансбуст"):
        tofind="balanceBoost"
    elif (topmode=="рег" or topmode=="регистрация"):
        tofind="registerTime"
        inverse=True
    elif (topmode=="банк"):
        tofind="bank"
    elif (topmode=="деньги"):
        tofind="bank"
        tofind2="balance"
        
    if (tofind=="0"):
        return "По этому значению не может быть составлена доска лидеров!"
    for i in fileRead["users"].keys():
        if (i!="default"):
            if (not active_top or time.time()-int(fileRead["users"][i]["timeLastCommand"])<1814400):
                place=place+1
                try:
                    if (tofind2!="0"):
                        int(fileRead["users"][i][tofind])+int(fileRead["users"][i][tofind2])
                    else:
                        int(fileRead["users"][i][tofind])
                except:
                    return "Произошла ошибка, напиши об этом сообщении @Martin_Verner"
                if (tofind2!="0"):
                    znmas.append(int(fileRead["users"][i][tofind])+int(fileRead["users"][i][tofind2]))
                else:
                    znmas.append(int(fileRead["users"][i][tofind]))
                idlist.append(int(i))
    if (len(idlist)==0):
        return "Активных пользователей нет :("
    result_massive=l_sort(znmas, idlist, inverse)
    for i in range(len(result_massive)):
        result_massive[i].append(getFullName(result_massive[i][1], fileRead))
    return leaderboard2nd_step(fileRead,result_massive,topmode,caller_id,page,active_top)
def leaderboard2nd_step(fileRead, massive, topmode, caller_id, page, active_top):
    okrugleno=len(massive)//10
    if (str(len(massive))[-1]!="0"):
        okrugleno+=1
    if (page>okrugleno and page!=2281337):# or page<=0):
        return "Выберите правильную страницу (1-"+str(okrugleno)+")"
    msg=""
    start_page=0+10*(page-1)
    if (page==2281337):
        start_page=0
        page=okrugleno
        #print(start_page, page)
        msg+="Ты нахуй страницу отладки открыл а \n"
        #print(msg)
    t1="balance"
    t2="sec"
    t3="click"
    t4="balanceBoost"
    t5="registerTime"
    t6="bank"
    t7=""
    t1ru=" КШ"
    t2ru="/сек"
    t3ru="/клик"
    t4ru="% баланса/день"
    t5ru=" регистрация"
    t6ru=" в банке"
    t7ru=" КШ (всего)"
    #t1,t2,t3,t4,t5,t6,t7="balance","sec","click","balanceBoost","registerTime"
    #t1ru,t2ru,t3ru,t4ru,t5ru,t6ru,t7ru=" КШ","/сек","/клик","% баланса/день"," регистрация"," КШ (всего)"
    msg+="Топ"
    if (active_top):
        msg+=" активных пользователей (для общего топа есть команда \"всетоп\")\n"
    else:
        msg+=" всех пользователей (для топа активных есть команда \"топ\")\n"
    if (topmode=="б" or topmode=="баланс"):
        msg+="(Баланс) | Клик | Сек | Буст баланса | Регистрация | Банк | Деньги"
    elif (topmode=="с" or topmode=="сек"):
        msg+="Баланс | Клик | (Сек) | Буст баланса | Регистрация | Банк | Деньги"
        t1,t2="sec","balance"
        t1ru,t2ru="/сек"," КШ"
    elif (topmode=="к" or topmode=="клик"):
        msg+="Баланс | (Клик) | Сек | Буст баланса | Регистрация | Банк | Деньги"
        t1,t2,t3="click","balance","sec"
        t1ru,t2ru,t3ru="/клик"," КШ","/сек"
    elif (topmode=="бб" or topmode=="балансбуст"):
        msg+="Баланс | Клик | Сек | (Буст баланса) | Регистрация | Банк | Деньги"
        t1,t2,t3,t4="balanceBoost","balance","sec","click"
        t1ru,t2ru,t3ru,t4ru="% баланса/день"," КШ","/сек","/клик"
    elif (topmode=="рег" or topmode=="регистрация"):
        msg+="Баланс | Клик | Сек | Буст баланса | (Регистрация) | Банк | Деньги"
        t1,t2,t3,t4,t5="registerTime","balance","sec","click","balanceBoost"
        t1ru,t2ru,t3ru,t4ru,t5ru=" регистрация"," КШ","/сек","/клик","% баланса/день"
    elif (topmode=="банк"):
        msg+="Баланс | Клик | Сек | Буст баланса | Регистрация | (Банк) | Деньги"
        t1,t2,t3,t4,t5,t6,t7="bank","balance","sec","click","balanceBoost","",""
        t1ru,t2ru,t3ru,t4ru,t5ru,t6ru,t7ru=" в банке"," КШ","/сек","/клик","% баланса/день","",""
    elif (topmode=="деньги"):
        msg+="Баланс | Клик | Сек | Буст баланса | Регистрация | Банк | (Деньги)"
        t1,t2,t3,t4,t5,t6,t7="","balance","bank","","","",""
        t1ru,t2ru,t3ru,t4ru,t5ru,t6ru,t7ru=" КШ (всего)"," КШ"," в банке","","","",""
        

    #""
    #if (active_top):
    #    msg+="\nДля общего топа есть команда \"всетоп\""
    #else:
    #    msg+="\nДля топа активных пользователей есть команда \"всетоп\""
    msg+="\n\n"
    if (topmode=="деньги"):
        for i in range(start_page, 10*page):
            if (i<len(massive)):
                msg=msg+f"#{massive[i][0]}: {massive[i][2]} ({massive[i][1]}): {ob_chisla(fileRead['users'][str(massive[i][1])]['balance']+fileRead['users'][str(massive[i][1])]['bank'])}{t1ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t3])}{t3ru}"+"\n"# msg=msg+f"#{massive[i][0]}: {massive[i][2]} ({massive[i][1]}): {ob_chisla(fileRead['users'][str(massive[i][1])][t1])}{t1ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t5])}{t5ru}"+"\n" #str(massive[i][0])+"-е место: "+str(massive[i][2])+" ("+str(massive[i][1])+")\n"+str(fileRead["users"][str(massive[i][1])][t1])+str(fileRead["users"][str(massive[i][1])][t2])+str(fileRead["users"][str(massive[i][1])][t3])+"\n"
        msg+="__________\n"
        for i in massive:
            if (i[1]==caller_id):
                msg+=f"Вы: #{i[0]}: {ob_chisla(fileRead['users'][str(caller_id)][t1])}{t1ru}, {ob_chisla(fileRead['users'][str(caller_id)][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(caller_id)][t3])}{t3ru}"
    elif (topmode=="банк"):
        for i in range(start_page, 10*page):
            if (i<len(massive)):
                msg=msg+f"#{massive[i][0]}: {massive[i][2]} ({massive[i][1]}): {ob_chisla(fileRead['users'][str(massive[i][1])]['balance']+fileRead['users'][str(massive[i][1])]['bank'])}{t1ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t5])}{t5ru}"+"\n"# msg=msg+f"#{massive[i][0]}: {massive[i][2]} ({massive[i][1]}): {ob_chisla(fileRead['users'][str(massive[i][1])][t1])}{t1ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t5])}{t5ru}"+"\n" #str(massive[i][0])+"-е место: "+str(massive[i][2])+" ("+str(massive[i][1])+")\n"+str(fileRead["users"][str(massive[i][1])][t1])+str(fileRead["users"][str(massive[i][1])][t2])+str(fileRead["users"][str(massive[i][1])][t3])+"\n"
        msg+="__________\n"
        for i in massive:
            if (i[1]==caller_id):
                msg+=f"Вы: #{i[0]}: {ob_chisla(fileRead['users'][str(caller_id)][t1])}{t1ru}, {ob_chisla(fileRead['users'][str(caller_id)][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(caller_id)][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(caller_id)][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(caller_id)][t5])}{t5ru}"
    elif (topmode=="рег" or topmode=="регистрация"):
        for i in range(start_page, 10*page):
            if (i<len(massive)):
                msg=msg+f"#{massive[i][0]}: {massive[i][2]} ({massive[i][1]}): {ob_vremeni(fileRead['users'][str(massive[i][1])][t1])}, {ob_chisla(fileRead['users'][str(massive[i][1])][t2])}{t2ru}"+"\n"#, {ob_chisla(fileRead['users'][str(massive[i][1])][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t5])}{t5ru}"+"\n"#str(massive[i][0])+"-е место: "+str(massive[i][2])+" ("+str(massive[i][1])+")\n"+str(fileRead["users"][str(massive[i][1])][t1])+str(fileRead["users"][str(massive[i][1])][t2])+str(fileRead["users"][str(massive[i][1])][t3])+"\n"
        msg+="__________\n"
        for i in massive:
            if (i[1]==caller_id):
                msg+=f"Вы: #{i[0]}: {ob_vremeni(fileRead['users'][str(caller_id)][t1])}, {ob_chisla(fileRead['users'][str(caller_id)][t2])}{t2ru}"#, {ob_chisla(fileRead['users'][str(caller_id)][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(caller_id)][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(caller_id)][t5])}{t5ru}"
    else:
        for i in range(start_page, 10*page):
            if (i<len(massive)):
                msg=msg+f"#{massive[i][0]}: {massive[i][2]} ({massive[i][1]}): {ob_chisla(fileRead['users'][str(massive[i][1])][t1])}{t1ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t5])}{t5ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t6])}{t6ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t7])}{t7ru}"+"\n"# msg=msg+f"#{massive[i][0]}: {massive[i][2]} ({massive[i][1]}): {ob_chisla(fileRead['users'][str(massive[i][1])][t1])}{t1ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(massive[i][1])][t5])}{t5ru}"+"\n" #str(massive[i][0])+"-е место: "+str(massive[i][2])+" ("+str(massive[i][1])+")\n"+str(fileRead["users"][str(massive[i][1])][t1])+str(fileRead["users"][str(massive[i][1])][t2])+str(fileRead["users"][str(massive[i][1])][t3])+"\n"
        msg+="__________\n"
        for i in massive:
            if (i[1]==caller_id):
                msg+=f"Вы: #{i[0]}: {ob_chisla(fileRead['users'][str(caller_id)][t1])}{t1ru}, {ob_chisla(fileRead['users'][str(caller_id)][t2])}{t2ru}, {ob_chisla(fileRead['users'][str(caller_id)][t3])}{t3ru}, {ob_chisla(fileRead['users'][str(caller_id)][t4])}{t4ru}, {ob_chisla(fileRead['users'][str(caller_id)][t5])}{t5ru}, {ob_chisla(fileRead['users'][str(caller_id)][t6])}{t6ru}, {ob_chisla(fileRead['users'][str(caller_id)][t7])}{t7ru}"
    msg+="\n\nСтраница "+str(page)+"/"+str(okrugleno)
    return msg

def chooseNewWinner(timeLastActivity, fileRead):
    try: timeLastActivity = int(timeLastActivity)
    except: return False
    winnerId = random.choice(list(fileRead["users"].keys()))
    if (winnerId != "default"):
        if (get_time_now() - fileRead["users"][winnerId]["timeLastCommand"]) < timeLastActivity:
            try: return int(winnerId)
            except: return chooseNewWinner(timeLastActivity, fileRead)
        else: return chooseNewWinner(timeLastActivity, fileRead)
    else: return chooseNewWinner(timeLastActivity, fileRead)

#530
