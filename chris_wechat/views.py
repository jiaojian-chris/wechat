# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage
import json


W_TOKEN = "chrisjiao"
AppID = "wx3caa80ff176f212e"
AppSecret = "e8281f1a5f854b560aed83e896c649a6"

wechat_instance = WechatBasic(
    token=W_TOKEN,
    appid=AppID,
    appsecret=AppSecret
)


@csrf_exempt
def index(request):
    if request.method == "GET":
        signature = request.GET.get("signature")
        timestamp = request.GET.get("timestamp")
        nonce = request.GET.get("nonce")

        if not wechat_instance.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest("Verify Faild")

        return HttpResponse(request.GET.get('echostr', ''), content_type="text/plain")

    try:
        wechat_instance.parse_data(data=request.body)
    except ParseError:
        return HttpResponseBadRequest("Invalid XML Data")

    message = wechat_instance.get_message()

    response = wechat_instance.response_text(
        content=(
            '感谢您的关注！\n回复【功能】两个字查看支持的功能，还可以回复任意内容开始聊天'
            ))
    if isinstance(message, TextMessage):
        # 当前会话内容
        content = message.content.strip()
        print content
        if content == '功能':
            reply_text = (
                '回复任意词语，查天气，陪聊天，讲故事，无所不能！\n'
                '还有更多功能正在开发中哦 ^_^\n'
            )
        elif content.endswith('天气'):
            city = content[:-2]
            response = requests.get('http://wthrcdn.etouch.cn/weather_mini?city=' + city)
            data = json.loads(response.content)

            reply_text = (
                data['data']['forecast'][0]['high'] + '\n' +
                data['data']['forecast'][0]['high'] + '\n' +
                data['data']['forecast'][0]['type']
            )

        response = wechat_instance.response_text(content=reply_text)

    return HttpResponse(response, content_type="application/xml")

