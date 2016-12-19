# !/usr/bin/python
# vim: set fileencoding=utf8 :
#
__author__ = 'keping.chu'


from pyalgotrade import strategy
from updaytech import UP318
from basetech import LimitPrice, CloseAvg
from pyalgotrade.broker.backtesting import LimitOrder, Broker


class LimitOrderDays(LimitOrder):

    def __init__(self, action, instrument, limitPrice, quantity, instrumentTraits):
        super(LimitOrderDays, self).__init__(action, instrument, limitPrice, quantity, instrumentTraits)
        self.days = 1


class MOrder:

    def __init__(self, order):

        self.order = order
        self.days = 1


class LeftBroker(Broker):

    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        return LimitOrderDays(action, instrument, limitPrice, quantity, self.getInstrumentTraits(instrument))

    def commitOrderExecution(self, order, dateTime, fillInfo):
        #
        if order.isSell():
            ins = order.getInstrument()
            amt = self.getShares(ins)
            if amt <= 0:
                return

        super(LeftBroker, self).commitOrderExecution(order, dateTime, fillInfo)


class UpStrategy(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument, days=5):
        self.broker = LeftBroker(4000000, feed)
        super(UpStrategy, self).__init__(feed, self.broker)
        self.instrument = instrument
        self.up_ = {}
        self.li_ = {}
        self.ca_ = {}
        self.days_ = days
        self.default_day = days
        self.positions = {}
        for stock in self.instrument:
            self.up_[stock] = UP318(feed.getDataSeries(stock), 5)
            self.li_[stock] = LimitPrice(feed.getDataSeries(stock), 2)
            self.ca_[stock] = CloseAvg(feed.getDataSeries(stock), 2)

    def onBars(self, bars):
        #订单计时
        self.sales(bars)
        self.buy(bars)

    def sales(self, bars):
        for ins, order in self.positions.items():
            #达到限定天数卖出
            bar = bars.getBar(order.order.getInstrument())
            if bar:
                ca = self.ca_[ins]
                if not ca[-1]:
                    self.marketOrder(ins, -order.order.getQuantity())
                    self.info("sales [%s %s %s]" % (order.order.getInstrument(), bar.getDateTime(), order.days))
                    del self.positions[ins]

    def buy(self, bars):
        for stock, bar in bars.items():
            up = self.up_[stock]
            #满足指标买入
            if up[-1] and (self.positions.get(stock) is None) and (self.li_[stock][-1] < 0.99) and self.ca_[stock][-1]:
                order = self.marketOrder(stock, self.round(bar.getClose()))
                self.info("buy [%s, %s, %s]" % (stock, bar.getClose(), order.getQuantity()))
                self.positions[stock] = MOrder(order)

    def round(self, price, cash=5000):
        ratio = self.getResult() / 4000000
        amount = int(int(cash * ratio / price) / 100) * 100
        if amount == 0:
            amount = 100
        return amount

