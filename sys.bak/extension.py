import pandas as pd
from zipline.data.bundles import register
from zipline.data.bundles.csvdir import csvdir_equities


start_session = pd.Timestamp('2007-1-2', tz='utc')
end_session = pd.Timestamp('2017-10-27', tz='utc')

register(
    'custom_history',
    csvdir_equities(
        ['minute'],
        '/home/kaiyan/Workspace/zipline/custom_history',
    ),
    calendar_name='CFX',
    start_session=start_session,
    end_session=end_session,
    minutes_per_day=24*60,
)
