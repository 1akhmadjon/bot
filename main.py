import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


API_TOKEN = '6338497392:AAGfIbiSMt4qTb7HX-LYeFcnYfQIfl7Wn4M'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



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

    elif text.startswith("https://www.instagram.com/"):
        result = get_ig_vd(text)
        await message.answer_video(result)
    elif text.startswith(("https://vt.tiktok.com/", "https://tiktok.com")):
        result = tiktok_vd(text)
        await message.answer_video(result)
    else:
        await message.answer("Please send a valid YouTube or Instagram URL.")



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
        await bot.send_audio(chat_id=callback_query.from_user.id, audio=result)
    await callback_query.message.delete()
    await callback_query.answer()

async def main():
    await dp.start_polling(bot)

def get_yt_mp3(vd_url):
	url = "https://youtube-mp3-downloader2.p.rapidapi.com/ytmp3/ytmp3/"

	querystring = {"url": vd_url}

	headers = {
		"x-rapidapi-key": "eea3e289a0msh912ea349e900e8fp19ac32jsn215363fc2737",
		"x-rapidapi-host": "youtube-mp3-downloader2.p.rapidapi.com"
	}

	response = requests.get(url, headers=headers, params=querystring)
	return response.json()['dlink']


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
	data = response.json()

	return data['url']

def tiktok_vd(vd_url):
	url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"

	payload = {"url": vd_url}
	headers = {
		"x-rapidapi-key": "eea3e289a0msh912ea349e900e8fp19ac32jsn215363fc2737",
		"x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com",
		"Content-Type": "application/json"
	}

	response = requests.post(url, json=payload, headers=headers)
	medias = response.json().get('medias', {})
	video_url = medias[1].get('url', None)
	return video_url

if __name__ == '__main__':
    asyncio.run(main())
