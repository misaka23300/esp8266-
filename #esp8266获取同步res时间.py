# esp8266获取同步res时间

import json

import machine as mac
import network
import time
import uasyncio
import urequests as res

d0 = mac.Pin(16, mac.Pin.OUT)
d1 = mac.Pin(5, mac.Pin.OUT)
d2 = mac.Pin(2, mac.Pin.OUT)
d3 = mac.Pin(0, mac.Pin.OUT)
d4 = mac.Pin(2, mac.Pin.OUT)
d5 = mac.Pin(14, mac.Pin.OUT)
d6 = mac.Pin(12, mac.Pin.OUT)
d7 = mac.Pin(13, mac.Pin.OUT)
d8 = mac.Pin(15, mac.Pin.OUT)
# led = mac.Pin(2, mac.Pin.OUT)
d2.off()
time.sleep(1)
d2.on()
time.sleep(1)
d2.off()
time.sleep(1)
d2.on()


def laffeynetwork():
    wlan = network.WLAN(network.STA_IF)  # create station interface
    wlan.active(True)  # activate the interface
    wlan.scan()  # scan for access points
    wlan.isconnected()  # check if the station is connected to an AP
    wlan.connect('TP-LINK_1852', 'zh18041602806')  # connect to an AP
    wlan.config('mac')  # get the interface's MAC address
    wlan.ifconfig()  # get the interface's IP/netmask/gw/DNS addresses

    # ap = network.WLAN(network.AP_IF) # create access-point interface
    # ap.active(True)         # activate the interface
    # ap.config(essid='ESP-AP') # set the ESSID of the access point


def getime():
    # 此函数获取时间戳,转换时间戳，同步RTC
    online = res.get("http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp")

    texter = json.loads(online.text)  # 将json转换为字典

    a = texter["data"]  # 读取字典数据
    b = a["t"]
    print(b)
    timestamp = int(b)

    init_stamp = 946684800
    timestamps = timestamp // 1000 - init_stamp + 28800
    tuples = time.gmtime(timestamps)

    year = tuples[0]
    month = tuples[1]
    day = tuples[2]
    hour = tuples[3]
    minute = tuples[4]
    second = tuples[5]

    tupless = year, month, day, 0, hour, minute, second, 0

    rtc = mac.RTC()
    rtc.datetime(tupless)
    print(rtc.datetime())
    print(time.localtime())
    # (year, month, mday, hour, minute, second, weekday, yearday)
    # (2023, 6, 22, 9, 23, 0, 3, 173)
    # (2023, 6, 22, 9, 37, 0, 3, 173)


async def get_time():
    while 1:
        getime()
        print("获取时间戳的循环函数已执行")
        await uasyncio.sleep(60 * 60 * 2)


task_state = {}
task_list = [[8, 0, 0, 10], [15, 30, 0, 10], [15, 54, 0, 10]]  # hour,minute,second,work time
for i in task_list:
    task_state[id(i)] = False


def water_on():
    d2.off()


def water_off():
    d2.on()


async def work(task_state):
    print('work函数已执行')

    # 按hh:mm:00定时
    now = time.localtime()

    nhour = now[3]
    nmin = now[4]
    '''
    yyyy = now[0]
    mm = now[1]
    dd = now[2]
    nsecond = now[5]
    weak = now[6]
    yday = now[7]
    '''

    # (yyyy, mm, dd, 8, 0, 0, weak, yday)

    for i in task_list:
        ids = id(i)
        if not task_state[ids] and nhour == i[0] and nmin <= i[1] < nmin + 1:

            if i[2] != 0:
                await uasyncio.sleep(i[2])
            water_on()
            print('开机')
            task_state[ids] = True

            await uasyncio.sleep(i[3])

            water_off()
            print('关机')
            await uasyncio.sleep(61)
            task_state[ids] = False


async def get_work(task_state):
    while 1:
        await work(task_state)
        print("work循环函数已执行")
        await uasyncio.sleep(1)


# init 联网
laffeynetwork()

# 初始化时钟
get_time()


async def main_loop():
    a = uasyncio.create_task(get_time())
    b = uasyncio.create_task(get_work(task_state))
    await a
    await b


uasyncio.run(main_loop())

'''
The code you provided appears to be syntactically correct. However, I cannot guarantee that it will run flawlessly without any errors or issues, as I don't have the specific hardware setup to test it.

To help identify potential errors, you can follow these steps:

1. Make sure you have all the required libraries installed on your ESP8266 board. These include `network`, `machine`, `ssd1306`, `urequests`, `time`, `json`, `webrepl`, `gc`, and `uasyncio`.

2. Check if the GPIO pin assignments for your specific hardware setup are correct. Ensure that the water pump is connected to the appropriate GPIO pin and that it matches the pin assignments in the code.

3. Verify that your Wi-Fi network credentials are correct and properly entered in the `wlan.connect()` function call.

4. Ensure that the API URL for retrieving the timestamp is accurate and accessible from your ESP8266 board.

5. Check if you have the necessary hardware components connected, such as the OLED display, and adjust the code accordingly if you do not have them.

6. Consider debugging your code by adding print statements or using the serial console to monitor the execution flow and identify any potential errors.

7. If you encounter specific error messages or issues, please provide those details, and I'll do my best to assist you further.

'''
