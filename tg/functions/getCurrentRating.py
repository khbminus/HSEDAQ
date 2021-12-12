from tg.bot import Bot
from telebot.types import Message, CallbackQuery
from db.users import get_user
from db.tournaments import get_tournament, get_tournament_participants
from tg.tournaments import get_statistics
from tg.keyboards import back_to_tournament

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


@bot.callback_query_handler(func=lambda c: c.data == 'rating')
def callback_status(call: CallbackQuery):
    message = call.message
    cid = message.chat.id

    user = get_user(cid)
    tournament = get_tournament(user.tournament_id)
    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text="Processing...", reply_markup=None)
    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text=get_statistics(tournament, get_tournament_participants(tournament)),
                          reply_markup=back_to_tournament())
