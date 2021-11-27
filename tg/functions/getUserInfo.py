from tg.bot import Bot
from telebot.types import Message
from db.users import get_user

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
Are you participating in tournament rn: {"Yes" if user.tournament_id is not None else "No"}'''
    if user.tournament_id is not None:
        response_text += f'\nTournament id: {user.tournament_id}\nCurrent money: ${user.money:.3f}'

    bot.send_message(chat_id=cid, text=response_text)
