# stonks moex
Application for analyzing information on liquid Russian shares, interacting with the [MOEX API](https://www.moex.com/a2193)



## Available in DockerHub
    docker pull fridi7/stonks_moex
    docker build .
    docker run -it -p 8000:8000 stonks_moex

## Usage
1\. Uploading data on stocks:

in the browser go to the URL:
        http://localhost:8000/load_stock/
        
or python console:

    import requests
    requests.get('http://localhost:8000/load_stock/')
    
or command line:
    
    http http://localhost:8000/load_stock/
    
Answer:

    "Stock data loaded"
   
2\. Get stock data by ticker:   
 
in the browser go to the URL 

    http://localhost:8000/get_data/<ticker>/   
(or curl, requests, etc, similar to the first point)    
for example, http://localhost:8000/get_stock/ABRD/  

Answer:

    {
        "trade_data": "2020-08-11",
        "secid": "ABRD",
        "name": "Абрау-Дюрсо ПАО ао",
        "isin": "RU000A0JS5T7",
        "reg_number": "1-02-12500-A",
        "main_board_id": "TQBR",
        "list_level": null,
        "quoted": true
    }
    
3\. The mechanism for obtaining and saving quotes (OHLC) for specified instruments for an arbitrary period of time:

in the browser go to the URL 

    http://localhost:8000/stocks/from<start_date>to<end_date>by<ticker>/ 
(or curl, requests, etc, similar to the first point)    
for example, http://localhost:8000/stocks/from2020-08-03to2020-08-05bySBER 

Answer:

    {
        "trade_data": "2020-08-03",
        "close": 229.99,
        "board_id": "SMAL"
    },
    {
        "trade_data": "2020-08-03",
        "close": 226.72,
        "board_id": "TQBR"
    },
    {
        "trade_data": "2020-08-04",
        "close": 226.14,
        "board_id": "SMAL"
    },
    {
        "trade_data": "2020-08-04",
        "close": 227.16,
        "board_id": "TQBR"
    },
    {
        "trade_data": "2020-08-05",
        "close": 225.6,
        "board_id": "SMAL"
    },
    {
        "trade_data": "2020-08-05",
        "close": 226.4,
        "board_id": "TQBR"
    }

4\. Getting a list of all saved instruments and the percentage (%) of price change for each instrument for a given period of time

in the browser go to the URL 

    http://localhost:8000/get_summary/from<start_date>to<end_date>/ 
(or curl, requests, etc, similar to the first point)    
for example, http://localhost:8000/get_summary/from2020-06-03to2020-08-07 

Example answer:

    {
        "name": "Аэрофлот-росс.авиалин(ПАО)ао",
        "secid": "AFLT",
        "board_id": "TQBR",
        "pct_change": -0.04402810304449656
    },
    {
        "name": "\"Газпром\" (ПАО) ао",
        "secid": "GAZP",
        "board_id": "TQBR",
        "pct_change": -0.09995194617972125
    },
    {
        "name": "Сбербанк России ПАО ао",
        "secid": "SBER",
        "board_id": "TQBR",
        "pct_change": 0.033409090909090944
    }

