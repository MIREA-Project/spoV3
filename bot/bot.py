import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot_source_dir import handlers
from bot_source_dir.config import load_config

# main file of bot
config = load_config()
token = config.bot_token

# logger initializing
logger = logging.getLogger(__name__)


# configuration and turn on bot
async def start_bot():
    # configurate logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=token)

    dp: Dispatcher = Dispatcher()
    dp.include_router(handlers.router_main)
    # set main menu
    # await set_main_menu(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())
