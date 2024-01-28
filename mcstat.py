from mcstatus import JavaServer
from typing import Tuple
import asyncio
import json
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import matplotlib.pyplot as plt

async def get_server_data(name: str, address: str) -> Tuple[dict,bool]:   
    try:
        server = await JavaServer.async_lookup(address,timeout=10)
        status = server.status()
    except:
        dict = {"name":name, 
        "address":address, 
        "icon":None, 
        "description":None,
        "ping":None,
        "version":None,
        "players":None,
        "online/max":None
        }
        return dict, False
    # 服务器图标
    icon = status.favicon
    # 服务器描述
    description = status.description
    # 服务器延迟
    ping = int(status.latency)
    # 服务器版本
    version = status.version.name
    # 服务器人数上限
    max = status.players.max
    # 服务器在线人数
    online = status.players.online
    # 在线玩家列表
    online_players = status.players.sample

    dict = {"name":name, 
            "address":address, 
            "icon":icon, 
            "description":description,
            "ping":ping,
            "version":version,
            "players":online_players,
            "online":online,
            "max":max
            }
    return dict

def process():
    t=time.localtime()
    server_list=None
    server_stat_list=None
    with open("config.json","r",encoding="utf-8") as _f:
        server_list=json.loads(_f.read())
    try:
        with open("status.json","r",encoding="utf-8") as _f:
            server_stat_list=json.loads(_f.read())
    except:
        server_stat_list={}
    print("Server List:",server_list)
    if server_list.keys()!=server_stat_list.keys():
        server_stat_list={}
        for _key in server_list.keys():
            server_stat_list[_key]=[]
    for _key in server_list.keys():
        result=asyncio.run(get_server_data(_key,server_list[_key]))
        if(len(server_stat_list[_key])>48):
            server_stat_list[_key].pop(0)
        server_stat_list[_key].append([result["online"],f"{t.tm_hour}:{t.tm_min}"])
    
    print(server_stat_list)

    plt.figure()
    plt.rcParams["font.sans-serif"]=["SimHei"]
    for _key in server_stat_list.keys():
        print([i[1] for i in server_stat_list[_key]] )
        plt.plot([i[1] for i in server_stat_list[_key]],[i[0] for i in server_stat_list[_key]],label=_key,alpha=0.5)
    plt.legend()
    plt.xlabel("Time")
    plt.ylabel("Player Number")
    plt.savefig("plot.png")

    with open("status.json","w",encoding="utf-8") as _f:
        _f.write(json.dumps(server_stat_list))


if __name__ == '__main__':
    process()

    scheduler=BlockingScheduler()
    scheduler.add_job(process,"cron",minite="0,10,20,30,40,50")
    scheduler.start()