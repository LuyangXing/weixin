# Create your views here.
# coding=utf-8
from django.http import HttpResponse
import hashlib
import time
import datetime
from xml.etree import ElementTree as ET

from weixin.autore.models import MsgList
from weixin.autore.models import KeywordsList


def handle_request(request):
    if request.method == 'GET':
        response = HttpResponse(check_signature(request), content_type="text/plain")
        return response
    elif request.method == 'POST':
        response = HttpResponse(response_msg(request), content_type="application/xml")
        return response
    else:
        return HttpResponse("Invalid Request")


def check_signature(request):
    token = "wxtoken20130515"
    params = request.GET
    args = [token, params['timestamp'], params['nonce']]
    args.sort()
    if hashlib.sha1("".join(args)).hexdigest() == params['signature']:
        if params.has_key('echostr'):
            return HttpResponse(params['echostr'])
    else:
        return HttpResponse("Invalid Request")


def response_msg(request):
    if request.raw_post_data:
        xml = ET.fromstring(request.raw_post_data)
        fromUserName = xml.find("ToUserName").text
        toUserName = xml.find("FromUserName").text
        msgtype = xml.find("MsgType").text
        postTime = str(int(time.time()))

        reply_text = """<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[%s]]></MsgType>
                        <Content><![CDATA[%s]]></Content>
                        <FuncFlag>0</FuncFlag>
                    </xml>"""

        reply_news = """<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[%s]]></MsgType>
                        <ArticleCount>1</ArticleCount>
                        <Articles>
                            <item>
                                <Title><![CDATA[%s]]></Title>
                                <Description><![CDATA[%s]]></Description>
                                <PicUrl><![CDATA[%s]]></PicUrl>
                                <Url><![CDATA[%s]]></Url>
                            </item>
                        </Articles>
                        <FuncFlag>1</FuncFlag>
                    </xml>"""

        reply_music = """<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[%s]]></MsgType>
                        <Music>
                            <Title><![CDATA[%s]]></Title>
                            <Description><![CDATA[%s]]></Description>
                            <MusicUrl><![CDATA[%s]]></MusicUrl>
                            <HQMusicUrl><![CDATA[%s]]></HQMusicUrl>
                        </Music>
                        <FuncFlag>0</FuncFlag>
                    </xml>"""

        if msgtype == 'text':
            content = xml.find("Content").text
            data = MsgList(cToUserName=toUserName, cFromUserName=fromUserName,
                           cCreateTime=datetime.datetime.now(), cMsgType=msgtype, cContent=content)
            data.save()

            try:
                kwlobjs = KeywordsList.objects.filter(cKeywords=content)
                for kwlobj in kwlobjs:
                    if kwlobj.cMsgType == 'text':
                        return HttpResponse(reply_text % (toUserName, fromUserName, postTime, kwlobj.cMsgType,
                                                          kwlobj.cContent))
                    elif kwlobj.cMsgType == 'news':
                        return HttpResponse(reply_news % (toUserName, fromUserName, postTime, kwlobj.cMsgType,
                                                          '1', '2', 'http://www.zcool.com.cn/img.html?src=/60/15/1259734790432.jpg', 'http://xyxd.tk'))
                    elif kwlobj.cMsgType == 'music':
                        return HttpResponse(reply_music % (toUserName, fromUserName, postTime, kwlobj.cMsgType,
                                                           kwlobj.cTitle, kwlobj.cDescription, kwlobj.cMusicUrl, kwlobj.cHQMusicUrl))
                    else:
                        pass
            except KeywordsList.DoesNotExist:
                pass

        elif msgtype == 'event':
            event = xml.find("Event").text
            if event == 'subscribe':
                pass
            elif event == 'unsubscribe':
                pass
            else:
                return HttpResponse("Invalid Request")

        else:
            return HttpResponse("Invalid Request")

    else:
        return HttpResponse("Invalid Request")


# #  reference