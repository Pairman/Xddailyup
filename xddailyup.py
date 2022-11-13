'''
# 西安电子科技大学晨午晚检自动上报工具

# 作者

[Pairman](https://github.com/Pairman)

# 免责信息

本程序仅供学习交流使用，使用本程序造成的任何后果由用户自行负责。

# 依赖

```Python>=3``` , ```requests```

# 用法

```
用法：
    python3 xddailyup.py [参数]
参数：
    -h,--help                   输出帮助信息
    -u,--username <学号>        指定学号
    -p,--password <密码>        指定密码
    -l,--location <上报地址>    指定上报地址（格式：某国某省某市某县/区）
    -d,--debug                  进入调试模式
```

# 致谢

[使用Github Action自动填写疫情通](https://cnblogs.com/soowin/p/13461451.html)

[西安电子科技大学疫情通、晨午晚检自动上报工具](https://github.com/jiang-du/Auto-dailyup)

[西安电子科技大学(包含广州研究院)晨午晚检自动上报工具](https://github.com/HANYIIK/Auto-dailyup)

[西安电子科技大学晨午晚检自动上报工具](https://github.com/cunzao/ncov)

# 开源协议

GNU General Public License v3.0 (gpl-3.0)
'''

from datetime import datetime
from getopt import getopt
from random import randint
from requests import Session
from sys import argv
from time import sleep

opts=getopt(argv[1:],"hu:p:l:d",["help","username=","password=","location=","debug"])[0]

USERNAME,PASSWORD,LOCATION,DEBUG="","",1,False

helpMsg="""Xddailyup - 西安电子科技大学晨午晚检自动上报工具 3.1 (2022 Nov 13, Pairman)
本程序仅供学习交流使用，使用本程序造成的任何后果由用户自行负责。
用法：
    python3 %s [参数]
参数：
    -h,--help                   输出帮助信息
    -u,--username <学号>        指定学号
    -p,--password <密码>        指定密码
    -l,--location <上报地址>    指定上报地址（0：北校区，1：南校区，2：广州研究院 (测试)，3：杭州研究院 (预留)，4：备用(出差)，默认为1）
    -d,--debug                  进入调试模式
"""%(argv[0])

if len(argv)==1:
    print(helpMsg)
    exit()

for opt,arg in opts:
    if opt in ("-h","--help"):
        print(helpMsg)
        exit()
    if opt in ("-u","--username"):
        USERNAME=arg
    if opt in ("-p","--password"):
        PASSWORD=arg
    if opt in ("-l","--location"):
        LOCATION=arg
    if opt in ("-d","--debug"):
        DEBUG=1

print("本程序仅供学习交流使用，使用本程序造成的任何后果由用户自行负责。")

if USERNAME=="":
    print("请指定学号！")
    exit()
if PASSWORD=="":
    print("请指定密码！")
    exit()

# 上报信息表

# 0 - 北校区
NORTH_UPLOAD_MSG={
    "sfzx":"1", # 是否在校(0->否，1->是)
    "tw":"0", # 体温 (36℃->0，36℃到36.5℃->1，36.5℃到36.9℃->2，36.9℃到37℃.3->3，37.3℃到38℃->4，38℃到38.5℃->5,
    # 38.5℃到39℃->6，39℃到40℃->7，40℃以上->8)
    "sfcyglq":"0", # 是否处于隔离期? (0->否，1->是)
    "sfyzz":"0", # 是否出现乏力、干咳、呼吸困难等症状？ (0->否，1->是)
    "qtqk":"", # 其他情况 (文本)
    "askforleave":"0", # 是否请假外出? (0->否，1->是)
    "geo_api_info":"{\"type\":\"complete\",\"info\":\"SUCCESS\",\"status\":1,\"VDa\":\"jsonp_324977_\","
                    "\"position\":{\"Q\":34.23254,\"R\":108.91516000000001,\"lng\":108.91802,\"lat\":34.23231},"
                    "\"message\":\"Get ipLocation success.Get address success.\",\"location_type\":\"ip\","
                    "\"accuracy\":None,\"isConverted\":true,\"addressComponent\":{\"citycode\":\"029\","
                    "\"adcode\":\"610113\",\"businessAreas\":[],\"neighborhoodType\":\"\",\"neighborhood\":\"\","
                    "\"building\":\"\",\"buildingType\":\"\",\"street\":\"白沙路\",\"streetNumber\":\"238号\","
                    "\"country\":\"中国\",\"province\":\"陕西省\",\"city\":\"西安市\",\"district\":\"雁塔区\","
                    "\"township\":\"电子城街道\"},\"formattedAddress\":\"陕西省西安市雁塔区电子城街道西安电子科技大学北校区\",\"roads\":[],"
                    "\"crosses\":[],\"pois\":[],\"info\":\"SUCCESS\"}",
    "area":"陕西省 西安市 雁塔区", # 地区
    "city":"西安市", # 城市
    "province":"陕西省", # 省份
    "address":"陕西省西安市雁塔区电子城街道西安电子科技大学北校区"  # 实际地址
}

