from tg.bot import Bot
from telebot.types import Message

bot = Bot().bot


@bot.message_handler(commands=['help', 'commands'])
def get_help(message: Message):
    cid = message.chat.id

    bot.send_message(chat_id=cid, text=f"""
Generic commands:
`/enter <id>` -- enter at tournament with specific id
You can't leave from a running tournament, but you can leave from an ended/not started tournament.

`/create_tournament <start time> <finish time>` -- create an tournament (time in strictly ISO-8601 format)

`/about_me` -- get some information about You)

Tournament commands:
`/prices` -- get current prices

`/buy|sell <symbol> <amount>` -- buy/sell some amount of company

`/short|return <symbol> <amount>` -- short or return short. (Borrow due is 24 hours)

`/stats` --- get list of players

`/status` --- get some status (tournament status, money, portfolio)
    """)
