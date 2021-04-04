# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 13:38:13 2020

@author: zhanghai
"""
'''
Input parameters： ticker，interval, test start date, test end date, model name
Output ： dataframe： initial deposit， gross profit，gross loss， total net profit，profit factor，
                    expected payoff， absolute drawdown， maximal drawdown， relative drawdown，
                    profit trades%， loss trades
Entry strategy： -1： close long position and wait；
                0： keep current position；
                1： create 
Exit strategy： reverse signal appears；
               reach stop loss entry-ATR
position size control： ATR based，ATR period = 20; ATR multiplier = 1; 2% risk tolerance， nomal value is average of ATR

'''
import pandas as pd 
pd.set_option('mode.chained_assignment', None)
import numpy as np
import datetime
import matplotlib.pyplot as plt
import stockstats
import sys
sys.path.append('../')
from uis.calculate_ama import calculate_ama
from data_processing.load_data import load_rawdata



class AMABackTest():
    def __init__(self, etf, start_date, end_date, model_name='AMA',initial_deposit=100000, price_type='open',er_window = 9, slow_window = 20, fast_window = 4):
        self.ticker = etf
        self.start_date = start_date
        self.end_date = end_date
        self.model_name = model_name
        self.init_deposit = initial_deposit
        self.price_type = price_type
        self.er_window = er_window
        self.slow_window = slow_window
        self.fast_window = fast_window
        self.raw_data = load_rawdata(etf, 'weekly')
        print("Self.raw",self.raw_data)
        self.indicators = stockstats.StockDataFrame.retype(self.raw_data.copy())
        ama, _, _ = calculate_ama(self.raw_data, self.indicators, self.price_type, self.er_window, self.slow_window, self.fast_window)
        self.raw_data['ama'] = ama
        self.report = pd.DataFrame(columns=['position size','total','profit'])


    def predict(self,cur_date):
        if self.raw_data.loc[cur_date]['open'] > self.raw_data.loc[cur_date]['ama'] and self.raw_data.loc[cur_date]['close'] > \
                self.raw_data.loc[cur_date]['ama']:
            signal = 1
        elif self.raw_data.loc[cur_date]['open'] < self.raw_data.loc[cur_date]['ama'] and self.raw_data.loc[cur_date]['close'] < \
                self.raw_data.loc[cur_date]['ama']:
            signal = -1
        else:
            signal = 0

        return signal
            
    def up_action(self,cur_date):
        if self.position == 'empty':
            self.entry_price = self.raw_data['close'][cur_date]
            self.entyr_atr =  self.indicators['atr'].loc[cur_date]
            self.position_size = int(self.total_value*0.05/self.entyr_atr)
            if self.position_size*self.entry_price > self.total_value:
                self.position_size = int(self.total_value/self.entry_price)
            df = pd.DataFrame({'position size':self.position_size,'total':self.total_value,'profit':0},index=[cur_date])
            self.report = self.report.append(df)
            self.position = 'long'
        else:
            stop_price = self.entry_price - 0.1*self.entyr_atr
            target_price = self.entry_price * 1.3
            if self.raw_data['low'][cur_date]  < stop_price < self.raw_data['high'][cur_date]:
                #sell at stop price
                profit = round((self.raw_data['high'][cur_date] - self.entry_price)*self.position_size, 2)
                self.total_value += profit
                df = pd.DataFrame({'position size':0,'total':self.total_value,'profit':profit},index=[cur_date])
                self.report = self.report.append(df)
                self.position = 'empty'
            elif self.raw_data['low'][cur_date] < target_price < self.raw_data['high'][cur_date]:
                #sell at target price
                profit = round((self.raw_data['low'][cur_date]-self.entry_price)*self.position_size, 2)
                self.total_value += profit
                df = pd.DataFrame({'position size':0,'total':self.total_value,'profit':profit},index=[cur_date])
                self.report = self.report.append(df)
                self.position = 'empty'
            else:
                #hold the position
                profit = round((self.raw_data['close'][cur_date]-self.entry_price)*self.position_size, 2)
                current_value = self.total_value + profit
                df = pd.DataFrame({'position size':self.position_size,'total':current_value,'profit':0},index=[cur_date])
                self.report = self.report.append(df)
                
    
    def down_action(self,cur_date):
        if self.position == 'long':
            #sell long position
            sell_price = self.raw_data['close'][cur_date]
            profit = round((sell_price-self.entry_price)*self.position_size, 2)
            self.total_value += profit
            df = pd.DataFrame({'position size':0,'total':self.total_value,'profit':profit},index=[cur_date])
            self.report = self.report.append(df)
            self.position = 'empty'
        else:
            #wait
            df = pd.DataFrame({'position size':0,'total':self.total_value,'profit':0},index=[cur_date])
            self.report = self.report.append(df)
    
    
    def sideway_action(self,cur_date):
        if self.position == 'long':
            #maintain long position
            stop_price = self.entry_price - 0.1 * self.entyr_atr
            target_price = self.entry_price * 1.3
            if self.raw_data['low'][cur_date]  < stop_price < self.raw_data['high'][cur_date]:
                #sell at stop price
                profit = round((self.raw_data['high'][cur_date] - self.entry_price)*self.position_size, 2)
                self.total_value += profit
                df = pd.DataFrame({'position size':0,'total':self.total_value,'profit':profit},index=[cur_date])
                self.report = self.report.append(df)
                self.position = 'empty'
            elif self.raw_data['low'][cur_date] < target_price < self.raw_data['high'][cur_date]:
                #sell at target price
                profit = round((self.raw_data['low'][cur_date]-self.entry_price)*self.position_size, 2)
                self.total_value += profit
                df = pd.DataFrame({'position size':0,'total':self.total_value,'profit':profit},index=[cur_date])
                self.report = self.report.append(df)
                self.position = 'empty'
            else:
                #hold the position
                profit = round((self.raw_data['close'][cur_date]-self.entry_price)*self.position_size, 2)
                current_value = self.total_value + profit
                df = pd.DataFrame({'position size':self.position_size,'total':current_value,'profit':0},index=[cur_date])
                self.report = self.report.append(df)
        else:
            #wait
            df = pd.DataFrame({'position size':0,'total':self.total_value,'profit':0},index=[cur_date])
            self.report = self.report.append(df)
        
    
    def run_test(self):
        cur_date = self.start_date
        date_list = list(self.raw_data.index)
        while cur_date not in self.raw_data.index:
            date = datetime.datetime.strptime(cur_date,'%Y-%m-%d')
            cur_date = (date +datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        first_date_index = date_list.index(cur_date)

        
        #set initial position size
        self.entry_atr = self.indicators['atr'].loc[cur_date]
        self.total_value = self.init_deposit
        self.position = 'empty'
        self.position_size = int(self.total_value*0.05/self.entry_atr)
        
        
        for cur_date_index in range(first_date_index, len(date_list)):
            #print(cur_date,'--',self.position_size)
            cur_date = date_list[cur_date_index]
            if cur_date > self.end_date:
                break
            trend = self.predict(cur_date)
            if trend == -1:
                self.down_action(cur_date)
            elif trend == 1:
                self.up_action(cur_date)
            else:
                self.sideway_action(cur_date)


        # plot the movement of total value and spy price
        """ to_plot = pd.concat([self.raw_data['close'][self.start_date:self.end_date]/100,
                   self.report['total']/self.init_deposit],axis=1,sort=False)
        to_plot.columns = [self.ticker+" price",self.model_name+" model net value"]
        ax = to_plot.plot(subplots=False,
                     figsize=(10,5),
                     grid=True,
                     title="{} {} model vs. {}".format(self.model_name, self.interval,self.ticker))
        fig = ax.get_figure()
        fig.savefig("./pic/AMA/{}_to_{}_{}_{}_model_vs_{}.png".format(self.start_date,
                                                            self.end_date,
                                                            self.model_name,
                                                            self.interval,
                                                            self.ticker))
        fig.plot()
        plt.close()"""
        # save position. total value information
        
        #calculate statistics
        '''
        initial deposit， total_trades,gross profit，gross loss， total net profit，
        profit factor，expected payoff， absolute drawdown， maximal drawdown， 
        relative drawdown，profit trades%， loss trades%
        '''
        profit = np.array(self.report['profit'])
        profit = profit[profit!=0]
        total_trades = len(profit)
        total_net_profit = round(self.report.iloc[-1]['total'] - self.init_deposit, 2)
        if len(profit) == 0:
            profit_trades = 100
        else:
            profit_trades = round(sum(profit>0)/len(profit)*100,2)
        loss_trades = round(100-profit_trades,2)
        
        
        peek = 1
        maxdrawdown = 0
        relative_drawdown = 0
        for i in self.report['total']:
            if i >= peek:
                relative_drawdown = maxdrawdown/peek
                peek = i
            elif i < peek:
                if peek-i > maxdrawdown:
                    maxdrawdown = peek - i
                    relative_drawdown = maxdrawdown/peek
        #elona removed -
        maxdrawdown = round(relative_drawdown*100,2)
        
        total_return = round(total_net_profit/self.init_deposit*100,2)
        test_interval = (datetime.datetime.strptime(self.end_date,'%Y-%m-%d')-\
                        datetime.datetime.strptime(self.start_date,'%Y-%m-%d')).days
                         
        cagr = pow(total_return/100+1,365/test_interval)-1
        cagr = round(cagr*100,2)

        # sharpe ratio
        return_rate = self.report['total'].pct_change(periods=1)
        return_std = return_rate.std() * np.sqrt(52)
        if return_std == 0: return_std = 0.1
        sharpe_ratio = round((cagr/100 - 0.02) / return_std, 2)


        
        self.statistics = {'ETF':self.ticker,
                           'Start date':self.start_date,
                           'End date':self.end_date,
                           'Initial deposit':self.init_deposit,
                           'Total trades':total_trades,
                           'Profit trades':profit_trades,
                           'Loss trades':loss_trades,
                           'Maximal drawdown':maxdrawdown, 
                           'Sharpe ratio':sharpe_ratio,
                           'Total net profit': total_net_profit,
                           'Total return':total_return,
                           'CAGR':cagr}
        
        return self.statistics