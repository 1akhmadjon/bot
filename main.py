import logging
import os
from dotenv import load_dotenv
import openai
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

API_TOKEN = '6338497392:AAGfIbiSMt4qTb7HX-LYeFcnYfQIfl7Wn4M'
openai.api_key = os.getenv('OPENAI_API_KEY')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def ai_conversation_analysis(user_input):
    system_message = (
        "You have to respond like human user should not to know that you are human "
                    "Do not tell that you are ai or program "
                    "make them think that you are human "
                    "do not user same words or sentences to let user know that your are ai or program"
                    "You have created by developer Ziyovuddinov Axmad"
                    "Ziyovuddinov Axmad is 18 years old Uzbek programmer "
                    "Axmad is from Uzbekistan Tashken "
                    "You have integrated to telegram bot "
                    "Your must answer in language only user wrote you"
                    "Your name is Anna by this name you are as girls "
                    "You have to answer all question that you asked as you can "
                    "If the answer uzbek language you speak uzbek language"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input},
        ],
    )

    ai_response = response.choices[0].message["content"]

    return ai_response


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Hi! Send me a YouTube or Instagram link to get started!")


@dp.message()
async def handle_message(message: types.Message):
    text = message.text

    if text.startswith(("https://youtube.com", "https://youtu.be/")):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Video", callback_data=f"yt_video_{text}")],
            [InlineKeyboardButton(text="MP3", callback_data=f"yt_mp3_{text}")]
        ])
        await message.answer("Choose the format:", reply_markup=keyboard)

    elif text.startswith(("https://www.instagram.com/", "https://instagram.com")):
        result = get_ig_vd(text)
        await message.answer_video(result)
    elif text.startswith(("https://vt.tiktok.com/", "https://tiktok.com")):
        result = tiktok_vd(text)
        await message.answer_video(result)
    else:
        ai_response = await ai_conversation_analysis(text)
        await message.answer(ai_response)



# Callback handler for the inline keyboard
@dp.callback_query(lambda callback_query: callback_query.data.startswith('yt_'))
async def process_callback(callback_query: types.CallbackQuery):
    action = callback_query.data
    vd_url = callback_query.data.split("_", 2)
    if action.startswith('yt_video'):
        result = get_yt_mp4(vd_url[2])
        await callback_query.message.answer_video(result)

    elif action.startswith('yt_mp3'):
        result = get_yt_mp3(vd_url[2])
        # await bot.send_message(chat_id=callback_query.from_user.id,text="Is not working")
        await bot.send_audio(chat_id=callback_query.from_user.id, audio=result)

    await callback_query.message.delete()
    await callback_query.answer()


def get_yt_mp3(vd_url):
    url = "https://yt-search-and-download-mp3.p.rapidapi.com/mp3"

    querystring = {"url": vd_url}

    headers = {
        "x-rapidapi-key": "eea3e289a0msh912ea349e900e8fp19ac32jsn215363fc2737",
        "x-rapidapi-host": "yt-search-and-download-mp3.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    return data['download']



def get_yt_mp4(vd_url):
    url = "https://all-media-downloader1.p.rapidapi.com/all"
    payload = (
        f"-----011000010111000001101001\r\n"
        "Content-Disposition: form-data; name=\"url\"\r\n\r\n"
        f"{vd_url}\r\n"
        "-----011000010111000001101001--\r\n"
    )

    headers = {
        "x-rapidapi-key": "eea3e289a0msh912ea349e900e8fp19ac32jsn215363fc2737",
        "x-rapidapi-host": "all-media-downloader1.p.rapidapi.com",
        "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
    }

    response = requests.post(url, data=payload, headers=headers)
    result = response.json()['url']
    return result


def get_ig_vd(vd_url):
    url = "https://social-all-in-one.p.rapidapi.com/info"

    querystring = {"format": "json", "url": vd_url}

    headers = {
        "x-rapidapi-key": "eea3e289a0msh912ea349e900e8fp19ac32jsn215363fc2737",
        "x-rapidapi-host": "social-all-in-one.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    formats = data.get('formats', [])
    for format in formats:
        if len(format) == 17:
            return format.get('url')


def tiktok_vd(vd_url):
    url = "https://snap-video3.p.rapidapi.com/download"

    payload = {"url": vd_url}

    headers = {
        "x-rapidapi-key": "eea3e289a0msh912ea349e900e8fp19ac32jsn215363fc2737",
        "x-rapidapi-host": "snap-video3.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    medias = response.json().get('medias', {})
    video_url = medias[0].get('url', None)
    return video_url


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
