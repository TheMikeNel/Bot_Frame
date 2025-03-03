import asyncio
import logging
from services.getconf import Server, Telebot

from app import commands, callbacks, handlers
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

ALLOWED_UPDATES = ["message", "callback_query"]

async def main() -> None:
    logging.basicConfig(level=logging.INFO, filename=f"bot_log.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
    logging.info("Program init...")

    redis_storage = RedisStorage.from_url(Server.redis_url)
    logging.info(f"Redis connection: {await redis_storage.redis.ping()}")

    bot = Bot(token=Telebot.test_token) # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Менять на token в релизе

    dp = Dispatcher(storage=redis_storage)
    dp.include_routers(commands.router, handlers.router, callbacks.router)
    print(f"Routers binded to dispatcher...{(commands.__name__, callbacks.__name__, handlers.__name__)}")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    try: asyncio.run(main())
    except BaseException as e: logging.error(f"Exit with: {e}")