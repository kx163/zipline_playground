from zipline.api import symbol
from zipline.data import bundles


def initialize(context):
    context.asset = symbol('GBPUSD')
    bundle = bundles.load('custom_history')
    print(bundle.asset_finder.retrieve_all(bundle.asset_finder.sids))


def handle_data(context, data):
    # print(data.current(context.asset, 'price'))
    pass
