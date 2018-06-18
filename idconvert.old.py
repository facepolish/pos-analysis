import pandas
import hashlib
import gc

posfile = 'pos.csv'
userfile = 'user.csv'


def createHash(userid):
    return hashlib.md5(userid).hexdigest()

def IDtoHash(filename):
    infile = '../input/'+filename
    outfile = '../output/'+filename
    
    table = pandas.read_csv(infile, encoding='utf-8')
    table['hashedid'] = createHash(postable['id'])
    table.drop('id',axix = 1)
    table.to_csv(outfile)
    
    
if __name__ == '__main__':

	df_sample =\
	pd.DataFrame([["day1","day2","day1","day2","day1","day2"],
	              ["A","B","A","B","C","C"],
	              [100,150,200,150,100,50],
	              [120,160,100,180,110,80]] ).T  #とりあえず適当なデータを作ります

	df_sample.columns = ["day_no","class","score1","score2"]  #カラム名を付ける
	df_sample.index   = [11,12,13,14,15,16]  #インデックス名を付ける
	    


#    IDtoHash(posfile)
#    IDtoHash(userfile)




