from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import json
import requests as r
import time
import re
import datetime
from colorama import Fore, Style, init
from urllib.parse import urlparse
from urllib.parse import quote
import requests as r
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located as prec
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import selenium
import argparse
parser = argparse.ArgumentParser(
    description="вывести названия и цены товаров по ссылкам и посчитать общую цену.")
parser.add_argument(
    "file", help="файл (путь к файлу) JSON для извлечения ссылок")
parser.add_argument(
    "-o", "--out", help="путь для JSON-файла с выводом (по умолчанию: не выводить в JSON)")
parser.add_argument(
    "-g", "--graph", help="путь для JSON-файла с выводом данных для построения графика (по умолчанию: не выводить)")
parser.add_argument("-n", "--no-headless",
                    help="запускать браузер не в фоне", action="store_true")
args = parser.parse_args()
# from bs4 import BeautifulSoup as bs4
# from lxml.html.soupparser import fromstring as bs4
pricc = {"None": 0}


def su(*args):
    a = args[0]
    for i in args[1:]:
        a += i
    return a


"""
prices = {"dns": ["span", {"class": "current-price-value", "data-role": "current-price-value"}],
          "indicator": ["div", {"class": "new-price"}]}
names = {"dns": ["h1", {"class": "page-title price-item-title"}],
         "indicator": ["h1", {"class": "ty-product-block-title"}]}
"""
prices = {"dns-shop": [By.CSS_SELECTOR, "span.product-card-price__current"],
          "indicator": [By.CSS_SELECTOR, ".new-price"],
          "regard": [By.CSS_SELECTOR, "span.price"],
          "123": [By.CSS_SELECTOR, ".pc-mb-price"],
          "avito": [By.CSS_SELECTOR, ".price-value_side-card > span:nth-child(1) > span:nth-child(1)"],
          "youla": [By.CSS_SELECTOR, ".sc-qQKPx"],
          "computeruniverse": [By.CSS_SELECTOR, 'div[class="prices at__prices"]>div:not([class])>span,div[class="prices at__prices"]>span[class="at__altcurrencyvalue"]>font'],
          "nix": [By.CSS_SELECTOR, ".price > span"],
          "fotosklad": [By.CSS_SELECTOR, 'meta[itemprop=price]'],
          "citilink": [By.CSS_SELECTOR, "div.price > ins:nth-child(1)"],
          "coolera": [By.CSS_SELECTOR, 'form[action="case.php"]:nth-child(1)'],
          "os-com": [By.CSS_SELECTOR, ".ty-price[id^=line_discounted_price_]"],
          "nwht": [By.CSS_SELECTOR, ".price_value"],
          "computermarket": [By.CSS_SELECTOR, "div[class='cnt-price add-tovar cf']"],
          "beru": [By.CSS_SELECTOR, 'div[data-auto="price"]>span>span:not([data-auto="currency"])']}
names = {"dns-shop": [By.CSS_SELECTOR, ".page-title"],
         "indicator": [By.CSS_SELECTOR, ".ty-product-block-title"],
         "regard": [By.CSS_SELECTOR, '[id="goods_head"]'],
         "123": [By.CSS_SELECTOR, "h1.hidden-xs"],
         "avito": [By.CSS_SELECTOR, ".title-info-title-text"],
         "youla": [By.CSS_SELECTOR, ".sc-fznZeY"],
         "computeruniverse": [By.CSS_SELECTOR, ".product-name"],
         "nix": [By.CSS_SELECTOR, "span.temp_classH11:nth-child(30)"],
         "fotosklad": [By.CSS_SELECTOR, 'h1[itemprop=name]'],
         "citilink": [By.CSS_SELECTOR, ".product_header > h1:nth-child(2)"],
         "nix": [By.CSS_SELECTOR, "span.temp_classH11:not([style])"],
         "coolera": [By.CSS_SELECTOR, 'body > div.main > div.cont > div > h3'],
         "os-com": [By.CSS_SELECTOR, ".ut2-pb__title"],
         "nwht": [By.CSS_SELECTOR, "h1[id=pagetitle]"],
         "computermarket": [By.CSS_SELECTOR, '.product-name > h1:nth-child(1)'],
         "beru": [By.CSS_SELECTOR, 'div[data-zone-name="summary"]>div>div>div>div>div>h1']
         }
prices["technopoint"], names["technopoint"] = [i["dns-shop"]
                                               for i in [prices, names]]
