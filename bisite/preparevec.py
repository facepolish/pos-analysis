from bi.createitemvec import ItemRecommend
from bi import posenv
import pandas as pd

if __name__=='__main__':
#    f=open(posenv.deptfile,'rb')
#    lis=pickle.load(f)
#    print(lis)
#    posfile = "c:/Users/ttmuyn/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl"
    table = pd.read_pickle(posenv.posfile)
#    vec_update(table)
    it_rec = ItemRecommend(newfile=True)
    it_rec.vec_update(table)

    '''
    sampleitem = table.loc[table.index[10],'jan_code']
    print ('sample item is '+sampleitem)
    list = it_rec.getsamecartrecommendlist(sampleitem)
    print ('same cart recommends are')
    print (list[1:11])

    list = it_rec.getsamecustomerrecommendlist(sampleitem)
    print ('Customer based recommends are')
    print (list[1:11])
    '''

