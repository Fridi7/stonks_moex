import requests

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse

from .models import Stock, QuotedSecurities
from . import actions
from .serializers import QuotedSecuritiesSerializer, StocksSerializer, SummarySerializer


def load_stock(request):
    """Описание запроса к MOEX - https://iss.moex.com/iss/reference/171 """
    data = requests.get(url='https://iss.moex.com/iss/statistics/engines/stock/quotedsecurities.json?iss.meta=off&iss'
                            '.only=quotedsecurities')
    ready_data = actions.decoder_from_js(data, element='quotedsecurities')
    process = 0
    for i in ready_data:
        stock2 = QuotedSecurities(trade_data=i[0], secid=i[1], name=i[2], isin=i[3],
                                  reg_number=i[4], main_board_id=i[5], list_level=i[6], quoted=bool(i[7]))
        process = process + 1
        stock2.save()
    return JsonResponse("Stock data loaded", safe=False)


@api_view(('GET',))
def get_stock(request, secid):
    """    :param secid:
        Тикер ценной бумаги"""
    try:
        stock = QuotedSecurities.objects.get(secid=secid)
        serializer = QuotedSecuritiesSerializer(stock)
    except QuotedSecurities.DoesNotExist:
        return JsonResponse("Quoted securities not found", safe=False)
    return Response(serializer.data)


@api_view(('GET',))
def ohlc(request, start_date, end_date, secid):
    """Описание запроса к MOEX - https://iss.moex.com/iss/reference/65
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
        data = requests.get(url=f'https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/{secid}'
                                f'.json?iss.meta=off&iss.only=history&from={start_date}&till={end_date}'
                                f'&history.columns=BOARDID,SECID,TRADEDATE,NAME,CLOSE')

        ready_data = actions.decoder_from_js(data, element='history')
        to_user = []
        for i in ready_data:
            sec_id = QuotedSecurities.objects.get(secid=i[1])
            stock = Stock.objects.get_or_create(secid=sec_id, trade_data=i[2], close=i[3], board_id=i[0])
            to_user.append(stock)
        stocks = Stock.objects.filter(trade_data__gte=start_date, trade_data__lte=end_date,
                                      secid=QuotedSecurities.objects.get(secid=secid))
        serializer = StocksSerializer(instance=stocks, many=True)
        return Response(serializer.data)


@api_view(('GET',))
def get_summary(request, start_date, end_date, board='TQBR'):
    """ :param start_date:
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
        return JsonResponse("Stock Does Not Exist", safe=False)
    result = []
    for i in data:
        s_date = i.stocks.filter(trade_data=start_date).first()  # расчет будет по одному из board
        e_date = i.stocks.filter(trade_data=end_date).first()

        if not hasattr(s_date, 'close') or not hasattr(e_date, 'close'):
            return JsonResponse("Stock Value Does Not Exist", safe=False)
        change = [s_date.close, e_date.close]
        pct_change = actions.calc_percentage_change(change)
        result.append({'name': i.name, 'secid': i.secid, 'pct_change': pct_change[1], 'board_id': board})

    if not result:
        return JsonResponse("Stock Does Not Exist", safe=False)

    serializer = SummarySerializer(result, many=True)
    return Response(serializer.data)
