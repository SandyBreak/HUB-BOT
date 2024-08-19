# HUB BOT
Telegram bot that can replace a paid livegram bot

The bot is added to a group in which topics are allowed, it is granted administrator rights, after which the messages of people who write to the bot are forwarded to separate topics in the group. Administrators can communicate with users in the topics created for them by the bot and conduct individual dialogues with them.
Also, with the help of the bot, you can make global and targeted mailings to users whose data is stored in the MongoDB database

How to deploy:

Ubuntu 22.04:

1) Apt install docker.io docker-compose -y

2) git clone https://github.com/SandyBreak/HUB_BOT.git | Copy app to server

3) Change mongodb pass&login and telegram_token in docker-compose.env 

4) In project dir: sudo docker-compose up -d --build

5) How to connect using mongodb compass: mongodb://{mongodb_login}:{mongodb_password}@{sever_ip_adress}:27021/

Commands:

1. sudo docker ps -a | list all running containers

2. sudo docker stop <container name> | stop container

3. sudo docker rm <container name> | remove container

4. sudo docker-compose down | stop&remove containers
