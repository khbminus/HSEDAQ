from typing import Any, List, TypeVar

from telebot import types
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter
from telebot.types import CallbackQuery
from db.stocks import tickers, get_price, get_longs_portfolio, get_shorts_portfolio
from tg.utils import get_float
from tg.bot import Bot

bot = Bot().bot


def main_menu():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [types.InlineKeyboardButton(text="New tournament", callback_data="new")],
            [types.InlineKeyboardButton(text="Enter to existing tournament", callback_data="enter")],
            [types.InlineKeyboardButton(text="About me", callback_data="about_me")],
            [types.InlineKeyboardButton(text='Tournament menu', callback_data="back_tour")]
        ]
    )


def tournament_menu():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [types.InlineKeyboardButton(text="Buy a stock", callback_data="buy"),
             types.InlineKeyboardButton(text="Sell a stock", callback_data="sell")],
            [types.InlineKeyboardButton(text="Short a stock", callback_data="short"),
             types.InlineKeyboardButton(text='Return a short', callback_data="return")],
            [types.InlineKeyboardButton(text="Get status", callback_data="status"),
             types.InlineKeyboardButton(text="Rating", callback_data="rating")]
        ]
    )


def back_to_main():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [types.InlineKeyboardButton(text="Back", callback_data="back_main")]
        ]
    )


def back_to_tournament():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [types.InlineKeyboardButton(text="Back", callback_data="back_tour")]
        ]
    )


def leave_tournament():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [types.InlineKeyboardButton(text="Leave tournament", callback_data="leave")]
        ]
    )


def delete_button():
    return types.InlineKeyboardMarkup(
        keyboard=[
            [types.InlineKeyboardButton(text="Delete this message", callback_data="del")]
        ]
    )


T = TypeVar('T')


def get_pages(arr: List[T], page_size: int) -> List[List[T]]:
    pages = []
    for i in range(0, len(arr), page_size):
        pages.append(arr[i:i + page_size])
    return pages


stock_pages_factory = CallbackData('page', 'type', prefix="pages")
sell_return_page_factory = CallbackData('page', 'type', 'uid', 'tid', 'text', prefix="pages2")


class PagesCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class SellReturnPagesCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


bot.add_custom_filter(PagesCallbackFilter())
bot.add_custom_filter(SellReturnPagesCallbackFilter())


def get_stocks_menu(page: int, factory: CallbackData):
    pages = get_pages(tickers, 10)
    now = pages[page]
    markup = []
    for i in range(0, len(now), 2):
        markup.append([types.InlineKeyboardButton(text=f"{symbol}: ${get_float(get_price(symbol))}",
                                                  callback_data=factory.new(symbol=symbol)) for symbol in
                       now[i:i + 2]])
    markup.append(
        [types.InlineKeyboardButton(text="⬅",
                                    callback_data=stock_pages_factory.new(page=page - 1, type=factory.prefix)),
         types.InlineKeyboardButton(text=f"{page + 1}/{len(pages)}", callback_data="page_num"),
         types.InlineKeyboardButton(text="➡",
                                    callback_data=stock_pages_factory.new(page=page + 1, type=factory.prefix))])
    markup.append([types.InlineKeyboardButton(text="Back to menu", callback_data='back_tour')])
    return types.InlineKeyboardMarkup(keyboard=markup)


@bot.callback_query_handler(func=None, config=stock_pages_factory.filter())
def callback_buy_prev_page(call: CallbackQuery) -> None:
    callback_data = stock_pages_factory.parse(callback_data=call.data)
    message = call.message
    cid = message.chat.id

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Processing...",
                          reply_markup=None)

    factory = None
    if callback_data['type'] == 'buy':
        from tg.functions.buyCommand import buy_factory
        factory = buy_factory
    elif callback_data['type'] == 'short':
        from tg.functions.shortCommand import short_factory
        factory = short_factory

    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text=f"Choose a stock to {callback_data['type']}:",
                          reply_markup=get_stocks_menu(min(4, max(0, int(callback_data['page']))), factory))


@bot.callback_query_handler(func=None, config=sell_return_page_factory.filter())
def callback_buy_prev_page(call: CallbackQuery) -> None:
    callback_data = sell_return_page_factory.parse(callback_data=call.data)
    message = call.message
    cid = message.chat.id

    bot.edit_message_text(chat_id=cid, message_id=message.message_id, text="Processing...",
                          reply_markup=None)

    factory = None
    if callback_data['type'] == 'sell':
        from tg.functions.sellCommand import sell_factory
        factory = sell_factory
    elif callback_data['type'] == 'return':
        from tg.functions.returnShort import return_short_factory
        factory = return_short_factory

    bot.edit_message_text(chat_id=cid, message_id=message.message_id,
                          text=callback_data['text'],
                          reply_markup=globals()[callback_data['func']](callback_data['uid'], callback_data['tid'],
                                                                        callback_data['page'], factory))


def get_longs_keyboard(uid: int, tid: int, page: int, factory: CallbackData):
    stocks = get_longs_portfolio(uid, tid)
    pages = get_pages(stocks, 5)

    now = pages[page]

    markup = [[types.InlineKeyboardButton(text=f"{long.symbol}: ${get_float(get_price(long.symbol))} "
                                               f"x {long.amount}",
                                          callback_data=factory.new(symbol=long.symbol))] for long in now]
    markup.append(
        [types.InlineKeyboardButton(text="⬅",
                                    callback_data=sell_return_page_factory.new(page=max(0, page - 1),
                                                                               type=factory.prefix,
                                                                               uid=uid, tid=tid,
                                                                               text="Choose a stock to sell")),
         types.InlineKeyboardButton(text=f"{page + 1}/{len(pages)}", callback_data="page_num"),
         types.InlineKeyboardButton(text="➡",
                                    callback_data=sell_return_page_factory.new(page=min(len(pages), page + 1),
                                                                               type=factory.prefix,
                                                                               uid=uid, tid=tid,
                                                                               text="Choose a stock to sell"))])
    markup.append([types.InlineKeyboardButton(text="Back to menu", callback_data='back_tour')])
    return types.InlineKeyboardMarkup(keyboard=markup)


def get_shorts_keyboard(uid: int, tid: int, page: int, factory: CallbackData):
    shorts = list(enumerate(get_shorts_portfolio(uid, tid)))
    pages = get_pages(shorts, 5)

    now = pages[page]

    markup = []
    for i in range(0, len(now), 2):
        markup.append([types.InlineKeyboardButton(text=f"{short.symbol}: ${get_float(get_price(short.symbol))} "
                                                       f"x {short.amount}",
                                                  callback_data=factory.new(symbol=short.symbol, index=i))
                       for i, short in now])

    markup.append(
        [types.InlineKeyboardButton(text="⬅",
                                    callback_data=sell_return_page_factory.new(page=max(0, page - 1),
                                                                               type=factory.prefix,
                                                                               uid=uid, tid=tid,
                                                                               text="Choose a short to return")),
         types.InlineKeyboardButton(text=f"{page + 1}/{len(pages)}", callback_data="page_num"),
         types.InlineKeyboardButton(text="➡",
                                    callback_data=sell_return_page_factory.new(page=min(len(pages), page + 1),
                                                                               type=factory.prefix,
                                                                               uid=uid, tid=tid,
                                                                               text="Choose a short to return"))])
    markup.append([types.InlineKeyboardButton(text="Back to menu", callback_data='back_tour')])
    return types.InlineKeyboardMarkup(keyboard=markup)