prices_out = []
out = {"Конфигурация": {}}
rates = r.get(
    "https://api.exchangeratesapi.io/latest?base=RUB&symbols=EUR,USD").json()["rates"]
rates = [rates[i] for i in list(rates.keys())]
headers = {
    'authority': 'technopoint.ru',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '"Chromium";v="85", "\\\\Not;A\\"Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4148.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://technopoint.ru/',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
}
cu_request = """fetch('https://www.computeruniverse.net/ru/changedeliverycountrymasked', {
    method: 'POST',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.computeruniverse.net',
        'Connection': 'keep-alive',
        'Referer': 'https://www.computeruniverse.net/ru/corsair-virtuoso-rgb-wireless-hi-fi-gaming-headset-carbon',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
        'Cookie': '__cfduid=ded6069a521b46383c37a2a593cebd4fb1592736469; Nop.IsSearchEngine=False; cuncid=1769162468; Nop.customer=84ead155-f043-4179-8a13-67566ffd1880; eu=UA; languageId=3; ASP.NET_SessionId=leq1yywyxtfiedqiubdl3voe; __RequestVerificationToken=ozY4BbYM3W0E1nI6BNRN_e9YdmqbBWf0TOW9p0S3cULdhHbcYy1p6bxtoxNlfLkISfLtMyX2uNQl2tQpygsyszm57B_-QBFnpbnhTv7Uiw01; _dy_ses_load_seq=89355%3A1592736519168; _dy_csc_ses=t; _dy_c_exps=; _dy_soct=1001551.1001955.1592736519*1008289.1013217.1592736522*1010721.1018046.1592736522*1010727.1018052.1592736522*1020534.1036745.1592736522; _dycnst=dg; wt_cdbeid=1; wt3_eid=%3B977787962413082%7C2159273647543813931%232159273652067802471; wt3_sid=%3B977787962413082; wt_rla=977787962413082%2C2%2C1592736475458; _ALGOLIA=anonymous-a4f88bb2-a6ad-4303-a038-b354742a4e5d; wacucs15d=3741650748324592; cwd3741650748324592={"p1":12,"p2":18,"t1":30,"t2":15,"sessions":{"8369876861487243":1},"cu_bm":false,"os":"win","os_rv":"10","wb":"ff","wb_rv":"","id":"111379020"}; wacucs15s=8369876861487243; cws8369876861487243={"firstaction":true,"multiple":0,"traffic":"","ref":"direct","landing":"https://www.computeruniverse.net/ru/corsair-virtuoso-rgb-wireless-hi-fi-gaming-headset-carbon","pagecount":2,"productcount":2,"prod_age":{},"id":"129308471"}; vwo_user_n=0; DeliveryCountrySet=66; Nop.DeliveryCountry=RU; _dy_c_att_exps='
    },
    body: 'targetCountryId=66&returnUrl=VFNMIK>{F{F{F{F'
});
"""
init()
gr = Fore.GREEN
rd = Fore.RED
ye = Fore.YELLOW
sr = Style.RESET_ALL


try:
    with open(args.file, "rb") as file:
        a = json.loads(file.read().decode("utf-8"))["Конфигурация"]
except FileNotFoundError as e:
    raise FileNotFoundError(e, "Ошибка! Файла нет.")
except PermissionError as e:
    raise PermissionError(e, "Нет прав для чтения файла.")
# os.environ['MOZ_HEADLESS'] = '1'
caps = DesiredCapabilities().FIREFOX
caps["pageLoadStrategy"] = "normal"
namm = ""
opts = Options()
opts.set_preference("permissions.default.image", 2)
if not args.no_headless:
    opts.headless = True
# profile = webdriver.FirefoxProfile(os.path.join(os.getcwd(), "lol"))
"""
profile = webdriver.FirefoxProfile()
profile.add_extension(extension=os.path.join(os.getcwd(), "ublock.xpi"))
profile.set_preference("toolkit.startup.max_resumed_crashes", "-1")"""
driver = webdriver.Firefox(desired_capabilities=caps, options=opts)
wait = WebDriverWait(driver, 20)
not_done_cu = True


def getId(prices, namm):
    oo = []
    for i in range(2):
        try:
            return list(prices.keys())[list(prices.keys()).index(namm[i])]
        except IndexError:
            pass
        except KeyError:
            pass
        except ValueError:
            pass
    return False


