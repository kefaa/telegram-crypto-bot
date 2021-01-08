import os
import requests
import json

from apscheduler.schedulers.background import BackgroundScheduler
import telebot

import util


os.environ['URL'] = "https://shrouded-reaches-16356.herokuapp.com"
os.environ['TOKEN'] = ""
bot = telebot.TeleBot(os.environ['TOKEN'])

scheduler = BackgroundScheduler()
util.monitor.tasks = list()
scheduler.add_job(util.monitor, 'interval', seconds=30)
scheduler.start()


@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.chat.id, "Hi, {}, I'm cryptobot!".format(message.from_user.first_name))


@bot.message_handler(commands=['help'])
def show_help(message):

    markets = {
        'bin': 'Binance, https://www.binance.com/',
        'bitf': 'Bitfinex, https://www.bitfinex.com/'
    }

    commands = {
        '/help': 'list of commands I can perform',

        '/news [X]': 'ask me to show latest cryptonews (at most X, X is optional, 3 by default)',

        '/track X FROM TO MARKET': """ask me how much are X units of FROM currency worth in TO currency in MARKET."""
                                   """ FROM, TO - currencies, abbreviated as in MARKET."""
                                   """ List of the abbreviations you can find by the appropriate link of the MARKET""",

        '/track CUR MARKET': """ask me for CUR currency in USD in MARKET."""
                             """ The same behavior as if you ask me '/track 1 CUR USD MARKET'""",

        '/deals N FROM TO MARKET': """ask me to show N latest FROM-TO trades in MARKET."""
                                   """ FROM, TO - currencies, abbreviated as in MARKET."""
                                   """ List of the abbreviations you can find by the appropriate link of the MARKET""",

        '/append_tracker PRICE FROM TO MARKET': """ask me to notify you when FROM-TO price reaches PRICE in MARKET. """
                                                """It means, if current price is X and X > PRICE you will be notified"""
                                                """ when price Y at that moment will be less than PRICE, and vise v"""
                                                """ersa. FROM, TO - currencies, abbreviated as in MARKET. List of the"""
                                                """ abbreviations you can find by the appropriate link of the MARKET""",

        '/plot FROM TO MARKET X TIME_TYPE': """ask me to draw plot of FROM-TO price for last X minutes/hours/"""
                                            """days/weeks/months. Please note that data is taken from Binance which """
                                            """ founded in September, 2017""",

        '/analytics FROM TO MARKET X TIME_TYPE QUERY1 QUERY2 ...': """ask me for analytics queries of FROM-TO price """
                                                                   """for last X minutes/hours/days/weeks/months. """
                                                                   """Queries can be as follows:"""
    }

    queries = {
        'max': 'maximum price for period',
        'min': 'minimum price for period',
        'amplitude': 'absolute difference of prices for period',
        'volume': 'total volume for period',
        'change': 'difference of prices between endpoints of period',
        'trades': 'total number of trades for period'
    }

    reply = "MARKETS:\n"
    for market, descr in markets.items():
        reply += '{} -- {}.\n'.format(market, descr)
    reply += "\nCOMMANDS:\n"
    for comm, descr in commands.items():
        reply += '\n{} -- {}.\n'.format(comm, descr)
    for query, descr in queries.items():
        reply += '{} -- {}.\n'.format(query, descr)

    reply += "\n"
    reply += """Unfortunately, /plot and /analytics for Bitfinex is not supported"""

    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['news'])
def show_news(message):
    result = list(requests.get("{}/news".format(os.environ['URL'])).text.split(','))
    amount = 3

    text = message.text[6:]
    if text.isdigit():
        x = int(text)
        amount = (x if x > 0 else 0)
    elif text:
        amount = 0

    if amount == 0:
        bot.send_message(message.chat.id, "Sorry, I can show you only positive integer number of news!")
    result = result[:amount]
    for link in result:
        bot.send_message(message.chat.id, link)


@bot.message_handler(commands=['track'])
def track_coins(message):
    try:
        (amount, from_cur, to_cur, market) = util.parse_track(message.text[7:])

        param = {'symbol': "{}{}".format(from_cur, to_cur)}
        response = requests.get("{}/track_{}".format(os.environ['URL'], market), params=param)

        if response.status_code != 200:
            raise util.CryptobotError("Sorry, unable to find conversion from {} to {} in {}".format(
                from_cur, to_cur, util.full_name[market]))

        price = float(response.text)

        total = round(price * amount, 8)
        bot.send_message(message.chat.id,
                         "{} {} to {} = {} ({})".format(amount, from_cur, to_cur, total, util.full_name[market]))

    except util.CryptobotError as e:
        bot.send_message(message.chat.id, str(e))


