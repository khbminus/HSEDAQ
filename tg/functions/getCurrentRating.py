from tg.bot import Bot
from telebot.types import Message
from db.users import get_user
from db.tournaments import get_tournament, get_tournament_participants
from tg.tournaments import get_statistics

bot = Bot().bot


@bot.message_handler(commands=['rating', 'stats', 'statistics'])
def command_stats(message: Message):
    cid = message.chat.id
    uid = message.from_user.id

    user = get_user(uid)
    if user.tournament_id is None or (tournament := get_tournament(user.tournament_id)) is None:
        bot.send_message(chat_id=cid, text="You are currently doesn't participate in tournament")
    else:

        bot.send_message(chat_id=cid, text=get_statistics(tournament, get_tournament_participants(tournament)))