# 1 - 南校区
SOUTH_UPLOAD_MSG={
    "sfzx":"1", # 是否在校(0->否，1->是)
    "tw":"0",
    # 体温 (36℃->0，36℃到36.5℃->1，36.5℃到36.9℃->2，36.9℃到37℃.3->3，37.3℃到38℃->4，38℃到38.5℃->5，38.5℃到39℃->6，39℃到40℃->7,
    # 40℃以上->8)
    "sfcyglq":"0", # 是否处于隔离期? (0->否，1->是)
    "sfyzz":"0", # 是否出现乏力、干咳、呼吸困难等症状？ (0->否，1->是)
    "qtqk":"", # 其他情况 (文本)
    "askforleave":"0", # 是否请假外出? (0->否，1->是)
    "geo_api_info":"{\"type\":\"complete\",\"position\":{\"Q\":34.121994628907,\"R\":108.83715983073,"
                    "\"lng\":108.83716,\"lat\":34.121995},\"location_type\":\"html5\",\"message\":\"Get ipLocation "
                    "failed.Get geolocation success.Convert Success.Get address success.\",\"accuracy\":65,"
                    "\"isConverted\":true,\"status\":1,\"addressComponent\":{\"citycode\":\"029\","
                    "\"adcode\":\"610116\",\"businessAreas\":[],\"neighborhoodType\":\"\",\"neighborhood\":\"\","
                    "\"building\":\"\",\"buildingType\":\"\",\"street\":\"雷甘路\",\"streetNumber\":\"264号\","
                    "\"country\":\"中国\",\"province\":\"陕西省\",\"city\":\"西安市\",\"district\":\"长安区\","
                    "\"township\":\"兴隆街道\"},\"formattedAddress\":\"陕西省西安市长安区兴隆街道西安电子科技大学长安校区办公辅楼\",\"roads\":[],"
                    "\"crosses\":[],\"pois\":[],\"info\":\"SUCCESS\"}",
    "area":"陕西省 西安市 长安区", # 地区
    "city":"西安市", # 城市
    "province":"陕西省", # 省份
    "address":"陕西省西安市长安区兴隆街道西安电子科技大学长安校区行政辅楼" # 实际地址
}

# 2 - 广州研究院 (测试)
GZ_UPLOAD_MSG={
    "sfzx":"1", # 是否在校(0->否，1->是)
    "tw":"0",
    # 体温 (36℃->0，36℃到36.5℃->1，36.5℃到36.9℃->2，36.9℃到37℃.3->3，37.3℃到38℃->4，38℃到38.5℃->5，38.5℃到39℃->6，39℃到40℃->7,
    # 40℃以上->8)
    "sfcyglq":"0", # 是否处于隔离期? (0->否，1->是)
    "sfyzz":"0", # 是否出现乏力、干咳、呼吸困难等症状？ (0->否，1->是)
    "qtqk":"", # 其他情况 (文本)
    "askforleave":"0", # 是否请假外出? (0->否，1->是)
    "geo_api_info":"{\"type\":\"complete\",\"position\":{\"Q\":23.327658,\"R\":113.54548,"
                    "\"lng\":113.54548,\"lat\":23.327658},\"location_type\":\"html5\",\"message\":\"Get ipLocation "
                    "failed.Get geolocation success.Convert Success.Get address success.\",\"accuracy\":65,"
                    "\"isConverted\":true,\"status\":1,\"addressComponent\":{\"citycode\":\"020\","
                    "\"adcode\":\"510555\",\"businessAreas\":[],\"neighborhoodType\":\"\",\"neighborhood\":\"\","
                    "\"building\":\"\",\"buildingType\":\"\",\"street\":\"九龙大道\",\"streetNumber\":\"海丝知识中心\","
                    "\"country\":\"中国\",\"province\":\"广东省\",\"city\":\"广州市\",\"district\":\"黄埔区\","
                    "\"township\":\"九龙街道\"},\"formattedAddress\":\"广东省广州市黄埔区九龙大道海丝知识中心\",\"roads\":[],"
                    "\"crosses\":[],\"pois\":[],\"info\":\"SUCCESS\"}",
    "area":"广东省 广州市 黄埔区", # 地区
    "city":"广州市", # 城市
    "province":"广东省", # 省份
    "address":"广东省广州市黄埔区九龙大道海丝知识中心" # 实际地址
}

