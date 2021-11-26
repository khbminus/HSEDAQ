from tg.bot import Bot
from telebot.types import Message
from db.types import User
from db.users import get_user, save_user
from db.tournaments import get_tournament
from loguru import logger

bot = Bot().bot


@bot.message_handler(commands=['status'])
def command_status(message: Message):
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

    if user.tournament_id is None or (tournament := get_tournament(user.tournament_id)) is None:
        bot.send_message(chat_id=cid, text="You are currently doesn't participate in tournament")
    else:
        status = ''
        if not tournament.is_started:
            status = "Not started"
        elif not tournament.is_ended:
            status = "Running"
        bot.send_message(chat_id=cid, text=f"Status: {status}\n"
                                           f"Your money: {user.money}\n"
                                           f"Portfolio:  NaN")
