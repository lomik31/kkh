# Инструкция по установке

## Перед установкой
Убедитесь, что на вашем компьютере (сервере) установлен `python3`, `nodejs` и `npm`

## Установить зависимости
```
npm i
python -m pip install -r requirements.txt
```

## Настройка конфига
1. Вам необходимо получить токен яндекс диска (для бекапов в облако), а так же токены ботов соответствующих клиентов (discord/telegram).
2. В файле `config.json.example` указываете ваши токены. Если вам не нужен один из клиентов, его токен можно не получать и указать там пустую строку. При этом, вы не должны будете запускать соответствующий файл клиента.
3. В параметре `websocketIp` необходимо указать ip машины и через двоеточие порт, на котором запущен сервер. Если вы запускаете клиенты и сервер на локальной машине, то установите значение `localhost:3200`
4. Переименуйте `config.json.example` в `config.json`

## Запустить сервер
```
node main.js
```
Прослушивает `0.0.0.0:3200`



## Запуск клиентов
Запустите клиент telegram командой `python telegram-client.py` и клиент discord командой `python discord-client.py`.
Если вы все сделали правильно, в консоли каждый из клиентов скажет, что соединение открыто, а в консоли сервера будет указано, какие именно клиенты сейчас подключены
