from tg.bot import Bot
from telebot.types import CallbackQuery, InlineKeyboardButton
from tg.keyboards import main_menu, tournament_menu
from db.users import get_user, save_user

bot = Bot().bot


@bot.callback_query_handler(func=lambda x: x.data == 'back_main')
def callback_back_to_main(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    response_text = 'Choose action: '
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text=response_text, reply_markup=main_menu())


@bot.callback_query_handler(func=lambda x: x.data == 'leave')
def callback_leave(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    response_text = 'Choose action: '
    user = get_user(cid)
    user.tournament_id = -1
    user.money = 1000
    save_user(user)
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text=response_text, reply_markup=main_menu())


@bot.callback_query_handler(func=lambda x: x.data == 'back_tour')
def callback_back_to_tournament(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    response_text = 'Choose action: '
    user = get_user(cid)
    keyboard = tournament_menu()
    if user.tournament_id == -1:
        keyboard.keyboard.append([InlineKeyboardButton(text='Back to main menu', callback_data='back_main')])
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text=response_text,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda x: x.data == 'del')
def callback_delete_message(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    bot.delete_message(chat_id=cid, message_id=message.message_id)
