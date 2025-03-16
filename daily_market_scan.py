from datetime import date
from datetime import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import polygon

#//////////////////////////////////////////////////
#      create files cilent and prarameters
#//////////////////////////////////////////////////

WORKERS = 60
API_KEY = ""
curr_date = datetime(2024, 6, 3)

#change from date to friday if its monday
if curr_date.weekday() == 0:
    from_date = (curr_date - timedelta(days=3)).strftime("%Y-%m-%d")
else:
    from_date = (curr_date - timedelta(days=1)).strftime("%Y-%m-%d")

#create client
client = polygon.RESTClient(API_KEY, retries=5)

#files
tickerFile = open("tickers.txt")

#create output files
scan_output = open("scan_output.csv", "w")

#output headers
scan_output.write("Pre-Mark.,Ticker,Growth,Shares,Volume,Norm M.,Ticker,Growth,Shares,Volume,After Hrs.,Ticker,Growth,Shares,Volume,High Vol.,Ticker,Volume\n")

#output lists
high_volume = []
pre_market_gains = []
normal_market_gains = []
after_hours_gains = []

#//////////////////////////////////////////////////
#             def functions / classes
#//////////////////////////////////////////////////

class tickergain:
    def __init__(self, ticker, gain, shares, volume):
        self.ticker = ticker
        self.gain = gain
        self.shares = shares
        self.volume = volume
    
    def __str__(self):
        return f"{self.ticker} - {self.gain}% - {self.shares} shares - {self.volume} volume"


