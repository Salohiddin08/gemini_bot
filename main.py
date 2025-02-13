import os
import csv
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import google.generativeai as genai

# Konfiguratsiyalar
load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

CSV_FILE = "users.csv"


# CSV faylga ma'lumot saqlash funksiyasi
def save_user_to_csv(chat_id: int, username: str, first_name: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists or file.tell() == 0:
            writer.writerow(["Chat ID", "Username", "First Name", "Timestamp"])
        writer.writerow([chat_id, username or "N/A", first_name or "N/A", timestamp])


# Bot ishga tushganda terminalga xabar
@dp.startup()
async def on_startup():
    print("🤖 Bot ishga tushdi!")


# /start komandasi
@dp.message(Command("start"))
async def start(message: types.Message):
    greeting = """
🌍 *Assalomu alaykum!* (O'zbekcha)
🖐️ *Hello!* (English)
🇷🇺 *Здравствуйте!* (Русский)

_Qanday yordam bera olaman?_ 😊
    """
    await message.answer(greeting, parse_mode=ParseMode.MARKDOWN)


# AI javobi va foydalanuvchi ma'lumotlarini saqlash
@dp.message()
async def ai_response(message: types.Message):
    # Foydalanuvchi ma'lumotlarini saqlash
    user = message.from_user
    save_user_to_csv(user.id, user.username, user.first_name)

    # AI javobi
    try:
        response = model.generate_content(message.text)
        await message.answer(response.text)
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {str(e)}")


if __name__ == "__main__":
    dp.run_polling(bot)