@bot.message_handler(commands=['deals'])
def show_deals(message):
    try:
        (amount, from_cur, to_cur, market) = util.parse_deals(message.text[7:])
        amount = min(amount, 1000)

        param = {
            'symbol': '{}{}'.format(from_cur, to_cur),
            'limit' if market == 'bin' else 'limit_trades': str(amount)
        }
        response = requests.get("{}/deals_{}".format(os.environ['URL'], market), params=param)

        if response.status_code != 200:
            raise util.CryptobotError("Sorry, unable to find {}-{} trades in {}".format(
                from_cur, to_cur, util.full_name[market]))

        trades = json.loads(response.text)
        bot.send_message(message.chat.id, 'Latest {} deals from {} to {} in {}:'.format(
            amount, from_cur, to_cur, util.full_name[market]))

        for deal in trades:
            price = float(deal['price'])
            qty = float(deal['qty' if market == 'bin' else 'amount'])
            bot.send_message(message.chat.id, "price per unit = {}, amount = {}, total price = {}".format(
                price, qty, price * qty))

    except util.CryptobotError as e:
        bot.send_message(message.chat.id, str(e))


@bot.message_handler(commands=['append_tracker'])
def append_tracker(message):
    try:
        (amount, from_cur, to_cur, market) = util.parse_track(message.text[16:])

        param = {'symbol': "{}{}".format(from_cur, to_cur)}
        response = requests.get("{}/track_{}".format(os.environ['URL'], market), params=param)

        if response.status_code != 200:
            raise util.CryptobotError("Sorry, unable to find conversion from {} to {} in {}".format(
                from_cur, to_cur, util.full_name[market]))

        price = float(response.text)

        task = (message.chat.id, price, amount, from_cur, to_cur, market)
        util.append_task(task)

        bot.send_message(message.chat.id, 'Thank you, job {} was successfully added, '
                                          'current price = {}'.format(task[2:], price))

    except util.CryptobotError as e:
        bot.send_message(message.chat.id, str(e))


@bot.message_handler(commands=['plot'])
def plot(message):
    try:
        (from_cur, to_cur, market, period, limit, _) = util.parse_analytics(message.text[6:])

        print(period, limit)
        param = {'symbol': "{}{}".format(from_cur, to_cur),
                 'interval': period,
                 'limit': limit}
        response = requests.get("{}/candlestick_{}".format(os.environ['URL'], market), params=param)

        if response.status_code != 200:
            if response.text.startswith('Unfortunately'):
                raise util.CryptobotError(response.text)
            raise util.CryptobotError("Sorry, unable to find conversion from {} to {} in {}".format(
                from_cur, to_cur, util.full_name[market]))

        util.print_plot("{}{}".format(from_cur, to_cur), response.text)
        pic = open('pic.png', 'rb')
        bot.send_chat_action(message.chat.id, 'upload_photo')
        bot.send_photo(message.chat.id, pic)

    except util.CryptobotError as e:
        bot.send_message(message.chat.id, str(e))


@bot.message_handler(commands=['analytics'])
def analytics(message):
    try:
        (from_cur, to_cur, market, period, limit, queries) = util.parse_analytics(message.text[11:])
        param = {'symbol': "{}{}".format(from_cur, to_cur),
                 'interval': period,
                 'limit': limit}
        response = requests.get("{}/candlestick_{}".format(os.environ['URL'], market), params=param)

        if response.status_code != 200:
            if response.text.startswith('Unfortunately'):
                raise util.CryptobotError(response.text)
            raise util.CryptobotError("Sorry, unable to find conversion from {} to {} in {}".format(
                from_cur, to_cur, util.full_name[market]))

        reply = util.analytics(response.text, queries)
        for query, answer in reply.items():
            bot.send_message(message.chat.id, '{}: {}'.format(query, answer))

    except util.CryptobotError as e:
        bot.send_message(message.chat.id, str(e))


# SHOULD BE THE LAST ONE!!!
@bot.message_handler(content_types=['text'])
def undefined_message(message):
    bot.send_message(message.chat.id, "Sorry, can't understand you :(")
    bot.send_message(message.chat.id, "Use /help to see list of commands")
