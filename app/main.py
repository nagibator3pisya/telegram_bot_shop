import asyncio

from aiogram import F, Dispatcher
from aiogram.enums import ContentType

from app.config import bd, bot
from app.user.user_hendler import user_router, pre_checkout_handler, successful_payment_handler, \
    process_category,process_test_payment

bd.include_router(user_router)
def register_handlers(dp: Dispatcher):
        dp.callback_query.register(process_category, lambda c: c.data and c.data.startswith('category_'))
        dp.callback_query.register(process_test_payment, lambda c: c.data and c.data.startswith('pay_stars_'))
        dp.pre_checkout_query.register(pre_checkout_handler)
        dp.message.register(successful_payment_handler, F.content_type == ContentType.SUCCESSFUL_PAYMENT)


register_handlers(bd)

# bd.message.register(process_star_payment)
# bd.pre_checkout_query(pre_checkout_handler)
# bd.message.register(successful_payment_handler)


async def main():
    await bd.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())