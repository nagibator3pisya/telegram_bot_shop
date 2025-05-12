import asyncio
from app.config import bd, bot
from app.user.user_hendler import user_router




bd.include_router(user_router)


async def main():
    await bd.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())