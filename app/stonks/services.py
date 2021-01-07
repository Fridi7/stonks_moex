import datetime

import requests
from django.conf import settings

from .models import Stock, QuotedSecurities
from .utils import *


def get_stocks():
    """
    Описание запроса к MOEX - https://iss.moex.com/iss/reference/171
    """
    if not QuotedSecurities.objects.filter(trade_data=datetime.datetime.now().strftime("%Y-%m-%d")).exists():
        data = requests.get(url=f'{settings.MOEX_URL_STOCK}quotedsecurities.json?iss.meta=off&iss'
                                '.only=quotedsecurities')
        data_dict = decoder_from_js(data, element='quotedsecurities')
        for stock in data_dict:
            QuotedSecurities.objects.create(trade_data=stock[0], secid=stock[1], name=stock[2],
                                            isin=stock[3], reg_number=stock[4], main_board_id=stock[5],
                                            list_level=stock[6], quoted=bool(stock[7]))
        return "Stock data loaded"
    else:
        return "Stock data for today already loaded"


def get_stock(secid):
    """
    :param secid:
        Тикер ценной бумаги
    """
    stock = QuotedSecurities.objects.filter(secid=secid).last()
    return stock


def get_ohlc(start_date, end_date, secid):
    """
    Описание запроса к MOEX - https://iss.moex.com/iss/reference/65
     :param start_date:
        Дата начала вида ГГГГ-ММ-ДД
    :param end_date:
        Дата конца вида ГГГГ-ММ-ДД
    :param secid:
        Тикер ценной бумаги
    """
    secid_object = QuotedSecurities.objects.filter(secid=secid).last()
    if secid_object:
        start_date_checker = Stock.objects.filter(trade_data=start_date, secid=secid_object, board_id='TQBR')
        end_date_checker = Stock.objects.filter(trade_data=end_date, secid=secid_object, board_id='TQBR')
        if start_date_checker and end_date_checker:
            # checking that database already contains the requested data and does not need to contact the api
            stocks = Stock.objects.filter(trade_data__gte=start_date, trade_data__lte=end_date,
                                          secid=secid_object)
            return stocks
        else:
            data = requests.get(url=f'{settings.MOEX_URL_OHLC}{secid}'
                                    f'.json?iss.meta=off&iss.only=history&from={start_date}&till={end_date}'
                                    f'&history.columns=BOARDID,SECID,TRADEDATE,NAME,CLOSE')

            data_dict = decoder_from_js(data, element='history')
            stocks = []
            for quotation in data_dict:
                sec_id = QuotedSecurities.objects.filter(secid=quotation[1]).last()
                stock = Stock.objects.get_or_create(secid=sec_id,
                                                    trade_data=quotation[2],
                                                    close=quotation[3],
                                                    board_id=quotation[0])
                stocks.append(stock[0])
            return stocks


def get_summary(start_date, end_date, board='TQBR'):
    """
    :param start_date:
        Дата начала вида ГГГГ-ММ-ДД
    :param end_date:
        Дата конца вида ГГГГ-ММ-ДД
    :param board:
        Режим торгов - по умолчанию основной режим торгов TQBR
    """
    stock_id = Stock.objects.filter(trade_data=start_date and end_date, board_id=board)  # at the moment only data on
    # the TQBR board is returned
    data = QuotedSecurities.objects.filter(stocks__in=stock_id)
    if not data:
        return "Stock Does Not Exist - use the ohlc method"
    result = []
    for stock in data:
        s_date = stock.stocks.filter(trade_data=start_date).first()  # calculation will be one of the board
        e_date = stock.stocks.filter(trade_data=end_date).first()

        if not hasattr(s_date, 'close') or not hasattr(e_date, 'close'):
            return "Stock Value Does Not Exist"
        change = [s_date.close, e_date.close]
        pct_change = calc_percentage_change(change)
        result.append({'name': stock.name, 'secid': stock.secid, 'pct_change': pct_change, 'board_id': board})

    if not result:
        return "Stock Does Not Exist"

    return result
