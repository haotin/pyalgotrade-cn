# -*- coding: utf-8 -*-
"""
Created on Tue Nov 03 13:06:56 2015

@author: Eunice
"""

# if __name__ == '__main__':
#     import sys
#     sys.path.append("..")
#     from pyalgotrade import bar
#     from pyalgotrade import plotter
# 以上模块仅测试用
from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.technical import atr


class thrSMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, short_l, long_l, up_cum):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__malength1 = int(short_l)
        self.__malength2 = int(long_l)
        self.__circ = int(up_cum)
        self.__bardata = feed[instrument]
        self.N = atr.ATR(self.__bardata, 20)

        self.__ma1 = ma.SMA(self.__prices, self.__malength1)
        self.__ma2 = ma.SMA(self.__prices, self.__malength2)

    def getPrice(self):
        return self.__prices

    def getBarData(self):
        return self.__bardata

    def getSMA(self):
        return self.__ma1, self.__ma3

    def onEnterCanceled(self, position):
        self.__position = None

    def onEnterOK(self):
        pass

    def onExitOk(self, position):
        self.__position = None
        #self.info("long close")

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def buyCon1(self):
        if cross.cross_above(self.__ma1, self.__ma3) > 0:
            return True

    def sellCon1(self):
        if cross.cross_below(self.__ma1, self.__ma3) > 0:
            return True


    def onBars(self, bars):
        # print self.N[-1],self.__ma1[-1]
        # If a position was not opened, check if we should enter a long position.
        if self.__ma2[-1]is None:
            return

        if self.__position is not None:
            if not self.__position.exitActive() and cross.cross_below(self.__ma1, self.__ma2) > 0:
                self.__position.exitMarket()
            #self.info("sell %s" % (bars.getDateTime()))

        if self.__position is None:
            if cross.cross_above(self.__ma1, self.__ma2) > 0:
                shares = int(self.getBroker().getCash() * 0.2 / bars[self.__instrument].getPrice())
                self.__position = self.enterLong(self.__instrument, shares)
                # print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()



def testStrategy(paras):
    from pyalgotrade import bar
    from pyalgotrade import plotter

    strat = thrSMA
    instrument = '600288'
    market = 'SH'
    fromDate = '20150101'
    toDate ='20150601'
    frequency = bar.Frequency.DAY
    #paras = [3, 21,20]
    plot = False

    #############################################path set ############################
    import os
    if frequency == bar.Frequency.MINUTE:
        path = os.path.join('..', 'histdata', 'minute')
    elif frequency == bar.Frequency.DAY:
        path = os.path.join('..', 'histdata', 'day')
    filepath = os.path.join(path, instrument + market + ".csv")


    #############################################don't change #########################
    from pyalgotrade.cn.csvfeed import Feed

    barfeed = Feed(frequency)
    barfeed.setDateTimeFormat('%Y-%m-%d')#  %H:%M:%S'
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
    '''**************************************'''
    return sharp,maxdd,return_



    # print sharp,maxdd,return_
if __name__ == "__main__":
    '''**************************************'''
    # TODO :回测在此
    result = []
    import multiprocessing
    pool = multiprocessing.Pool(4)
    for i in range(5,7):
        for j in range(10,12):
            z = 20
            paras = [i,j,z]
            result.append(pool.apply_async(testStrategy,[paras]))

    pool.close()
    pool.join()


    savereturn = []
    for item in result:
        savereturn.append(item.get())
    print savereturn
