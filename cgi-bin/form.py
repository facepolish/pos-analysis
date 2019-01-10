import cgi
import tableclass as tb
import pandas as pd
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
html_body=u"""<html><head> 
<meta charset="UTF-8" /></head>
<body>
	<form method="POST" action="/cgi-bin/result.py">
	選んでください:<select name="brand">
	%s
	</select>
	<input type="submit" />
	</form>
%s </body>
</html>"""
options=''
content=''
brand_vec=pd.read_pickle('C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/cgi-bin/brand.pkl')
brandlist = brand_vec.index
#brandlist = [u'ノースフェース','abc mart']
for br in brandlist:
    if br != u'ノースフェイス':
        select=''
    else:
        select=' selected="selected"'
    options+="<option%s>%s</option>" % (select, br)
print ("Content-type: text/html;character=utf-8\n")
print ((html_body % (options, content)))
