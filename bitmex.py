import hashlib
import json
import time
import websockets
import asyncio
import hmac
import bitmex
import urllib.parse



api_testKey = ""
api_testSecret = ""

api_key = ""
api_secret = ""
#bitmex에서 api키를 발급 받아 입력 api키만 받아도 구독 가능

def restAPI():
    client = bitmex.bitmex(test=True, api_key=api_testKey, api_secret=api_testSecret)
    result = client.Quote.Quote_get(symbol='XBTUSD', reverse=True, count=10).result()

    return result


async def bitmex_ws_client():
    uri = "wss://www.bitmex.com/realtime"
    uri = "wss://testnet.bitmex.com/realtime"


    ENDPOINT = "/realtime"

    expires = int(round(time.time()) + 10)
    signature = bitmex_signature(api_secret, "GET", ENDPOINT, expires)




    async with websockets.connect(uri, ping_interval=None) as websocket:

        await websocket.send(json.dumps("help"))

        args = {"op": "subscribe", "args": "tradeBin5m:XBTUSD"}
        await websocket.send(json.dumps(args))  # json 모듈을 사용해서 파이썬 딕셔너리를 JSON 타입으로 변환합니다.

        args = {"op": "subscribe", "args": "tradeBin1m:XBTUSD"}
        await websocket.send(json.dumps(args)) # json 모듈을 사용해서 파이썬 딕셔너리를 JSON 타입으로 변환합니다.

        # args = {"op": "subscribe", "args": "trade:XBTUSD"}
        # await websocket.send(json.dumps(args))

        args = {"op": "authKeyExpires", "args": [api_key, expires, signature]}
        signature = bitmex_signature(api_testSecret, "GET", ENDPOINT, expires)
        args = {"op": "authKeyExpires", "args": [api_testKey, expires, signature]}
        await websocket.send(json.dumps(args))

        args = {"op": "subscribe", "args": "execution:XBTUSD"}
        await websocket.send(json.dumps(args))

        args = {"op": "cancelAllAfter", "args": 60000}
        await websocket.send(json.dumps(args))

        minute30m = []
        minute5 = {}
        minute1 = {}
        tradeUSD ={}

        # print(restAPI())

        while True:
                data = await websocket.recv()
                data = json.loads(data) # 전달받은 JSON 타입의 데이터를 파이썬 딕셔너리 타입으로 변환합니다.
                # print(data)

                if "tradeBin5m" in data.values():
                    minute = "5분봉"
                    # print(minute, "고가", data["data"][0]["high"])
                    # print(minute, "저가", data["data"][0]["low"])
                    # print(minute, "종가", data["data"][0]["close"])
                    minute5 = {"data": minute, "시간": data["data"][0]["timestamp"], "고가": data["data"][0]["high"],
                               "저가": data["data"][0]["low"], "종가": data["data"][0]["close"]}
                    print(minute5)

                elif "tradeBin1m" in data.values():
                    minute = "1분봉"
                    # print(minute, "고가", data["data"][0]["high"])
                    # print(minute, "저가", data["data"][0]["low"])
                    # print(minute, "종가", data["data"][0]["close"])
                    minute1 = {"data": minute, "시간": data["data"][0]["timestamp"], "고가": data["data"][0]["high"],
                               "저가": data["data"][0]["low"], "종가": data["data"][0]["close"]}
                    print(minute1)

                elif "trade" in data.values():
                    # print(data["data"][0]["side"], data["data"][0]["price"], data["data"][0]["size"])
                    tradeUSD = {"data": "현재가", "시간": data["data"][0]["timestamp"], "상태": data["data"][0]["side"],
                                "가격": data["data"][0]["price"], "크기": data["data"][0]["size"]}
                    print(tradeUSD)
                    if minute5:
                        if tradeUSD["가격"]>minute5["종가"]:
                            print("종가대비", (tradeUSD["가격"]-minute5["종가"])/minute5["종가"]*100, "% 상승",
                                  tradeUSD["가격"]-minute5["종가"], "달러", "현재가", tradeUSD["가격"])
                        elif tradeUSD["가격"]<minute5["종가"]:
                            print("종가대비", (minute5["종가"]-tradeUSD["가격"])/minute5["종가"]*100, "% 하락",
                                  tradeUSD["가격"]-minute5["종가"], "달러", "현재가", tradeUSD["가격"])
                        else:
                            print("횡보중")


def bitmex_signature(apiSecret, verb, url, nonce, postdict=None): #bitmex 홈페이지 signature 생성 예문
    """Given an API Secret key and data, create a BitMEX-compatible signature."""
    data = ''
    if postdict:
        # separators remove spaces from json
        # BitMEX expects signatures from JSON built without spaces
        data = json.dumps(postdict, separators=(',', ':'))
    parsedURL = urllib.parse.urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query
    # print("Computing HMAC: %s" % verb + path + str(nonce) + data)
    message = (verb + path + str(nonce) + data).encode('utf-8')
    print("Signing: %s" % str(message))

    signature = hmac.new(apiSecret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()
    print("Signature: %s" % signature)
    return signature


async def main():
    await bitmex_ws_client()


asyncio.run(main())
