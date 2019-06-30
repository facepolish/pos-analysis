import requests,bs4
import urllib
import difflib
import unicodedata
import re
#'好日山荘'

class extnum(object):
    re_num = '[0-9０-９a-zA-Zａ-ｚＡ-Ｚ]+'
    num = re.compile(re_num)
    def GetNumList(self,st):
        norm_st = unicodedata.normalize('NFKC',st)
        ret = self.num.findall(norm_st)
        return(ret)
def UtfSafe(buf):
    buf = buf.replace(u"\uff3c",u"\u005c")
    buf = buf.replace(u"\uff5e",u"\u301c")
    buf = buf.replace(u"\u2225",u"\u2016")
    buf = buf.replace(u"\uff0d",u"\u2212")
    buf = buf.replace(u"\uffe0",u"\u00a2")
    buf = buf.replace(u"\uffe1",u"\u00a3")
    buf = buf.replace(u"\uffe2",u"\u00ac")
#    buf = unicodedata.normalize('NFKC',buf)
    return(buf)
def HaveAllNum(target,numlist):
    norm_target = unicodedata.normalize('NFKC',target)
    for item in numlist:
        if target.find(item) == -1:
            return False
    return(True)
def GetPricefromKakaku(brand,itemid,exclude=None):
    kakaku_query = 'https://kakaku.com/search_results/'
    brand_code = UtfSafe(brand)
    item_code = UtfSafe(itemid)
    brand_code = urllib.parse.quote(brand_code.encode('shift-jis'))
    item_code = urllib.parse.quote(item_code.encode('shift-jis'))
    space = '%20'
    commandstr = kakaku_query+str(itemid)+'/'
#    commandstr = kakaku_query+brand_code+space+item_code
    print (commandstr)
    res = requests.get(commandstr)
    
    num = extnum()
    numlist = num.GetNumList(itemid)

    soup = bs4.BeautifulSoup(res.text,"html.parser")
    elems = soup.select('.c-positioning.p-result_item_row')
#    elems = soup.select('.p-result_item_linkArea.s-biggerlink.is-biggerlinkHot')
    shoplist = []
    for elem in elems:
        price = elem.find('p',class_='p-item_price')
        price = price.find('span')
        price = price.text
        shop = elem.find('img',class_='p-result_item_mallImg')
        if shop is None:
            continue
        else:
            shop = shop['alt']
        if not (exclude is None) and shop[:len(exclude)]==exclude:
            continue
        image = elem.find('a',class_ = 'p-item_visual')
        link = image['href']
        image = image.find('img',class_ ='p-item_visual_entity' )
        image_text = image['alt']
#        if not HaveAllNum(image_text,numlist):
#            continue
        image = image['data-original']
        item = {'shop':shop,'image':image,'text':image_text,'price':price,'link':link}
        shoplist.append(item)
    shoplist = sorted(shoplist, key=lambda x:x['price'])
    return(shoplist)

if __name__=='__main__':
    shopdic = GetPricefromKakaku('マウントギア','MTG-29')
    for l in shopdic:
        print ('shop = '+l[0]+' price = '+l[3])
        print ('detail = '+l[1])
        print ('photo is '+l[2])
        print ('shop link is '+l[4])
    
