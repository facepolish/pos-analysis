#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from posenv import posfile,userfile
from datetime import timedelta,datetime

from fbprophet import Prophet
if __name__=='__main__':

    postable = pd.read_pickle(posfile)
    postable.loc[:,'yearmonth'] = [d.strftime('%Y/%m/%d') for d in postable.purchase_date]
    monthlysales = postable.groupby('yearmonth').agg({'price':sum})
    monthlysales = monthlysales.reset_index()
    monthlysales = monthlysales.rename(columns={'price':'y','yearmonth':'ds'})

    print(monthlysales.head())
    monthlysales['y'] = np.log(monthlysales['y'])

    m = Prophet()
    m.fit(monthlysales)

    future = m.make_future_dataframe(periods=365)
    future.tail()

    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

    m.plot(forecast).savefig('1.png');

    m.plot_components(forecast).savefig('2.png');
