# -*- coding: utf-8 -*-
"""
Created on 2016.12.28

@author: haotin
"""

from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.technical import atr


class Turtle(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument,up_cum,cash_or_brk=10000):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__circ = int(up_cum)
        #self.bardata = feed[instrument]
        #self.N = atr.ATR(self.bardata, up_cum)
        self.N = atr.ATR(self.getFeed()[self.__instrument], up_cum)
        self.U = 0  # 总资金100w  self.U = acount/(50*atr)  2%最大回撤+10倍杠杆  atr day:100  10min:20  1min:5  5w本金 day :1  10min:5 1min:20 #单个市场上 最多建立4个U

        self.buyPrice = []
        self.shortPrice = []
        self.max20 = 0
        self.min10 = 0
        self.max10 = 0
        self.min20 = 0
        self.buyPrice0 = 0
        self.shortPrice0 = 0
        self.lastPrice0 = 0
        self.lastPrice1 =0






    def getPrice(self):
        return self.__prices

    def getBarData(self):
        return self.__bardata

    def onEnterCanceled(self, position):
        self.__position = None

    def onEnterOK(self):
        pass

    def onExitOk(self, position):
        self.__position = None
        #self.info("long close")

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def enterLongSignal(self):
        if self.__enterLong1 and self.__enterLong2 and self.__enter:
            return True

    def enterShortSignal(self):
        if self.__enterShort1 and self.__enterShort2 and self.__enter:
            return True

    def exitLongSignal(self):
        if self.__exitLong1 and self.__exitLong2 and not self.__longPos.exitActive():
            return True

    def exitShortSignal(self):
        if self.__exitShort1 and self.__exitShort2 and not self.__shortPos.exitActive():
            return True



    def onBars(self, bars):

        # TODO :实盘从数据库读取相关信息字段
        # print self.N[-1]# 462
        if len(self.__prices) < 20:
            return
        if self.N[-1]==0:
            return

        self.max20 = max(self.__prices[:20])
        self.min10 = min(self.__prices[:10])
        self.max10 = max(self.__prices[:10])
        self.min20 = min(self.__prices[:20])
        self.lastPrice0 = self.__prices[-1]
        self.lastPrice1 = self.__prices[-2]
        self.U = int(self.getBroker().getCash())/(100*self.N[-1]*7)


        if self.__position is None:
            if (self.lastPrice0 > self.max20) & (self.lastPrice1 <= self.max20):
                shares = self.U
                self.__position = self.enterLong(self.__instrument, shares)
                print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()
                self.buyPrice.append(self.lastPrice0)  #list of buy
                if len(self.buyPrice) > 20:
                    self.buyPrice.pop(0)


        if self.__position is not None:
            #多方止损，止盈
            if (len(self.buyPrice) > 0) and (self.__position > 0):
                if not self.__position.exitActive():
                    self.buyPrice0 = self.buyPrice[-1]
                    if  (self.lastPrice0 < self.min10) and (self.lastPrice1 >= self.min10):
                        self.__position.exitMarket()
                        self.info("sell %s" % (bars.getDateTime()))
                    if (self.buyPrice0 - self.lastPrice0 > 2*self.N[-1])  and  (self.buyPrice0 - self.lastPrice1<= 2*self.N[-1]):
                        self.__position.exitMarket()
                        self.info("sell %s" % (bars.getDateTime()))
                    #加仓
                    if (self.lastPrice0 - self.buyPrice0 > 0.5 * self.N[-1] )and (self.lastPrice1 - self.buyPrice0 <= 0.5 * self.N[-1]):
                        shares = self.U
                        self.__position = self.enterLong(self.__instrument, shares)
                        self.info(self.getActivePositions())
                        self.buyPrice.append(self.lastPrice0)
                        self.info("++ %s" % (bars.getDateTime()))
                        if len(self.buyPrice) > 20:
                            self.buyPrice.pop(0)




        #print self.U
            # self.U  = (int(self.getBroker().getCash())/100/(self.N[0])
            # print

        # if self.__position is not None:
        #     if not self.__position.exitActive() and cross.cross_below(self.__ma1, self.__ma2) > 0:
        #         self.__position.exitMarket()
        #     #self.info("sell %s" % (bars.getDateTime()))
        #
        # if self.__position is None:
        #     if cross.cross_above(self.__ma1, self.__ma2) > 0:
        #         shares = int(self.getBroker().getCash() * 0.2 / bars[self.__instrument].getPrice())
        #         self.__position = self.enterLong(self.__instrument, shares)
        #         print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()



def testStrategy():
    from pyalgotrade import bar
    from pyalgotrade import plotter

    strat = Turtle
    instrument = '600288'
    market = 'SH'
    fromDate = '20100105'
    toDate ='20150601'
    frequency = bar.Frequency.DAY
    paras = [20]
    plot = True

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
    barfeed.setDateTimeFormat('%Y-%m-%d')    # %H:%M:%S
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



    print sharp,maxdd,return_
if __name__ == "__main__":
    testStrategy()



# highs =  self.getFeed()[self.__instrument].getHighDataSeries()
# high20Value = high[-20:]
# highDate = high.getDateTimes()[-20:]
# sq = SequenceDataSeries(20)
# for i in range(20):
#     sq.appendWithDataTime(high20Date[i],high20Value[i])