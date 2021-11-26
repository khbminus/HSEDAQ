from tg.bot import Bot
from telebot.types import Message
from db.users import get_user
from db.tournaments import get_tournament

bot = Bot().bot


@bot.message_handler(commands=['status'])
def command_status(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
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
