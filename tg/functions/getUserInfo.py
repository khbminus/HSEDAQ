from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from db.users import get_user
from tg.tournaments import get_float
from tg.keyboards import back_to_main
from loguru import logger

bot = Bot().bot


@bot.message_handler(commands=['get_user', 'about_me'])
def command_get_user(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
    response_text = \
        f'''
Your first name: {user.first_name},
Your last name: {user.last_name},
Are you participating in tournament rn: {"Yes" if user.tournament_id != -1 else "No (default tournament)"}'''
    response_text += f'\nTournament id: {user.tournament_id}\nCurrent money: ${get_float(user.money)}'
    bot.send_message(chat_id=cid, text=response_text, reply_markup=back_to_main())


@bot.callback_query_handler(func=lambda x: x.data == 'about_me')
def callback_get_user(call: CallbackQuery) -> None:
    message = call.message
    cid = message.chat.id

    user = get_user(cid)

    response_text = \
        f'''
Your first name: {user.first_name},
Your last name: {user.last_name},
Are you participating in tournament rn: {"Yes" if user.tournament_id != -1 else "No (default tournament)"}'''
    response_text += f'\nTournament id: {user.tournament_id}\nCurrent money: ${get_float(user.money)}'
    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text=response_text, reply_markup=back_to_main())