def market_volume_scan(ticker):
    #check that ticker is between 0.05$ and 10.00$
    day_agg = client.get_daily_open_close_agg(ticker, curr_date.strftime("%Y-%m-%d"), True)
    if day_agg.low >= 0.05 and day_agg.high <= 10.00:
        
        group_one = False
        group_two = False
        group_three = False
        pre_market_high = 0
        normal_market_high = 0
        after_hours_high = 0
        pre_market_volume = 0
        normal_market_volume = 0
        after_hours_volume = 0

        #sort agg into pre-market normal market and after hours
        for a in client.list_aggs(ticker, 1, "minute", from_date, curr_date.strftime("%Y-%m-%d"), True):

            #get time from timestamp
            time = datetime.fromtimestamp(a.timestamp / 1000).time()
            
            #skip until time reaches 4pm day one
            if not group_one and time < datetime.strptime("16:00", "%H:%M").time():
                continue
            group_one = True
            
            #group-one: 4pm - 9:30am (pre-market))
            if group_one and not group_two:
                #get pre-market open
                if time == datetime.strptime("16:00", "%H:%M").time():
                    pre_market_open = a.open
                    if a.high > a.open:
                        pre_market_high = a.high
                    
                    pre_market_volume += a.volume
                #end pre-market group at 9:30am
                elif time == datetime.strptime("09:30", "%H:%M").time():
                    if a.high > a.open:
                        normal_market_high = a.high
                    group_two = True

                #check for new pre-market high
                elif pre_market_high < a.high:
                    pre_market_high = a.high
                    pre_market_volume += a.volume
                else:
                    pre_market_volume += a.volume
            #group-two 9:30am - 4pm (normal market)
            elif group_two and not group_three:
                #end normal market at 4:00pm
                if time == datetime.strptime("16:00", "%H:%M").time():
                    after_hours_open = a.open
                    if a.high > a.open:
                        after_hours_high = a.high
                    group_three = True
                
                #update normal market high
                elif normal_market_high < a.high:
                    normal_market_high = a.high
                    normal_market_volume += a.volume
                else:
                    normal_market_volume += a.volume

            #last-group: 4pm - 8pm (after-hours)
            elif after_hours_high < a.high:
                after_hours_high = a.high
                after_hours_volume += a.volume
            else: 
                after_hours_volume += a.volume
        
        #calculate gains for pre-market
        pct_gain_pre_market = round(((pre_market_high - pre_market_open)/pre_market_open) * 100, 2)

        #calculate gains for normal market
        pct_gain_normal_market = round(((normal_market_high - pre_market_open)/pre_market_open) * 100, 2)

        #calculate gains for after hours
        pct_gain_after_hours = round(((after_hours_high - after_hours_open)/after_hours_open) * 100, 2)

        #get amt of shares
        shares = client.get_ticker_details(ticker, curr_date.strftime("%Y-%m-%d")).share_class_shares_outstanding

        #insert pre-market gain
        spot_found = False
        if len(pre_market_gains) == 0:
            pre_market_gains.append(tickergain(ticker, pct_gain_pre_market, shares, pre_market_volume))
        else:
            #insert gain into apporpiate place
            for i in range(len(pre_market_gains)):
                if pre_market_gains[i].gain < pct_gain_pre_market:
                    pre_market_gains.insert(i, tickergain(ticker, pct_gain_pre_market, shares, pre_market_volume))
                    spot_found = True
                    break
            
            #add gain to end of list if lowest gain
            if not spot_found:
                pre_market_gains.append(tickergain(ticker, pct_gain_pre_market, shares, pre_market_volume))

        #insert normal market gain
        spot_found = False
        if len(normal_market_gains) == 0:
            normal_market_gains.append(tickergain(ticker, pct_gain_normal_market, shares, normal_market_volume))
        else:
            #insert gain into apporpiate place
            for i in range(len(normal_market_gains)):
                if normal_market_gains[i].gain < pct_gain_normal_market:
                    normal_market_gains.insert(i, tickergain(ticker, pct_gain_normal_market, shares, normal_market_volume))
                    spot_found = True
                    break
            
            #add gain to end of list if lowest gain
            if not spot_found:
                normal_market_gains.append(tickergain(ticker, pct_gain_normal_market, shares, normal_market_volume))

        #insert after hours gain
        spot_found = False
        if len(after_hours_gains) == 0:
            after_hours_gains.append(tickergain(ticker, pct_gain_after_hours, shares, after_hours_volume))
        else:
            #insert gain into apporpiate place
            for i in range(len(after_hours_gains)):
                if after_hours_gains[i].gain < pct_gain_after_hours:
                    after_hours_gains.insert(i, tickergain(ticker, pct_gain_after_hours, shares, after_hours_volume))
                    spot_found = True
                    break
            
            #add gain to end of list if lowest gain
            if not spot_found:
                after_hours_gains.append(tickergain(ticker, pct_gain_after_hours, shares, after_hours_volume))

        #check for high volume
        if day_agg.volume > 50000000:
            #if high volume empty append first match
            if len(high_volume) == 0:
                high_volume.append(day_agg)
                return
            else:
                #insert match in apporiate place to keep list sorted
                for i in range(len(high_volume)):
                    if high_volume[i].volume < a.volume:
                        high_volume.insert(i, day_agg)
                        return
                high_volume.append(day_agg)

#//////////////////////////////////////////////////
#                 ticker loop
#//////////////////////////////////////////////////

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    #delegate aggs for volume scan
    [executor.submit(market_volume_scan, t.rstrip()) for t in tickerFile]

#discard everything but top 30 results
pre_market_gains = pre_market_gains[:30]
normal_market_gains = normal_market_gains[:30]
after_hours_gains = after_hours_gains[:30]
high_volume = high_volume[:30]

#dump results in a .csv
for i in range(30):
    scan_output.write(f",{pre_market_gains[i].ticker},{pre_market_gains[i].gain},{pre_market_gains[i].shares},{pre_market_gains[i].volume},,")
    scan_output.write(f"{normal_market_gains[i].ticker},{normal_market_gains[i].gain},{normal_market_gains[i].shares},{normal_market_gains[i].volume},,")
    scan_output.write(f"{after_hours_gains[i].ticker},{after_hours_gains[i].gain},{after_hours_gains[i].shares},{after_hours_gains[i].volume},,")
    try:
        scan_output.write(f"{high_volume[i].symbol},{high_volume[i].volume}\n")
    except:
        scan_output.write(",,,\n")

#end script
scan_output.close()
tickerFile.close()