# 3 - 杭州研究院 (预留)
HZ_UPLOAD_MSG={
    "sfzx":"1", # 是否在校(0->否，1->是)
    "tw":"0",
    # 体温 (36℃->0，36℃到36.5℃->1，36.5℃到36.9℃->2，36.9℃到37℃.3->3，37.3℃到38℃->4，38℃到38.5℃->5，38.5℃到39℃->6，39℃到40℃->7,
    # 40℃以上->8)
    "sfcyglq":"0", # 是否处于隔离期? (0->否，1->是)
    "sfyzz":"0", # 是否出现乏力、干咳、呼吸困难等症状？ (0->否，1->是)
    "qtqk":"", # 其他情况 (文本)
    "askforleave":"0", # 是否请假外出? (0->否，1->是)
    "geo_api_info":"{\"type\":\"complete\",\"position\":{\"Q\":30.261994621906,\"R\":120.19715981072,"
                    "\"lng\":120.19715,\"lat\":30.26199},\"location_type\":\"html5\",\"message\":\"Get ipLocation "
                    "failed.Get geolocation success.Convert Success.Get address success.\",\"accuracy\":65,"
                    "\"isConverted\":true,\"status\":1,\"addressComponent\":{\"citycode\":\"0571\","
                    "\"adcode\":\"310000\",\"businessAreas\":[],\"neighborhoodType\":\"\",\"neighborhood\":\"\","
                    "\"building\":\"\",\"buildingType\":\"\",\"street\":\"龙井路\",\"streetNumber\":\"1号\","
                    "\"country\":\"中国\",\"province\":\"浙江省\",\"city\":\"杭州市\",\"district\":\"西湖区\","
                    "\"township\":\"西湖街道\"},\"formattedAddress\":\"浙江省杭州市西湖区西湖街道龙井路1号杭州西湖风景名胜区\",\"roads\":[],"
                    "\"crosses\":[],\"pois\":[],\"info\":\"SUCCESS\"}",
    "area":"浙江省 杭州市 西湖区", # 地区
    "city":"杭州市", # 城市
    "province":"浙江省", # 省份
    "address":"浙江省杭州市西湖区西湖街道龙井路1号杭州西湖风景名胜区" # 实际地址
}

