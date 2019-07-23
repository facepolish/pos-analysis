import numpy as np
import pandas as pd
from bi.posenv import postempfile,itemdbfile,postempfile2
from bi.tableclass import posaddcols,convert_table


if __name__=='__main__':

    table2 = pd.read_pickle(postempfile)
    table5 = pd.read_pickle(itemdbfile)
    table2 = convert_table(table2)
    table5 = convert_table(table5)

    janinpos = set(table2.jan_code)
    table5 = table5.reset_index()
    janindb = set(table5.jan_code)
    pos_diff = janinpos - janindb
    print ("pos jan count is "+str(len(janinpos)))
    print("jan in db count is "+str(len(janindb)))
    print ("POS only jan count is "+str(len(pos_diff)))
#    nans = (table2.user_id == np.nan)
#    nan_count = nans.sum()
#    print ("nan in user_id is "+str(len(nan_count)))
    table2 = posaddcols(table2)
    table2 = pd.merge(table2,table5,on='jan_code',how='inner')
    table2.cost = table2.cost.fillna(0)

    table2.to_pickle(postempfile2)
    print (table2.columns)
