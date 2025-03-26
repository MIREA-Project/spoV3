from aiogram import Router
from aiogram.types import Message
from aiogram import F

from lexicon import COMMAND_LEXICON

command_router: Router = Router()


# commands router file

@command_router.message(F.text == '/start')
async def hello_world(message: Message):
    await message.reply(text=COMMAND_LEXICON['start'])
