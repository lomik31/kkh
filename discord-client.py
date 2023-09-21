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

async def sendMessage(message):
    if (message["chatType"] == "private"): channel = client.get_user(int(message["chatId"]))
    else: channel = client.get_channel(int(message["chatId"]))
    await channel.send(message["text"])

async def setActivity(activity: bool):
    if (activity): await client.change_presence(activity=discord.Game(name="Коллекцию кристальных шаров"))
    else: await client.change_presence(activity=None)

@client.event
async def on_ready():
    if (ws.keep_running): await setActivity(True)


class CONNECTION:
    CLIENT = "discord"
    pending = []
    def receiver(self, ws, json):
        json = JSON.loads(json)
        self.json = json
        if (json.get("event") == "sendMessage" and json.get("message")):
            chatId = int(json["message"].get("chatId"))
            text = json["message"].get("text")
            # parseMode = json["message"].get("parseMode")
            # keyboard = json["message"].get("keyboard")
            chatType = json["message"].get("chatType")
            if (chatId and text and chatType):
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
                try:
                    asyncio.run_coroutine_threadsafe(sendMessage(json["message"]), client.loop).result()
                except: print(format_exc())
        else: pass
    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###\ncode: {}, message: {}".format(close_status_code, close_msg))
        asyncio.run_coroutine_threadsafe(setActivity(False), client.loop).result()
    def on_error(self, ws, error):
        print("error: ", error)
        # if (not error): message.send_message(self.sendIds.get(self.json["id"])["chatId"], "noerr") #TODO
    def on_open(self, ws):
        print("Opened connection")
        if (client.is_ready()):
            asyncio.run_coroutine_threadsafe(setActivity(True), client.loop).result()
        if (len(self.pending) > 0):
            print("Sending pending (lol what)")
            while (len(self.pending)):
                ws.send(self.pending[0])
                self.pending.pop(0)
            print("Successfully sent")
    def send(self, data):
        if (isinstance(data, object)): data = JSON.dumps(data, default=lambda x: x.__dict__)
        else: data = JSON.dumps(data)
        try: ws.send(data)
        except:
            print("can't send, added to pending")
            return self.pending.append(data)
    def reconnect():
        while True:
            if (not ws.keep_running):
                global a
                a = Thread(target=ws.run_forever).start()
                sleep(15)
            sleep(10)
            
connection = CONNECTION()

@client.event
async def on_message(message):
    if (message.author.bot or not message.content): return
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
        "id": str(message.author.id)
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
    ws = websocket.WebSocketApp(f"ws://{config['websocketIp']}/?client={connection.CLIENT}",
                on_open=connection.on_open,
                on_message=connection.receiver,
                on_error=connection.on_error,
                on_close=connection.on_close)
    a = Thread(target=ws.run_forever).start()
    Thread(target=CONNECTION.reconnect).start()
    
    client.run(config["tokens"]["discord"])