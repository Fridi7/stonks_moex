from django.urls import path

from .views import ohlc, load_stock, get_stock, get_summary


app_name = "stonks"


urlpatterns = [
    path('stocks/from<str:start_date>to<str:end_date>by<str:secid>', ohlc),
    path('load_stock/', load_stock),
    path('get_stock/<str:secid>/', get_stock),
    path('get_summary/from<str:start_date>to<str:end_date>', get_summary)
]
