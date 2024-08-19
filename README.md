# HUB BOT
Telegram bot that can replace a paid livegram bot

The bot is added to a group in which topics are allowed, it is granted administrator rights, after which the messages of people who write to the bot are forwarded to separate topics in the group. Administrators can communicate with users in the topics created for them by the bot and conduct individual dialogues with them.
Also, with the help of the bot, you can make global and targeted mailings to users whose data is stored in the MongoDB database

Ubuntu 22.04:

1) Apt install docker.io docker-compose -y

2) Copy app to server

3) In project dir: sudo docker-compose up -d --build

Commands:

1. sudo docker ps -a | list all running containers

2. sudo docker stop <container name> | stop container

3. sudo docker rm <container name> | remove container

