import discord, websocket, asyncio
import json as JSON
from threading import Thread
from time import sleep
from traceback import format_exc

with open("config.json", encoding="utf-8") as config:
    config = JSON.load(config)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True #если тебе оно нужно, конечно
client = discord.Client(intents=intents)


kostil_list = []

async def kostil():
    global kostil_list
    while True:
        if (len(kostil_list)):
            try:
                if (kostil_list[0]["chatType"] == "private"):
                    channel = client.get_user(int(kostil_list[0]["chatId"]))
                else:
                    channel = client.get_channel(int(kostil_list[0]["chatId"]))
                await channel.send(kostil_list[0]["message"])
            except: print("ошибка в костыле", format_exc(), sep="\n")
            finally: kostil_list.pop(0)
        await asyncio.sleep(0.7)

@client.event
async def on_ready():
    await kostil()

class CONNECTION:
    CLIENT = "discord"
    def receiver(self, ws, json):
        json = JSON.loads(json)
        self.json = json
        if (json.get("event") == "sendMessage" and json.get("message")):
            chatId = int(json["message"].get("chatId"))
            text = json["message"].get("text")
            parseMode = json["message"].get("parseMode")
            keyboard = json["message"].get("keyboard")
            chatType = json["message"].get("chatType")
            if (chatId and text):
                # data = [chatId, text]
                # if (parseMode): data.append(parseMode)
                # if (keyboard):
                #     if (keyboard == -1):
                #         resK = ReplyKeyboardRemove(True)
                #     else:
                #         resK = ReplyKeyboardMarkup(True)
                #         for i in keyboard:
                #             resK.add(*i)
                #     try: bot.send_message(*data, reply_markup=resK)
                #     except Exception as e: print(e)
                #     return
                # try: channel.send(text)
                    # bot.send_message(*data)
                # except Exception as e: print(e)
                kostil_list.append({"message": text, "chatId": chatId, "chatType": chatType})
        else: pass
    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###\ncode: {}, message: {}".format(close_status_code, close_msg))
    def on_error(self, ws, error):
        print("error: ", error)
        # if (not error): message.send_message(self.sendIds.get(self.json["id"])["chatId"], "noerr") #TODO
    def on_open(self, ws):
        print("Opened connection")
    def send(self, data):
        print(JSON.dumps(data))
        ws.send(JSON.dumps(data))
    def reconnect():
        while True:
            if (not ws.keep_running):
                a = Thread(target=ws.run_forever).start()
                sleep(15)
            sleep(10)
            
connection = CONNECTION()

@client.event
async def on_message(message):
    if (client.user.id == message.author.id or message.content): return
    if (message.content[0] == "/" and message.content == "/start"):
        connection.send({"event": "newCommand", "client": connection.CLIENT, "message": await parser(message)}) 
    else:
        connection.send({"event": "newMessage", "client": connection.CLIENT, "message": await parser(message)}) 


async def parser(message):
    if (message.reference is not None):
        message_r = await message.channel.fetch_message(message.reference.message_id)
    res = {
    "text": message.content,
    "chat": {
        "id": str(message.channel.id),
        "type": "private" if (message.guild is None) else "server"
    },
    "from_user": {
        "id": str(message.author.id),
        "nickname": message.author.name
    },
    "reply_to_message": None if (message.reference is None) else {
        "id": str(message.reference.message_id),
        "from_user": {
            "id": str(message_r.author.id)
        }
    }
}
    return res
    
if __name__ == "__main__":
    ws = websocket.WebSocketApp("ws://127.0.0.1:3200/?client={}".format(connection.CLIENT),
                on_open=connection.on_open,
                on_message=connection.receiver,
                on_error=connection.on_error,
                on_close=connection.on_close)
    a = Thread(target=ws.run_forever).start()
    Thread(target=CONNECTION.reconnect).start()
    
    client.run(config["tokens"]["discord"])