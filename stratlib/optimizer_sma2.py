# -*- coding: utf-8 -*-


import itertools
from pyalgotrade.optimizer import local
from pyalgotrade.barfeed import yahoofeed
import thrSMA
from pyalgotrade import bar


# ==========================================FeedLocalCsv========================

def parameters_generator():
    instrument = ['600288']
    long_1 = range(20, 22)
    short_l = range(2, 5)
    up_cum = range(19, 20)
    return itertools.product(instrument, short_l, long_1,up_cum)

if __name__ == "__main__":

    instrument = '600288'
    market = 'SH'
    fromDate = '20150101'
    toDate ='20150601'
    frequency = bar.Frequency.MINUTE
           #####################path set #######################
    import os
    if frequency == bar.Frequency.MINUTE:
        path = os.path.join('..', 'histdata', 'minute')
    elif frequency == bar.Frequency.DAY:
        path = os.path.join('..', 'histdata', 'day')
    filepath = os.path.join(path, instrument + market + ".csv")


           ##################don't change #####################
    from pyalgotrade.cn import csvfeed
    feed = csvfeed.Feed(frequency)
    feed.setDateTimeFormat('%Y-%m-%d %H:%M:%S')                # %H:%M:%S'
    feed.loadBars(instrument, market, fromDate, toDate, filepath)

    local.run(thrSMA.thrSMA, feed, parameters_generator())

# ==========================================feed yahoofeed======================
#
# def parameters_generator():
#     instrument = ["11gdx"]
#     long_1 = range(20, 50)
#     short_l = range(2, 10)
#     up_cum = range(19, 20)
#     return itertools.product(instrument, short_l, long_1,up_cum)
#
# if __name__ == "__main__":
#
#     feed = yahoofeed.Feed()
#     feed.addBarsFromCSV("11gdx", "gdx-2006-yahoofinance.csv")
#     print feed.addBarsFromCSV()
#     local.run(thrSMA.thrSMA, feed, parameters_generator())

