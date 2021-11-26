from tg.bot import Bot
from telebot.types import Message
from db.types import User
from db.users import get_user, save_user
from loguru import logger

bot = Bot().bot


@bot.message_handler(commands=['get_user', 'about_me'])
def command_get_user(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
    if user is None:
        bot.send_message(chat_id=cid, text="Wow, you aren't in the database... Strange, I'll report this")
        logger.error(f"User {user} isn't have record in the database, but using functions")
        user = User(
            user_id=uid,
            chat_id=cid,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name)
        save_user(user)
    # TODO: do it better
    response_text = \
        f'''
Your first name: {user.first_name},
Your last name: {user.last_name},
Are you participating in tournament rn: {"Yes" if user.tournament_id is not None else "No"}'''
    if user.tournament_id is not None:
        response_text += f'\nTournament id: {user.tournament_id}\nCurrent money: ${user.money}'

    bot.send_message(chat_id=cid, text=response_text)