done_shops = []
not_done = {"dns-shop": True, "technopoint": True, "computeruniverse": True}
for i in list(a.keys()):
    print(f"{gr} {i} {sr}-->")
    out["Конфигурация"][i] = {}
    for ii in list(a[i].keys()):
        out["Конфигурация"][i][ii] = []
        if type(a[i][ii]) == type(0) or (a[i][ii].isdigit() if type(a[i][ii]) != type([]) else False):
            print(f"{gr}\t{ii} (цена):{sr}", f"{rd}{a[i][ii]} рублей{sr}")
            [out["Конфигурация"][i][ii].append(iii) for iii in [
                ""]*2+[f"{a[i][ii]} рублей", int(a[i][ii])]]
            prices_out.append(int(a[i][ii]))
        else:
            print(f"\t{gr}{ii}{sr}:", end=" ")
            namm = (a[i][ii] if type(a[i][ii]) != type(
                []) else a[i][ii][0]).split(".")[0:2]
            now = [urlparse(a[i][ii] if type(a[i][ii]) == type("") else a[i][ii][0], "https").geturl().replace(
                "///", "//"), getId(prices, namm)]
            out["Конфигурация"][i][ii].append(now[0])
            try:
                driver.get(now[0])
            except:
                now[0] = now[0].replace("https://", "http://")
                driver.get(now[0])
            # (now[1] == "dns-shop") and (not (now[1] in done_shops)):
            if (now[1] in ["dns-shop", "technopoint"]) and not_done[now[1]]:
                time.sleep(0.2)
                wait.until(
                    prec((By.CSS_SELECTOR, "body > header > div.header-top > div > ul.header-top-menu__common-list > li:nth-child(1) > div > div")))
                time.sleep(0.2)
                aaasd = driver.find_element(
                    By.CSS_SELECTOR, "body > header > div.header-top > div > ul.header-top-menu__common-list > li:nth-child(1) > div > div")
                aaasd.click()
                wait.until(
                    prec((By.CSS_SELECTOR, 'input.form-control')))
                field = driver.find_element_by_css_selector(
                    'input.form-control')
                field.click()
                # driver.switch_to.alert.dismiss()
                # actions = ActionChains(driver)
                # actions.send_keys("Севасто")
                # actions.perform()
                field.send_keys("Севасто")
                wait.until(
                    prec((By.CSS_SELECTOR, '.city-choice')))
                # actions = ActionChains(driver)
                # actions.send_keys(Keys.RETURN)
                # actions.perform()
                field.send_keys(Keys.RETURN)
                # wait.until(prec(
                #    (By.XPATH, "/html/body/div[1]/div[3]/div[3]/div[2]/div/div[3]/div[1]/div[1]/div/div/div/div[2]/span")))
                wait.until(prec((By.CSS_SELECTOR, ".city-select")))
                not_done[now[1]] = False
            elif now[1] == "computeruniverse" and not_done[now[1]]:
                time.sleep(0.3)
                driver.execute_script("""document.body.insertAdjacentHTML('beforeend','<span class="country_option CU-span-hyperlink CU-span-hyperlink-blue" onclick="submitCountryMaskedChange(this);" data-submit="66" data-cf-modified-63a74e0a7bcc6fbda43be171-="" id="mamama">Российская Федерация</span>')""")
                elem = driver.find_element_by_id("mamama")
                elem.click()
                not_done[now[1]] = False
            elif now[1] in ["dns-shop", "technopoint"]:
                wait.until(prec((By.CSS_SELECTOR, ".city-select")))
            elif now[1] == "indicator":
                wait.until(
                    prec((By.XPATH, "//*[starts-with(@id, 'sec_discounted_price_')]")))
            # driver.delete_cookie(driver.get_cookie("city_path"))
            # driver.add_cookie(
            #    {"name": 'city_path', "value": 'sevastopol'})  # ,
            #                   "domain": f".{a[i][ii][:a[i][ii].find('/')+1]}"})
            # driver.refresh()
            # time.sleep(3)
            # bs = bs4(driver.page_source)
            if now[1] in ["dns-shop", "technopoint"]:
                time.sleep(5)
            # wait.until(prec(tuple(prices[now[1]])))
            name = driver.find_element(
                *(names[now[1]])).text.strip()
            name_parsed2 = name if type(a[i][ii]) == type(
                "") else "{} (в кол-ве {})".format(name, a[i][ii][1])
            name_parsed = re.findall(r"[0-9A-z](?:.*)", name_parsed2)
            if name_parsed == None or len(name_parsed) == 0:
                name_parsed = [name_parsed2]
            print(
                f"{ye}{' '.join(name_parsed)}{sr}", end=" ")
            out["Конфигурация"][i][ii].append(name_parsed)

            """
            if now[1] == "computeruniverse":
                pric = driver.find_element(
                    *(prices[now[1]])).get_attribute('innerHTML')
                price = re.findall(
                    r"[\d,]+\ <", pric)[0][:-1].replace(",", ".").strip()
                price_parsed2 = float(
                    (price))*(1/rates[0])*(a[i][ii] if type(a[i][ii]) == type([]) else 1)
                price_parsed = f"{round(price_parsed2,2)} рублей{sr} ({price} евро)"
            else:
                pric = driver.find_element(*(prices[now[1]]))
                tag = re.findall(
                    r"<(.*?)\ ", pric.get_attribute("outerHTML"))[0]
                if tag == "meta":
                    price = pric.get_attribute("content").strip()
                else:
                    price = pric.text.strip()
                price_parsed2 = str(int(float(".".join(re.findall(
                    r'(?:[\d](?:.?=[A-zА-яЁё]||\.))+', "".join(price.split(" "))))))*(a[i][ii][1] if type(a[i][ii]) == type([]) else 1))
                price_parsed = (price_parsed2+" рублей") if type(a[i][ii]) != type([]) else (str(int(float(".".join(re.findall(
                    r'(?:[\d](?:.?=[A-zА-яЁё]||\.))+', "".join(price.split(" ")))))))+"x"+str(a[i][ii][1])+f" ({price_parsed2})")"""
            price = driver.find_element(
                *(prices[now[1]])).text.strip()
            pric = driver.find_element(*(prices[now[1]]))
            """    pric = driver.find_element(
                    By.CSS_SELECTOR, ".at__prices > div:nth-child(6) > span:nth-child(1) > font:nth-child(1)")
            tag = re.findall(
                r"<(.*?)\ ", pric.get_attribute("outerHTML"))[0]
            if tag == "meta":
                price = pric.get_attribute("content").strip()"""
            if True:  # else
                price = pric.text.strip().replace(",", ".")
            price_parsed2 = str(int(float(".".join(re.findall(
                r'(?:[\d](?:.?=[A-zА-яЁё]||\.))+', "".join(price.split(" "))))))*(a[i][ii][1] if type(a[i][ii]) == type([]) else 1))
            price_parsed = (price_parsed2+" рублей") if type(a[i][ii]) != type([]) else (str(int(float(".".join(re.findall(
                r'(?:[\d](?:.?=[A-zА-яЁё]||\.))+', "".join(price.split(" ")))))))+"x"+str(a[i][ii][1])+f" ({price_parsed2})")
            print(f"-- {rd}{price_parsed}{sr}.")
            out["Конфигурация"][i][ii].append(price_parsed)
            out["Конфигурация"][i][ii].append(int(price_parsed2))
            prices_out.append(int(price_parsed2))
            done_shops.append(now[1])
            # time.sleep(5)
    pricc[i] = sum(prices_out)-sum(list(pricc.values()))
    print(f" Итого (цена) [{gr}{i}{sr}] -- {rd}{pricc[i]}{sr}.")
