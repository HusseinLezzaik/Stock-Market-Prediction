# iQuant user manual

### 0. How to start the software

Please download the apia.rar file and unzip it. In the directory you can find a file named apia.exe. Double click this file to run our software.



#### 1. Login

After the software starts, please click the "**login**" button. Then enter the following username and password to log in to the software.

- username : --------
- password : --------



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page0.jpg" style="zoom:50%;" />



#### 2. Home

The Home page mainly displays the price information of the ETF, including the latest price (updated every 30 seconds if it is during the opening period), the closing price of the previous period, the absolute rise and fall range and the relative rise and fall range, and the opening, highest and lowest price of the current period, and commonly used moving average information.



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page1.jpg" style="zoom:50%;" />


#### 3. Manage ETF

This page enables you to manage (add or delete) the ETF currently invested in.
When adding a new ETF, we support adding multiple ETFs at the same time. It should be noted that the names of each ETF must be separated by a comma or semicolon.



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page2.jpg" style="zoom:50%;" />



#### 4. Update historical data

Although our software has completely updated the historical data when it is started. However, sometimes we keep the software active for a long time, so when calculating trading signals, we ask users to manually update the data. Here, you only need to select the ETF that needs to be updated and the corresponding time frame and click “**Start**” button, then you can easily complete the data update.



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page3.jpg" style="zoom:50%;" />



#### 5. Show candles

This page will display the ETF candlestick chart. We provide three drop-down boxes for you to choose the corresponding parameters, namely ETF, time frame and moving average. After you have selected the corresponding combination, click the "**Show**" button to see the corresponding candlestick chart. In addition, this page will also display some price information, such as the current price, opening price, highest and lowest prices. In the candlestick chart, the mouse can follow each candle and display the date and corresponding price information.



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page4.jpg" style="zoom:50%;" />



#### 6. Trading signals

Here, if you don't want to change any model parameters, please click the "**Show Signals**" button to display trading signals. We have five basic trading signals, namely EMA12 (weekly), EMA20 (monthly), AMA, AMA Direction and SVM. The final trading signal is obtained through the weighted average of these five signals. 

If the conclusion is greater than 0.4, it is considered to be an upward trend, and the larger the value, the greater the possibility of rising. If the conclusion is less than minus 0.4, it is considered to be a downtrend, and the smaller the value (the closer it is to minus one), the greater the possibility of a fall. The middle part [-0.4, 0.4] is considered sideways.

If you want to change the model parameters, please input or select different model parameters. It should be noted  that after selecting specific parameters, you need to click "**Build Data**" and "**Update Models**" in turn to update the data required by the model and the model itself. Finally, click on the "**Show Signals**" button to get new trading signals.

For SVM, **Back window** represents how many cycles of data used to predict the current cycle.

For AMA, the **price type** represents which price we use to calculate the AMA. **ER Window** indicates how many periods are used to calculate the efficiency ratio. Fast window and Slow window indicate the number of calculation periods for fast EMA and slow EMA.



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page5.jpg" style="zoom:50%;" />



#### 7. Back Test

In the backtest, we must first specify the backtest model and model parameters. This part is consistent with Trading Signals. Click "**Do Backtest**" to get the backtest report in a specific backtest time period.

In the backtest report, we provide backtest start date, end date, number of transactions, percentage of profitable transactions, maximum drawdown, Sharpe rate, total return and annualized return for your reference.

In Historical Backtests you can select the reports of the backtests that have been done. At the same time, you can choose to delete the currently displayed backtest report. It is worth noting that when you select a historical backtest report, the relevant model parameters of this backtest will be synchronously displayed in the parameter selection area above.



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page6.jpg" style="zoom:50%;" />



#### 8. Core Strategy Table

We have integrated the most frequently used core strategy tables into the software. There are three tables in total. 

The first form needs to be filled out manually. Only the type of position needs to be entered in the table2, and the remaining data will be automatically calculated based on the data in the first table (in order to prevent human error, the automatically calculated data cannot be edited). The table3 will score the current status. Most of the data needs to be entered manually (except for the Profit Zone, which is calculated based on the Ratio in the table2). Of course, the last two rows in the table3 are also automatically calculated. Remember to save each time you change the form.



<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page7.jpg" style="zoom:50%;" />



#### 9 Position Calculator

This tool allows you to control the position based on the current price and ATR. You only need to enter the initial capital, risk tolerance and stop price coefficient (how many times the ATR), you can get all the information in the table. Such as the current price, ATR, recommended position size, stop loss price and current value of the position.

If possible, multiplying the position size calculated here with the conclusion in Trading Signals to obtain the position size under the current trading signals is also a good choice.

<img src="https://github.com/Haifei-ZHANG/iQuant/blob/master/images/page8.jpg" style="zoom:50%;" />
