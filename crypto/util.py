import botimpl
import os
import requests
import pylab
import json

markets = ['bin', 'bitf']
full_name = {'bin': 'Binance', 'bitf': 'Bitfinex'}
usd = {'bin': 'USDT', 'bitf': 'USD'}
usdr = {'bin': 'TUSD', 'bitf': 'USD'}

binance_periods = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']

minutes = {
    'minutes': 1, 'minute': 1, 'm': 1,
    'hours': 60, 'hour': 60, 'h': 60,
    'days': 60 * 24, 'day': 60 * 24, 'd': 60 * 24,
    'weeks': 60 * 24 * 7, 'week': 60 * 24 * 7, 'w': 60 * 24 * 7,
    'months': 60 * 24 * 30, 'month': 60 * 24 * 30, 'M': 60 * 24 * 30
}

possible_queries = ['max', 'min', 'amplitude', 'change', 'trades']


class CryptobotError(Exception):
    pass


def validate(tokens, type):
    # TODO(kefaa): check whitespaces in queries

    tokens = tokens[:4]
    amount, from_cur, to_cur, market = map(str, tokens)

    try:
        amount = type(amount)
        if amount <= 0:
            raise CryptobotError()
    except Exception as e:
        raise CryptobotError("Sorry, first argument should be a positive {} number".format(str(type).split("'")[1]))

    from_cur = from_cur.upper()
    to_cur = to_cur.upper()
    market = market.lower()
    if market not in markets:
        raise CryptobotError("Sorry, MARKET should be in {}".format(markets))

    if from_cur.startswith('USD'):
        from_cur = usdr[market]
    if to_cur.startswith('USD'):
        to_cur = usd[market]
    return amount, from_cur, to_cur, market


def validate_analytics(tokens):
    queries = tokens[5:]
    tokens = tokens[:5]
    from_cur, to_cur, market, amount, period = map(str, tokens)

    from_cur = from_cur.upper()
    to_cur = to_cur.upper()
    market = market.lower()

    try:
        amount = int(amount)
        if amount <= 0:
            raise CryptobotError()
    except Exception as e:
        raise CryptobotError("Sorry, first argument should be a positive int number")

    if period not in minutes:
        raise CryptobotError('Sorry, wrong period ({}), please follow the format specified by /help '.format(period))

    if market not in markets:
        raise CryptobotError("Sorry, MARKET should be in {}".format(markets))

    if from_cur.startswith('USD'):
        from_cur = usdr[market]
    if to_cur.startswith('USD'):
        to_cur = usd[market]

    q_minutes = minutes[period] * amount
    print(q_minutes)
    for per in binance_periods:
        unit = int(per[:-1]) * minutes[per[-1]]
        if unit * 1000 >= q_minutes:
            return from_cur, to_cur, market, per, q_minutes // unit, queries

    raise CryptobotError("Sorry, ask please less than for 1000 months")


def parse_track(msg):
    tokens = msg.split(' ')
    if len(tokens) < 4:
        try:
            result = parse_track('{} {} {} {}'.format(1, tokens[0], usd[tokens[1]], tokens[1]))
            return result
        except Exception:
            if not len(tokens) == 2:
                raise CryptobotError("Sorry, you entered invalid number of arguments,"""
                                     """ please follow the format specified by /help""")
            raise CryptobotError("Sorry, you entered invalid arguments,"""
                                 """ for the second version of /track, please follow the format specified by /help""")
    return validate(tokens, float)


def parse_deals(msg):
    tokens = msg.split(' ')
    tokens = list(filter(lambda x: x, tokens))
    if len(tokens) < 4:
        raise CryptobotError("Sorry, you entered invalid number of arguments,"""
                             """ please follow the format specified by /help""")

    return validate(tokens, int)


def parse_tracker(msg):
    tokens = msg.split(' ')
    tokens = list(filter(lambda x: x, tokens))
    if len(tokens) < 4:
        raise CryptobotError("Sorry, you entered invalid number of arguments,"""
                             """ please follow the format specified by /help""")

    return validate(tokens, float)


def parse_analytics(msg):
    tokens = msg.split(' ')
    tokens = list(filter(lambda x: x, tokens))
    if len(tokens) < 5:
        raise CryptobotError("Sorry, you entered invalid number of arguments,"""
                             """ please follow the format specified by /help""")

    return validate_analytics(tokens)


def parse_klines(klines):
    klines = json.loads(klines)
    new_klines = list()
    print()
    for item in klines:
        new_klines.append([float(item[1]), float(item[2]), float(item[3]), float(item[4]), float(item[5]), int(item[8])])
    return new_klines


def print_plot(symbol, klines):
    klines = parse_klines(klines)
    x = list()
    y = list()
    for index, item in enumerate(klines):
        x.append(index)
        y.append(item[0])
    pylab.plot(x, y, label=symbol)
    pylab.xlabel("checkpoints")
    pylab.ylabel("price")
    pylab.legend()
    pylab.savefig('pic.png')
    pylab.clf()


class AnalyticsHelper:

    @staticmethod
    def ask_min(klines):
        res = klines[0][2]
        for x in klines:
            res = min(res, x[2])
        return res

    @staticmethod
    def ask_max(klines):
        res = klines[0][1]
        for x in klines:
            res = max(res, x[1])
        return res

    @staticmethod
    def ask_amplitude(klines):
        return AnalyticsHelper.ask_max(klines) - AnalyticsHelper.ask_min(klines)

    @staticmethod
    def ask_volume(klines):
        res = 0
        for x in klines:
            res += x[4]
        return res

    @staticmethod
    def ask_change(klines):
        return klines[-1][3] - klines[0][0]

    @staticmethod
    def ask_trades(klines):
        res = 0
        for x in klines:
            res += x[5]
        return res


def analytics(klines, queries):
    klines = parse_klines(klines)
    if not queries:
        queries = possible_queries

    reply = dict()
    for query in queries:
        if query not in queries:
            continue
        if query == 'min':
            reply[query] = AnalyticsHelper.ask_min(klines)
        if query == 'max':
            reply[query] = AnalyticsHelper.ask_max(klines)
        if query == 'amplitude':
            reply[query] = AnalyticsHelper.ask_amplitude(klines)
        if query == 'change':
            reply[query] = AnalyticsHelper.ask_change(klines)
        if query == 'trades':
            reply[query] = AnalyticsHelper.ask_trades(klines)
    return reply


def check_task(data):
    chat, start_price, required_price, from_cur, to_cur, market = data

    param = {'symbol': "{}{}".format(from_cur, to_cur)}
    response = requests.get("{}/track_{}".format(os.environ['URL'], market), params=param)

    if response.status_code != 200:
        raise CryptobotError("Sorry, unable to find conversion from {} to {} in {}".format(
            from_cur, to_cur, full_name[market]))

    price = float(response.text)
    if price <= required_price <= start_price or start_price <= required_price <= price:
        botimpl.bot.send_message(chat, 'For job {} the price required is reached: {}. '
                                       'This job is no longer tracked.'.format(data[2:], price))
        return False
    return True


def monitor():
    monitor.tasks = list(filter(lambda x: check_task(x), monitor.tasks))


def append_task(task):
    monitor.tasks.append(task)