driver.quit()
summm = sum(prices_out)
itogo = f"Итого (цена): {rd}{summm} рублей{sr}, {round(summm*rates[1],2)} долларов, {round(summm*rates[0],2)} евро."
print(itogo)
out["Итого (цена)"] = summm
out["Итого (цена) (USD)"] = summm*rates[1]
out["Итого (цена) (EUR)"] = summm*rates[0]
out["Итого (цена)_text"] = f"Итого (цена): {rd}{summm} рублей{sr}, {round(summm*rates[1],2)} долларов, {round(summm*rates[0],2)} евро."
dt = str(datetime.datetime.now())
bb = {dt: {}}
for i in zip(su(*[list(a[i].keys()) for i in [*list(a.keys())]]), prices_out):
    bb[dt][i[0]] = i[1]
bb[dt]["Итого"] = summm
if args.graph:
    try:
        with open(args.graph, "rb") as file:
            graphdata = json.loads(file.read().decode("utf-8"))
        graphdata.update(bb)
    except:
        graphdata = bb
    with open("graph.json", "wb") as file:
        file.write(json.dumps(
            graphdata, indent=2, ensure_ascii=False).encode("utf-8"))
if args.out:
    try:
        with open(args.out, "wb") as file:
            file.write(json.dumps(out, indent=2,
                                  ensure_ascii=False).encode("utf-8"))
    except PermissionError as e:
        raise PermissionError(e, "Недостаточно прав для записи в файл вывода.")
