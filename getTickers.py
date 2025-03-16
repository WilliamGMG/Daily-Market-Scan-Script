import polygon

#create client
api_key = ""
client = polygon.RESTClient(api_key)

#output file
tickFile = open("tickersNoOTC.txt", "w")

#populate with tickers < 4
try: 
    for t in client.list_tickers(limit=1000):
        if len(t.ticker) < 5 and t.market != "otc":
            tickFile.write(str(t.ticker) + "\n")
except Exception as e:
    print(f"An error occurred: {e}")


tickFile.close()
