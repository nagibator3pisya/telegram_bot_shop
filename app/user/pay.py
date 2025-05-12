# from aiogram.types import LabeledPrice, Message
#
#
# async def send_invoice_handler(message: Message):
#     prices = [LabeledPrice(label="XTR", amount=20)]
#     await message.answer_invoice(
#         title="Поддержка канала",
#         description="Поддержать канал на 20 звёзд!",
#         prices=prices,
#         provider_token="",
#         payload="channel_support",
#         currency="XTR",
#         reply_markup=payment_button(),
#     )