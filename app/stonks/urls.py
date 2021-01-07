from django.urls import path

from .views import ohlc, load_stocks, stock, summary


app_name = "stonks"


urlpatterns = [
    path('stocks/from<str:start_date>to<str:end_date>by<str:secid>', ohlc),
    path('load_stock/', load_stocks),
    path('get_stock/<str:secid>/', stock),
    path('get_summary/from<str:start_date>to<str:end_date>', summary)
]
