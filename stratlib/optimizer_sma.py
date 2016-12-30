# -*- coding: utf-8 -*-
"""
Created on Tue Nov 03 13:06:56 2015

@author: Eunice
"""

import itertools
from pyalgotrade.optimizer import local
import thrSMA
from pyalgotrade import bar



def parameters_generator():
    instrument = ["600288SH"]
    long_1 = range(20, 24)
    short_l = range(2, 5)
    up_cum = range(19, 20)
    return itertools.product(instrument, short_l, long_1,up_cum)
instrument = '600288'
market = 'SH'
fromDate = '20150101'
toDate ='20150601'
frequency = bar.Frequency.MINUTE

#############################################path set ############################33
import os
if frequency == bar.Frequency.MINUTE:
    path = os.path.join('..', 'histdata', 'minute')
elif frequency == bar.Frequency.DAY:
    path = os.path.join('..', 'histdata', 'day')
filepath = os.path.join(path, instrument + market + ".csv")


#############################################don't change ############################33
from pyalgotrade.cn import csvfeed
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.tools import yahoofinance

barfeed = csvfeed.Feed(frequency)
barfeed.setDateTimeFormat('%Y-%m-%d %H:%M:%S')

# feed = csvfeed.Feed(frequency)
#feed = yahoofeed.Feed()
#feed.addBarsFromCSV("dia",'gdx-2009-yahoofinance.csv')
barfeed.loadBars(instrument, market, fromDate, toDate, filepath)


if __name__ == "__main__":

    local.run(thrSMA.thrSMA, barfeed, parameters_generator())
"""

    
    #############################################path set ############################33 
    import os
    if frequency == bar.Frequency.MINUTE:
        path = os.path.join('..', 'histdata', 'minute')
    elif frequency == bar.Frequency.DAY:
        path = os.path.join('..', 'histdata', 'day')
    filepath = os.path.join(path, instrument + market + ".csv")
    
    
    #############################################don't change ############################33  
    from pyalgotrade.cn.csvfeed import Feed
    
    barfeed = Feed(frequency)
    barfeed.setDateTimeFormat('%Y-%m-%d %H:%M:%S')
    barfeed.loadBars(instrument, market, fromDate, toDate, filepath)
    
    pyalgotrade_id = instrument + '.' + market
    strat = strat(barfeed, pyalgotrade_id, *paras)
    
    from pyalgotrade.stratanalyzer import returns
    from pyalgotrade.stratanalyzer import sharpe
    from pyalgotrade.stratanalyzer import drawdown
    from pyalgotrade.stratanalyzer import trades
    
    retAnalyzer = returns.Returns()
    strat.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    strat.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    strat.attachAnalyzer(tradesAnalyzer)
    
    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        
    strat.run()
    
    if plot:
        plt.plot()
        


    #夏普率
    sharp = sharpeRatioAnalyzer.getSharpeRatio(0.05)
    #最大回撤
    maxdd = drawDownAnalyzer.getMaxDrawDown()
    #收益率
    return_ = retAnalyzer.getCumulativeReturns()[-1]
    #收益曲线
    return_list = []
    for item in retAnalyzer.getCumulativeReturns():
        return_list.append(item)
        
# feed 实例
def run_strategy(smaPeriod):

    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("orcl", "orcl-2000.csv")

"""