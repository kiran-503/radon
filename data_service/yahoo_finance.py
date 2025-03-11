import yfinance as yf
import datetime

def get_stock_price(stock, start="2020-01-01", end=None, interval='1d', period='1mo'):
    if end is None:
        end = datetime.datetime.now().strftime("%Y-%m-%d")

    ticker = yf.Ticker(f"{stock}.NS")
    if not start:
        data = ticker.history(period=period, interval=interval)
    else:
        data = ticker.history(start=start, end=end, interval=interval)

    if data.empty:
        print(f"No data available for {stock}")
        return None

    data = data.reset_index()

    date_column = "Date" if "Date" in data.columns else "Datetime"
    data[date_column] = data[date_column].dt.strftime('%Y-%m-%d')
    data.drop(columns=[col for col in ['Dividends', 'Stock Splits'] if col in data.columns], inplace=True)
    data.columns = [col.lower() for col in data.columns]
    data = data.round(2)

    return data

# data = get_stock_price('RELIANCE',None,None,'1d','1mo')
# if data is not None:
#     print(data)
