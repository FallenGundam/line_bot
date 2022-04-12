# coding=utf-8


import requests,os,json

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('zR4+oCrvH8sBV/jC9iN5WLjJEQTN/enjCAfaOVM0Nl3mqRFdZ1wLKs8ozLKucxYxXoF6ckzEFBYBo2tw3CWuxF3ZKHIUECiUoDDIZ5FRBOnuInpyAAiHdWr1OxVzOOue0MPMcymj2e2eu0/A4uNsTQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5ed8ba2da9f2b19904520527a97e18cd')


#貨幣代號
coins={"USD":"美元","HKD":"港幣","MYR":"馬來西亞林吉特","BEF":"比利時法郎","CAD":"加幣","FRF":"法國法郎","ITL":"義大利里拉","PHP":"菲律賓比索","DEM":"德國馬克","JPY":"日圓","CHF":"瑞士法郎","SEK":"瑞典克郎","TWD":"新台幣","AUD":"澳幣","NZD":"紐西蘭幣","SGD":"新加坡幣","ESP":"西班牙比塞塔","DKK":"丹麥克郎","INR":"印度盧比","NOK":"挪威克郎","NLG":"荷蘭盾","FIM":"芬蘭馬克","SAR":"沙烏地里亞爾","THB":"泰銖","IDR":"印尼盧比","ZAR":"蘭特","ATS":"先令","GBP":"英鎊","IEP":"愛爾蘭鎊","EUR":"歐元","MOP":"澳門幣","MXN":"墨西哥比索","PLN":"茲羅提","CZK":"捷克克郎","TRY":"新土耳其里拉","HUF":"富林特","VND":"越南盾","CNY":"人民幣"}



#獲取預報方法  loc為地名   time為時段 1代表現在 2代表24小時候 3代表36小時候
def getweather(loc,time):
    url="https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON"
    r = requests.get(url,verify=False)
    j=r.json()
    datalist=j["cwbopendata"]["dataset"]["location"]
    for i in datalist:
        if loc in i["locationName"]:
            result=""  #初始化

            if time == 1:
                first=i["locationName"]+" - 目前天氣\n"
            elif time == 2:
                first=i["locationName"]+" - 24小時天氣預報\n"
            else:
                first=i["locationName"]+" - 36小時天氣預報\n"
            for x in i["weatherElement"]:

                count=0  #計數每跑完一次'elementName'初始化
                
                for a in x["time"]:
                    count+=1
                    #指定時段預報  count 為計數 判斷運行到第幾時段的資料 
                    if count==time:

                        if x["elementName"] == "Wx":
                            result+=("天氣狀態: "+a["parameter"]["parameterName"]+"\n")
                        elif x["elementName"] == "MaxT":
                            max1=a["parameter"]["parameterName"]
                        elif x["elementName"] == "MinT":
                            min1=a["parameter"]["parameterName"]
                        elif x["elementName"] == "CI":
                            result+=("舒適度: "+a["parameter"]["parameterName"]+"\n")
                        elif x["elementName"] == "PoP":
                            result+=("降雨機率: %s %%"% a["parameter"]["parameterName"]+"\n")
            
            result+=( "氣溫: "+min1+"~"+max1+"度")      
            return first + result
            
    return "請輸入台灣的縣市!"




@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'




@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):


#幣值轉換
    input_text = event.message.text
    if "天氣" in input_text:
        input_text=input_text.replace("天氣","")
        input_text=input_text.replace(" ","")
        if "台" in input_text:
            input_text=input_text=input_text.replace("台","臺")
        if "現在" in input_text:
            time=1
            input_text=input_text.replace("現在","")
        elif "明天" in input_text:
            time=2
            input_text=input_text.replace("明天","")
        elif "後天" in input_text:
            time=3
            input_text=input_text.replace("後天","")
        else:
            time=1
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=getweather(input_text,time)))
    if "$" in input_text:
        if "list" in input_text:
            result=""
            for a in coins:
                x=coins[a]
                result+=a+" "+x+" \n"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result))

        else:

            r=requests.get('https://tw.rter.info/capi.php')
            currency=r.json()

            var = input_text.split(" ", 3)
            cost=eval(var[1])
            
            FROM =var[2].upper()
            TO =var[3].upper()
            if "USD"+FROM in currency and "USD"+TO in currency:
                aaa=currency["USD"+FROM]['Exrate']
                bbb=currency["USD"+TO]['Exrate']
                result="%d %s 等於 %.2f %s"%(cost,coins[FROM],(cost/aaa * bbb),coins[TO])
            else:
                result="參數錯誤 用法 $ [cost] [coin1] [coin2]"
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result))

                
            
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8090)
