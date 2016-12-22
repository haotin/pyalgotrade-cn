# -*- coding: utf-8 -*-

from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.technical import atr

class Turtle(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, up_cum):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__circ = int(up_cum)
        # TODO : ATR公式确认  self.__N = atr.ATR(self.__prices, 20)
        self.__U = 1

        self.lastPrice = []
        self.buyPrice = []
        self.shortPrice = []
        self.max20 = 0
        self.min10 = 0
        self.max10 = 0
        self.min20 = 0

    def getPrice(self):
        return self.__prices

    def getatr(self):
        return self.__N

    def onEnterCanceled(self, position):
        self.__position = None

    def onEnterOK(self):
        pass

    def onExitOk(self, position):
        self.__position = None
        #self.info("long close")

    def onExitCanceled(self, position):
        self.__position.exitMarket()


    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.

        # TODO: 初始化 if self.__ma2[-1]is None:
           #  return

        if self.__position is not None:
            if not self.lastPrice0:
                self.lastPrice0 = [self.__instrument].getPrice()
            else:
                self.lastPrice1 = self.lastPrice0
                self.lastPrice0 = [self.__instrument].getPrice()
                self.lastPrice.append(self.lastPrice1)
            if len(self.lastPrice) > 20:
                self.lastPrice.pop(0)

            # TODO : 取到20单位时间k线(从数据库初始化)
            if len(self.lastPrice) == 20:

                self.max20 = max(self.lastPrice)
                self.min10 = min(self.lastPrice[9:])
                self.max10 = max(self.lastPrice[9:])
                self.min20 = min(self.lastPrice)

            if not self.__position.exitActive() and cross.cross_below(self.__prices, self.min20) > 0:
                self.__position.exitMarket()
                #self.info("sell %s" % (bars.getDateTime()))

        if self.__position is None:
            if cross.cross_above(self.__prices, self.max20) > 0:
                shares = int(self.getBroker().getCash() * 0.2 / bars[self.__instrument].getPrice())
                self.__position = self.enterLong(self.__instrument, shares)
                print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()
                #self.info("buy %s" % (bars.getDateTime()))


def testStrategy():
    from pyalgotrade import bar
    from pyalgotrade import plotter

    strat = Turtle
    instrument = '600288'
    market = 'SH'
    fromDate = '20150101'
    toDate ='20150601'
    frequency = bar.Frequency.MINUTE
    paras = [20]
    plot = True

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



if __name__ == "__main__":
    testStrategy()
































