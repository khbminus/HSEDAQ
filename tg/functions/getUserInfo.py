from tg.bot import Bot
from telebot.types import Message
from db.users import get_user
from tg.tournaments import get_float

bot = Bot().bot


@bot.message_handler(commands=['get_user', 'about_me'])
def command_get_user(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
    # TODO: do it better
    response_text = \
        f'''
Your first name: {user.first_name},
Your last name: {user.last_name},
Are you participating in tournament rn: {"Yes" if user.tournament_id != -1 else "No (default tournament)"}'''
    response_text += f'\nTournament id: {user.tournament_id}\nCurrent money: ${get_float(user.money)}'

    bot.send_message(chat_id=cid, text=response_text)
