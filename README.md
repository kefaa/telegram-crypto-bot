# Telegram Crypto Bot

Telegram Crypto Bot is one of homework projects of Python Language course. Fall, 2018.

This bot is not supported now.

Homework description is below.

### Криптобот

Бот работает с 2 биткоин-биржами. Одной из бирж должна быть [binance](https://www.binance.com/en). Поддерживаемый функционал:

* Возможность посмотреть текущий курс монеты (биткоин, эфир и другие). Хочется, чтобы можно было сравнивать
криптовалюты между собой, а также криптовалюты и обычные валюты (как минимум белорусский рубль, российский рубль,
доллар, евро). Формат ввода для пользователя можно сделать вот таким "1.5 btc to usd bin" - показать курс 1.5 биткоинов
к доллару на бирже binance.

* Графики и аналитика по движению курсов. Нужно уметь показывать график цены монеты (в валюте или другой монете)
за какой-то временной промежуток. В качестве аналитики можно уметь отвечать на вопросы, на какую стоимость
изменилась определенная монета за выбранный период, сколько сделок было совершено по определеннной монете за
определенный день, окупаемость определенного набора монет на выбранном периоде (например, насколько изменилась цена за
5 btc и 10 eth за неделю).

* Новости - предоставление последних новостей о криптовалюте. Список
новостей регулярно обновляется с некоторой периодичностью.

* Сделки - возможность просматривать информацию о последних сделках на выбранной бирже. Формат ввода - "сделки btc usd bin 50" - показать 50 последних сделок по обмену биткоина на доллары на бирже binance.

* Возможность посмотреть текущий курс монеты - пользователь указывает, что хочет отслеживать, когда цена на определенную монету
достигнет некоторой величины и бот проверяет, например раз в 5 минут, ее стоимость, и сигнализирует, когда это
произойдет.

### Требования

* Нужно предоставить возможность общаться как с ботом, так и напрямую ходить в http api. По-хорошему, бот должен быть
лишь прослойкой к api. У бота и в api должен метод хелп, который вернет описание его
возможностей.

* Выбор фреймворков остается на усмотрение (можно использовать, например, `flask` и `pyTelegramBotAPI`).

* Нужно обеспечить постоянную работу бота и api, можно воспользоваться AWS, Google Cloud или Digital Ocean.
