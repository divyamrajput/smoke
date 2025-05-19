#first do install modules pip3 install python-telegram-bot --upgrade then run nohup python3 terminal.py

import sys
import os
import time
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import asyncio

BOT_TOKEN = '7572496256:AAFhrnEBaAyoMkJI_xvuaSL6jwdCJD_Prt8'
ALLOWED_USER_ID = 2115570191
current_dir = os.path.expanduser("~")

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_dir
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Unauthorized access.")
        return

    command = update.message.text.strip()

    if command.startswith("cd "):
        path = command[3:].strip()
        new_dir = os.path.abspath(os.path.join(current_dir, path))
        if os.path.isdir(new_dir):
            current_dir = new_dir
            await update.message.reply_text(f"Changed directory to: {current_dir}")
        else:
            await update.message.reply_text(f"No such directory: {new_dir}")
        return

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=current_dir,
            timeout=30
        )
        output = result.stdout.strip() + "\n" + result.stderr.strip()
        output = output.strip()
        if not output:
            output = "(No output)"
    except Exception as e:
        output = f"Error: {str(e)}"

    for i in range(0, len(output), 4000):
        await update.message.reply_text(output[i:i+4000])

async def keep_alive():
    while True:
        try:
            subprocess.run("echo 'ping' > /dev/null", shell=True)
        except Exception as e:
            print(f"Keep-alive error: {str(e)}")
        await asyncio.sleep(300)

def restart_bot():
    os.execv(sys.executable, ['python3'] + sys.argv)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_command))

if __name__ == '__main__':
    print("Bot running...")

    loop = asyncio.get_event_loop()
    loop.create_task(keep_alive())

    try:
        app.run_polling()
    except Exception as e:
        print(f"Error encountered: {str(e)}")
        print("Restarting bot...")
        restart_bot()
