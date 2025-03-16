# 📊 Daily-Market-Scan-Script 📊

This is a simple Python script that creates an Excel sheet showing tickers with high percentage gain in the pre, normal and after-hours market as well as tickers with high volume.

⚠️ Note: you have to have a [polygon.io API](https://polygon.io/) key to use this script and you must install [polygon.io for python](https://github.com/polygon-io/client-python) / [python](https://www.python.org/downloads/).

## 📌 How To Use Daily Market Scan
1. Download `daily_market_scan.py` and place it in a new folder.
2. Create a `tickers.txt` file in the same folder as `daily_market_scan.py`.
3. Fill the tickers file with all of the tickers you want to scan or use the [tickers script](https://github.com/WilliamGMG/Daily-Market-Scan-Script/edit/main/README.md#-how-to-use-get-tickers) to generate tickers.
4. Inside of `daily_market_scan.py`, find
```python
  API_KEY = ""
```
  and enter your api key between ""

5. In order to select the date go to
```python
  curr_date = datetime(2024, 6, 3)
```
underneath `API_KEY = ""` and change the date to what you want.

6. Finally you can change
```python
  WORKERS = 60
```
to change how many tickers the script will proccess at once. A higher end computer will run the script better with more workers where as a lower end computer will work better with less.

8. Now you can run the script and the output will be in `scan_output.csv` in the same folder as the script.

## 📌 How To Use Get Tickers
1. Download `getTickers.py` and place it in a new folder.
2. Inside of `getTickers.py`, find
```python
  api_key = ""
```
  and enter your api key between ""

3. Run the script.
4. You should now have a `tickersNoOTC.txt` file in the same folder as the script.
