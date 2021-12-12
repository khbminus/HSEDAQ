from tg.bot import Bot
from telebot.types import CallbackQuery
from tg.keyboards import main_menu, tournament_menu

bot = Bot().bot


@bot.callback_query_handler(func=lambda x: x.data == 'back_main')
def callback_back_to_main(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    response_text = 'Choose action: '
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text=response_text, reply_markup=main_menu())


@bot.callback_query_handler(func=lambda x: x.data == 'back_tour')
def callback_back_to_tournament(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    response_text = 'Choose action: '
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text=response_text,
                          reply_markup=tournament_menu())
