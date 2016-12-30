# -*- coding: utf-8 -*-
import tushare as ts
import pandas as pd
import os
import datetime
pd.set_option('display.width', 350)


df = pd.read_csv('f:/data/trade.csv',sep='\t',encoding = 'gbk')
df = df[['StockName','OpenDate']]



instrument = raw_input("input code: ")
if instrument[0]=='6':market = 'SH'
else:market = 'SZ'

path1 = os.path.join('f:\\pyalgotrade-cn-master', 'histdata', 'day')
filepath1 = os.path.join(path1, instrument + market + ".csv")

fromDate = '20160501'
__TD=datetime.date.today()
end1 =__TD.strftime('%Y-%m-%d')
toDate=__TD.strftime('%Y%m%d')
# 得到15分钟数据（股票300336,始于2016-01-01,止于2016-05-24,15分钟数据）
data = ts.get_h_data(instrument,start='2012-01-01',end=end1)
# 数据存盘
data.to_csv('f:\\pyalgotrade-cn-master/histdata/15-300336-2016.csv')
# 读出数据，DataFrame格式
df = pd.read_csv('f:\\pyalgotrade-cn-master/histdata/15-300336-2016.csv')
# 从df中选取数据段，改变段名；新段'Adj Close'使用原有段'close'的数据
df2 = pd.DataFrame({'datetime' : df['date'], 'open' : df['open'],
                    'high' : df['high'],'close' : df['close'],
                    'low' : df['low'],'volume' : df['volume'],
                    'close':df['close'],
                    'amount':df['amount']})
# 按照Yahoo格式的要求，调整df2各段的顺序
dt = df2.pop('datetime')
df2.insert(0,'datetime',dt)
o = df2.pop('open')
df2.insert(1,'open',o)
h = df2.pop('high')
df2.insert(2,'high',h)
l = df2.pop('low')
df2.insert(3,'low',l)
c = df2.pop('close')
df2.insert(4,'close',c)
v = df2.pop('volume')
df2.insert(5,'volume',v)
a = df2.pop('amount')
df2.insert(5,'amount',a)
df3=df2.sort_values('datetime')
df3['datetime']=df3['datetime']+' 16:00:00'
df3.to_csv(filepath1, index=False)
# 新格式数据存盘，不保存索引编号
from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross

class DoubleMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, n, m):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__malength1 = int(n)
        self.__malength2 = int(m)

        self.__ma1 = ma.EMA(self.__prices, self.__malength1)
        self.__ma2 = ma.EMA(self.__prices, self.__malength2)

    def getPrice(self):
        return self.__prices

    def getSMA(self):
        return self.__ma1,self.__ma2

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

        if self.__ma2[-1]is None:
            return

        if self.__position is not None:
            if not self.__position.exitActive() and cross.cross_below(self.__ma1, self.__ma2) > 0:
                self.__position.exitMarket()
                #self.info("sell %s" % (bars.getDateTime()))

        if self.__position is None:
            if cross.cross_above(self.__ma1, self.__ma2) > 0:
                shares = int(self.getBroker().getEquity() * 0.2 / bars[self.__instrument].getPrice())
                self.__position = self.enterLong(self.__instrument, shares)
                print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()
                #self.info("buy %s" % (bars.getDateTime()))


def testStrategy():
    from pyalgotrade import bar
    from pyalgotrade import plotter

    strat = DoubleMA
    frequency = bar.Frequency.DAY
    paras = [5, 20]
    plot = True
#############################################path set ############################33
    import os
    if frequency == bar.Frequency.MINUTE:
        path = os.path.join('f:\\pyalgotrade-cn-master', 'histdata', 'minute')
    elif frequency == bar.Frequency.DAY:
        path = os.path.join('f:\\pyalgotrade-cn-master', 'histdata', 'day')
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
'''