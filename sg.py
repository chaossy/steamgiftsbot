import lxml.html
import requests
import json
import sys
import time
import os

working_dir = os.path.split(os.path.realpath(__file__))[0]
f = open(working_dir+'/cookie.txt', "r+")
cookie = f.read()
if not cookie:
    print('no cookie found, exit')
    sys.exit()
f.close()

base_url = ('https://www.steamgifts.com')

site_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,de;q=0.2',
    # 'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'PHPSESSID='+cookie,
    'Host': 'www.steamgifts.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

# Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
# Accept-Encoding:gzip, deflate, sdch
# Accept-Language:zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,de;q=0.2
# Connection:keep-alive
# Cookie:_gat=1; _ga=GA1.2.1263490937.1451986023; PHPSESSID=9amug2klqsjb8d8t8oqlovd1pt62q70q2n81l36m4o6ip9fbiu0smdomav4act6mlhg68seo8qus4uno5235luo9cilsrs2uncpk7u1
# Host:www.steamgifts.com
# Upgrade-Insecure-Requests:1
# User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36


enter_headers = {
    'Accept':'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,de;q=0.2',
    'Connection':'keep-alive',
    # 'Content-Length':'70',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'PHPSESSID='+cookie,
    'Host':'www.steamgifts.com',
    'Origin':'http://www.steamgifts.com',
    'Referer':'http://www.steamgifts.com/giveaway/rH8eR/trouble-in-the-manor',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
}

def get_user_pt(html_element):
    pt = html_element.xpath("//span[@class='nav__points']")[0]
    pt = int(pt.text)
    return pt

def loop_page(page_url):
    r = requests.get(page_url, headers=site_headers)
    html_element = lxml.html.document_fromstring(r.text)

    if get_user_pt(html_element) < 10:
        return True

    game_elements = html_element.xpath("//div[@class='giveaway__summary']")
    # user_level = xmldata.xpath("//a[@href='/account']")
    # user_level_element = xmldata.xpath("//span[@title='1.27']")[0]
    # user_level = int(user_level_element.text.split(' ')[1])
    for game_element in game_elements:
        neg_level_elements = game_element.xpath(".//div[@class='giveaway__column--contributor-level giveaway__column--contributor-level--negative']")
        if neg_level_elements:
            # required_level = int(level_elements[0].text.split(' ')[1][:-1])
            # if user_level < required_level:
            continue
        code_element = game_element.xpath(".//a[@class='giveaway__heading__name']")[0]
        href = code_element.attrib['href']
        code = href.split('/')[2]
        post_data = {
            'xsrf_token':xsrf_token,
            'do':'entry_insert',
            'code':code,
        }
        r = requests.post(base_url+'/ajax.php', headers=enter_headers, data=post_data)
        pt = int(json.loads(r.content)['points'])
        if pt < 20:
            return True
        time.sleep(2)
    return False


while True:
    r = requests.get(base_url, headers=site_headers)
    html_element = lxml.html.document_fromstring(r.text)
    xsrf_token_elements = html_element.xpath("//input[@name='xsrf_token']")
    if not xsrf_token_elements:
        print("xsrf token not found (maybe cookie expired?), exit")
        sys.exit()
    xsrf_token = xsrf_token_elements[0].value
    # xsrf_token = 'f2a22d7a5fa0f68757a9d407d536ed1e'

    if loop_page(base_url+'/giveaways/search?type=wishlist'):
        print("loop done")
    else:
        for page in range(100):
            url = '' if page == 0 else '/giveaways/search?page=' + str(page+1)
            if loop_page(base_url+url):
                print("loop done")
                break
    pt = 0
    while pt < 160:
        print("Current pt: "+str(pt)+". Sleep 30 mins")
        time.sleep(1800)
        r = requests.get(base_url, headers=site_headers)
        html_element = lxml.html.document_fromstring(r.text)
        pt = get_user_pt(html_element)