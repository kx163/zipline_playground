from zipline.api import order_target, record, symbol
import matplotlib.pyplot as plt


def initialize(context):
    context.i = 0
    context.asset = symbol('AAPL')


def handle_data(context, data):
    context.i += 1
    if context.i < 300:
        return

    short_ma = data.history(context.asset, 'price', bar_count=100, frequency='1d').mean()
    long_ma = data.history(context.asset, 'price', bar_count=300, frequency='1d').mean()

    if short_ma > long_ma:
        order_target(context.asset, 100)
    if short_ma < long_ma:
        order_target(context.asset, 0)

    record(AAPL=data.current(context.asset, 'price'), short_ma=short_ma, long_ma=long_ma)


def analyze(context, perf):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    perf.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value in $')

    ax2 = fig.add_subplot(212)
    perf['AAPL'].plot(ax=ax2)
    perf[['short_ma', 'long_ma']].plot(ax=ax2)

    perf_trans = perf.ix[[t != [] for t in perf.transactions]]
    buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
    sells = perf_trans.ix[[t[0]['amount'] < 0 for t in perf_trans.transactions]]
    ax2.plot(buys.index, perf.short_ma.ix[buys.index], '^', markersize=10, color='m')
    ax2.plot(sells.index, perf.long_ma.ix[sells.index], 'v', markersize=10, color='k')
    plt.legend(loc=0)
    plt.show()
