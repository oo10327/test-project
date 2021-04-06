
def getStockDataframe(symbols, in_days):
    
    df_stocktwits = pd.DataFrame(columns = ['symbol', 'text', 'sentiment', 'time'])
    start_date = dt.datetime.now() - dt.timedelta(days=in_days)
    start_date = start_date.date()  
    for symbol in symbols:
        ChangeSymbol = False
        maxCursor = ''        
        while ChangeSymbol == False:

            # 1. fetch stock data
            r1 = requests.get('https://api.stocktwits.com/api/2/streams/symbol/' + symbol + '.json?filter=top&limit=20&max=' + maxCursor)
            data = r1.json()
            if r1.status_code != 200:
                print('make more than 200 requests an hour')
                print(data)
                return df_stocktwits

            # 2. update maxCursor
            maxCursor = str(data['cursor']['max'])

            # 3. parse data and put into dataframe
            rows = []
            for msg in data['messages']:
                text = msg['body']
                time_str = msg['created_at'][:10]
                sentiments = msg['entities']['sentiment']
                symbol = data['symbol']['symbol']
                if sentiments != 'null':
                    sentiment = str(sentiments)[11:-2]
                else :
                    sentiment = ''
                date_time_obj = dt.datetime.strptime(time_str, '%Y-%m-%d')
                date_time_obj = date_time_obj.date()

                # check messages are enough 
                if date_time_obj <= start_date:
                    ChangeSymbol = True
                    break

                rows.append([symbol, text, sentiment, date_time_obj])

            df_stocktwits = df_stocktwits.append(pd.DataFrame(rows, columns = ['symbol', 'text', 'sentiment', 'time']), ignore_index=True)
            df_stocktwits = df_stocktwits.sort_values(by=['symbol'], ignore_index = True)
                            
    news_tables = {}
    parse_data_news = []
    for symbol in symbols:
        url = 'https://finviz.com/quote.ashx?t=' + symbol + '&ty=c&ta=1&p=d'
        r2 = requests.get(url, headers={'user-agent': 'my-app'})
        soup1 = BeautifulSoup(r2.text, 'html')
        all_news=soup1.find(id="news-table")
        news_tables[symbol] = all_news

        for symbol, news_table in  news_tables.items():
            for titles in news_table.findAll('tr'):
                datetime = titles.td.text
                title = titles.a.text
                channel = titles.span.text
                news_url = titles.a['href']
                if len(datetime.split(" ")) == 1:
                    time = datetime[0:7]
                else:
                    date = datetime[0:9]
                    time = datetime[11:17]

                date = pd.to_datetime(date)
                parse_data_news.append([symbol, date, time, title, channel, news_url])
                df_finviz = pd.DataFrame(parse_data_news, columns =['symbol','date', 'time', 'title', 'channel', 'news_url'])
        df_finviz = df_finviz.append(pd.DataFrame(df_finviz, columns =['symbol','date', 'time', 'title', 'channel', 'news_url']), ignore_index=True)
        df_finviz = df_finviz.sort_values(by=['symbol'], ignore_index = True)

        
    rating_tables = {}
    parse_data_rating = []       
    for symbol in symbols:
        url = 'https://finviz.com/quote.ashx?t=' + symbol + '&ty=c&ta=1&p=d'
        r2 = requests.get(url, headers={'user-agent': 'my-app'})
        soup2 = BeautifulSoup(r2.text, 'html')
        all_rating=soup2.findAll(class_="fullview-ratings-inner")
        rating_tables[symbol] = all_rating

        for symbol, ratings in rating_tables.items():
            for rating in ratings:
                date= rating.text.split('\n')[1][:9]
                date = dt.datetime.strptime(date, '%b-%d-%y')
                date = date.date()
                action= rating.text.split('\n')[1][9:]
                organization= rating.text.split('\n')[2]
                suggestion= rating.text.split('\n')[3]
                target_price= rating.text.split('\n')[4]
                
                parse_data_rating.append([symbol, date, action, organization, suggestion, target_price])
        df_rating = pd.DataFrame(parse_data_rating, columns = ['symbol', 'date', 'action', 'organization', 'suggestion', 'target_price'])
        df_rating = df_rating.sort_values(by=['symbol'], ignore_index = True)
    
    
    df_hist_data= pd.DataFrame([],columns = ['symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock', 'Splits'])
    for symbol in symbols:
        all_info = yf.Ticker(symbol)
        hist_data = all_info.history(period = 'max')
        hist_data['symbol']= symbol
        hist_data.reset_index(inplace=True)
        hist_data = hist_data.rename(columns = {'index': 'Date'})
        df_hist_data = df_hist_data.append(hist_data)
        
    return df_finviz, df_stocktwits, df_rating, df_hist_data


df_finviz, df_stocktwits, df_rating, df_hist_data= getStockDataframe(['ZM', 'SQ'], 3)

