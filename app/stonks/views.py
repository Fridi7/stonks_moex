from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import QuotedSecuritiesSerializer, StocksSerializer, SummarySerializer
from .services import *


@api_view(('GET',))
def load_stocks(request):
    result_message = get_stocks()
    return Response({result_message})


@api_view(('GET',))
def stock(request, secid):
    result_stock = get_stock(secid)
    if result_stock:
        serializer = QuotedSecuritiesSerializer(result_stock)
        return Response(serializer.data)
    else:
        return Response({"Quoted securities not found"})


@api_view(('GET',))
def ohlc(request, start_date, end_date, secid):
    stocks = get_ohlc(start_date, end_date, secid)
    serializer = StocksSerializer(instance=stocks, many=True)
    return Response(serializer.data)


@api_view(('GET',))
def summary(request, start_date, end_date):
    result = get_summary(start_date, end_date)
    if isinstance(result, list):
        serializer = SummarySerializer(result, many=True)
        return Response(serializer.data)
    elif isinstance(result, str):
        return Response({result})
