import requests
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Stock, QuotedSecurities
from . import actions
from .serializers import QuotedSecuritiesSerializer, StocksSerializer, SummarySerializer


@api_view(('GET',))
def load_stock(request):
    # FIXME: if you access url several times, then the data in DB is duplicated
    """
    Описание запроса к MOEX - https://iss.moex.com/iss/reference/171
    """
    data = requests.get(url=f'{settings.MOEX_URL_STOCK}quotedsecurities.json?iss.meta=off&iss'
                            '.only=quotedsecurities')
    ready_data = actions.decoder_from_js(data, element='quotedsecurities')
    process = 0
    for stock in ready_data:
        QuotedSecurities(trade_data=stock[0], secid=stock[1], name=stock[2],
                         isin=stock[3], reg_number=stock[4], main_board_id=stock[5],
                         list_level=stock[6], quoted=bool(stock[7]))
        process = process + 1
        print(process)
    return Response({"Stock data loaded"})


@api_view(('GET',))
def get_stock(request, secid):
    """
        :param secid:
        Тикер ценной бумаги
        """
    try:
        stock = QuotedSecurities.objects.get(secid=secid)
        serializer = QuotedSecuritiesSerializer(stock)
    except QuotedSecurities.DoesNotExist:
        return Response({"Quoted securities not found"})
    return Response(serializer.data)


@api_view(('GET',))
def ohlc(request, start_date, end_date, secid):
    """
    Описание запроса к MOEX - https://iss.moex.com/iss/reference/65
     :param start_date:
        Дата начала вида ГГГГ-ММ-ДД
    :param end_date:
        Дата конца вида ГГГГ-ММ-ДД
    :param secid:
        Тикер ценной бумаги
     """
    try:
        Stock.objects.get(trade_data=start_date, secid=QuotedSecurities.objects.get(secid=secid), board_id='TQBR')
        Stock.objects.get(trade_data=end_date, secid=QuotedSecurities.objects.get(secid=secid), board_id='TQBR')
        # checking that database already contains the requested data and does not need to contact the api
        stocks = Stock.objects.filter(trade_data__gte=start_date, trade_data__lte=end_date,
                                      secid=QuotedSecurities.objects.get(secid=secid))
        serializer = StocksSerializer(instance=stocks, many=True)
        return Response(serializer.data)
    except (Stock.DoesNotExist, QuotedSecurities.DoesNotExist):
        data = requests.get(url=f'{settings.MOEX_URL_OHLC}{secid}'
                                f'.json?iss.meta=off&iss.only=history&from={start_date}&till={end_date}'
                                f'&history.columns=BOARDID,SECID,TRADEDATE,NAME,CLOSE')

        ready_data = actions.decoder_from_js(data, element='history')
        to_user = []
        for quotation in ready_data:
            sec_id = QuotedSecurities.objects.get(secid=quotation[1])
            stock = Stock.objects.get_or_create(secid=sec_id,
                                                trade_data=quotation[2],
                                                close=quotation[3],
                                                board_id=quotation[0])
            to_user.append(stock)
        stocks = Stock.objects.filter(trade_data__gte=start_date, trade_data__lte=end_date,
                                      secid=QuotedSecurities.objects.get(secid=secid))
        serializer = StocksSerializer(instance=stocks, many=True)
        return Response(serializer.data)


@api_view(('GET',))
def get_summary(request, start_date, end_date, board='TQBR'):
    """
    :param start_date:
        Дата начала вида ГГГГ-ММ-ДД
    :param end_date:
        Дата конца вида ГГГГ-ММ-ДД
    :param secid:
        Тикер ценной бумаги
    :param board:
        Режим торгов - по умолчанию основной режим торгов TQBR
     """

    stock_id = Stock.objects.filter(trade_data=start_date and end_date, board_id=board)  # at the moment only data on
    # the TQBR board is returned
    data = QuotedSecurities.objects.filter(stocks__in=stock_id)
    if not data:
        return Response({"Stock Does Not Exist"})
    result = []
    for stock in data:
        s_date = stock.stocks.filter(trade_data=start_date).first()  # расчет будет по одному из board
        e_date = stock.stocks.filter(trade_data=end_date).first()

        if not hasattr(s_date, 'close') or not hasattr(e_date, 'close'):
            return Response({"Stock Value Does Not Exist"})
        change = [s_date.close, e_date.close]
        pct_change = actions.calc_percentage_change(change)
        result.append({'name': stock.name, 'secid': stock.secid, 'pct_change': pct_change[1], 'board_id': board})

    if not result:
        return Response({"Stock Does Not Exist"})

    serializer = SummarySerializer(result, many=True)
    return Response(serializer.data)