# 4 - 备用(出差)
BAK_UPLOAD_MSG={
    "sfzx":"1", # 是否在校(0->否，1->是)
    "tw":"0",
    # 体温 (36℃->0，36℃到36.5℃->1，36.5℃到36.9℃->2，36.9℃到37℃.3->3，37.3℃到38℃->4，38℃到38.5℃->5，38.5℃到39℃->6，39℃到40℃->7,
    # 40℃以上->8)
    "sfcyglq":"0", # 是否处于隔离期? (0->否，1->是)
    "sfyzz":"0", # 是否出现乏力、干咳、呼吸困难等症状？ (0->否，1->是)
    "qtqk":"", # 其他情况 (文本)
    "askforleave":"0", # 是否请假外出? (0->否，1->是)
    "geo_api_info":"{\"type\":\"complete\",\"position\":{\"Q\":31.142927,\"R\":121.81332,"
                    "\"lng\":121.81332,\"lat\":31.142927},\"location_type\":\"html5\",\"message\":\"Get ipLocation "
                    "failed.Get geolocation success.Convert Success.Get address success.\",\"accuracy\":65,"
                    "\"isConverted\":true,\"status\":1,\"addressComponent\":{\"citycode\":\"021\","
                    "\"adcode\":\"200120\",\"businessAreas\":[],\"neighborhoodType\":\"\",\"neighborhood\":\"\","
                    "\"building\":\"\",\"buildingType\":\"\",\"street\":\"迎宾大道\",\"streetNumber\":\"6000号\","
                    "\"country\":\"中国\",\"province\":\"上海市\",\"city\":\"上海市\",\"district\":\"浦东新区\","
                    "\"township\":\"祝桥镇\"},\"formattedAddress\":\"上海市浦东新区祝桥镇迎宾大道6000号浦东国际机场T2航站楼\",\"roads\":[],"
                    "\"crosses\":[],\"pois\":[],\"info\":\"SUCCESS\"}",
    "area":"上海市 浦东新区", # 地区
    "city":"上海市", # 城市
    "province":"上海市", # 省份
    "address":"上海市浦东新区祝桥镇迎宾大道6000号浦东国际机场T2航站楼" # 实际地址
}

# 上报哪个信息
uploadMsgs=(NORTH_UPLOAD_MSG,SOUTH_UPLOAD_MSG,GZ_UPLOAD_MSG,HZ_UPLOAD_MSG,BAK_UPLOAD_MSG)
currentUploadMsg=uploadMsgs[LOCATION]

# 定义程序上报的时间，初始值为 8:30，12:30，18:30
timeLib=[8,30,12,30,18,30]

# 登录
conn=Session()
logined=False
for i in range(3):
    result=None
    try :
        result=conn.post(url="https://xxcapp.xidian.edu.cn/uc/wap/login/check",data={"username":USERNAME,"password":PASSWORD},verify=not DEBUG)
        if result.json()['e']==0:
            logined=True
            print("登录成功")
            break
        print("登录失败：",result.json()['m'])
    except:
        print("登录失败：异常")
    sleep(60)
if not logined:
    print("登录失败，正在退出")
    exit()

# 上报晨午晚检
def dailyUp():
    result=None
    for i in range(3):
        try:
            result=conn.post(url="https://xxcapp.xidian.edu.cn/xisuncov/wap/open-report/save",data=currentUploadMsg,verify=not DEBUG)
            if result.json()['e']==0:
                print("上报成功")
                sleep(60)
                return 1
            elif result.json()['m']=="您已上报过":
                print("已上报过")
                sleep(60)
                return 2
            print("填报失败")
        except:
            pass
            sleep(60)
    print("连续三次填报失败")
    return 0

# 运行后立即尝试上报
dailyUp()

while True:
    currentTime=datetime.now()
    currentHour,currentMinute=int(str(currentTime)[11:13]),int(str(currentTime)[14:16])
    # 晨午晚检上报
    if (currentHour,currentMinute)==(timeLib[0],timeLib[1]):
        print("今天是%s年%s月%s日"%(str(currentTime)[0:4],str(currentTime)[5:7],str(currentTime)[8:10]))
        dailyUp()
        sleep(-60+3600*timeLib[2]+60*timeLib[3]-3600*timeLib[0]-60*timeLib[1])
    elif (currentHour,currentMinute)==(timeLib[2],timeLib[3]):
        dailyUp()
        sleep(-60+3600*timeLib[4]+60*timeLib[5]-3600*timeLib[2]-60*timeLib[3])
    elif (currentHour,currentMinute)==(timeLib[4],timeLib[5]):
        dailyUp()
        prviousTimeLib=timeLib
        timeLib[1],timeLib[3],timeLib[5]=randint(10,50),randint(10,50),randint(10,50)
        print("更新晨午晚检上报时间成功！下一天上报的时间为:%02d时%02d分、%02d时%02d分、%02d时%02d分"%tuple(timeLib))
        sleep(86340+3600*timeLib[0]+60*timeLib[1]-3600*currentHour-60*currentMinute)
    else:
        sleep(55)