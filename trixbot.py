import json
import requests
import time
import urllib.parse
from dbhelper import DBHelper

TOKEN = "463764621:AAFje6FXhT7kijK2EKah-8RQjluy8iVw4Cc"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

db = DBHelper()

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            items = db.get_items(chat)
            if text == "/done":
                keyboard = build_keyboard(items)
                if not items:
                    send_message("Parabéns, você não possui tarefas pendentes.", chat, keyboard)
                else:
                    send_message("Qual tarefa concluiu?", chat, keyboard)
            elif text in items:
                db.delete_item(text, chat)
                items = db.get_items(chat)
                keyboard = build_keyboard(items)
                send_message("Selecione uma tarefa para concluir", chat, keyboard)
            elif text == "/start":
                send_message("Olá eu sou a Trix, serei sua assistente pessoal para gerenciar suas atividades do dia a dia. Me envie qualquer texto e já adicionarei a sua lista de TO-DO. Envie /done para finalizar uma tarefa. O que está esperando? 'Get Things Done' ;)", chat)
            elif text.startswith("/"):
                continue
            else:
                db.add_item(text, chat)
                items = db.get_items(chat)
                message = "\n".join(items)
                send_message(message, chat)
        except KeyError:
            pass

def get_last_chat_info(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    text.encode('utf-8')
    return (text, chat_id)

def send_message(text, chat_id, reply_markup=None):
    print("Received: "+text)
    text1 = urllib.parse.quote_plus(text)
    print("Must send: " + text1)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def main():
    db.setup()
    last_update_id = None
    while True:
        print("Getting Updates")
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)

if __name__ == '__main__':
    main()
