import random

from botimpl import *

from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def init():
    bot.remove_webhook()
    bot.set_webhook(os.environ['URL'] + '/' + os.environ['TOKEN'])
    return "Kefaa Kurilenko", 200


@app.route('/' + os.environ['TOKEN'], methods=['POST'])
def process_updates():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "", 200


@app.route('/news')
def get_news():
    sources = ['https://ru.crypto-news.io/news/', 'https://investfuture.ru/crypto/news/']
    links = list()
    for source in sources:
        trash_reply = list(filter(lambda x: x.startswith('/news'),
                                  requests.get(source).text.split('href="')))

        for item in trash_reply:
            link = item.split('"')[0]
            if link and (link.endswith('.html') or link.startswith('/news/id')):
                links.append(source.replace('crypto/', '') + link[6:])
    random.shuffle(links)
    return ','.join(links[:10]), 200


@app.route('/track_bin')
def process_track_bin():
    api_link = 'https://api.binance.com/api/v3/ticker/price'
    response = requests.get(api_link, params=dict(request.args))
    if response.status_code != 200:
        return "", 400
    return json.loads(response.text)["price"], 200


@app.route('/track_bitf')
def process_track_bitf():
    api_link = 'https://api.bitfinex.com/v2/ticker'
    response = requests.get('{}/t{}'.format(api_link, request.args['symbol']))
    if response.status_code != 200:
        return "An error occured!", 400
    return response.text[1:-1].split(',')[0], 200


@app.route('/deals_bin')
def process_deals_bin():
    api_link = 'https://api.binance.com/api/v1/trades'
    response = requests.get(api_link, params=dict(request.args))
    if response.status_code != 200:
        return "An error occured!", 400
    return response.text, 200


@app.route('/deals_bitf')
def process_deals_bitf():
    api_link = 'https://api.bitfinex.com/v1/trades/'
    
    symbol = request.args['symbol']
    param = dict(request.args)
    param.pop('symbol')

    response = requests.get('{}/{}'.format(api_link, symbol), params=param)
    if response.status_code != 200:
        return "An error occured!", 400
    return response.text, 200


@app.route('/candlestick_bin')
def process_candlestick_bin():
    api_link = 'https://api.binance.com/api/v1/klines'

    api_time_link = 'https://api.binance.com/api/v1/time'
    cur_time = json.loads(requests.get(api_time_link).text)['serverTime']

    args = dict(request.args)
    args['endTime'] = cur_time
    response = requests.get(api_link, params=args)
    if response.status_code != 200:
        return "An error occured!", 400
    return response.text, 200


@app.route('/candlestick_bitf')
def process_candlestick_bitf():
    return "Unfortunately, bitfinex plots and analytics are unavailable now", 400


if __name__ == '__main__':
    app.run(True, True)
