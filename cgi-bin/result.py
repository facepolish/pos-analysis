import cgi
import tableclass as tb
import pandas as pd
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
html_body = u"""
<html><head>
<meta charset="UTF-8" /></head>
  </head>
  <body>
  %s
  </body>
</html>"""
content=''

form=cgi.FieldStorage()
brand_str=str(form.getvalue('brand',''))

pos17= tb.postable(tb.posnamelist[6])
pos17 = pos17.table
brand_vec=pd.read_pickle('C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/cgi-bin/brand.pkl')
user_vec=pd.read_pickle('C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/cgi-bin/user.pkl')
#brand_str=brand_vec.index[0]

user_metric = user_vec.dot(brand_vec.loc[brand_str,:].T)
user_metric = user_metric.sort_values(ascending=False)
top100 = user_metric.index[0:100]
north_lovers = pos17[pos17.user_id.isin(top100)]
north_lovers = north_lovers[['user_id','brand','price']]

north_lovers_count = north_lovers.groupby('brand').count()
#north_lovers_count = north_lovers_count['price']
north_lovers_count=north_lovers_count.sort_values('price',ascending=False)
content=north_lovers_count.to_html()
print ("Content-type: text/html;character=utf-8\n")
print (html_body % content)

