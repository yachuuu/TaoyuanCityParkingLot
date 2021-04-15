#!/usr/bin/env python
# -*- coding=utf-8 -*-
__author__ = "YA-CHU, CHEN"

"""
路外停車資訊
桃園市交通局轄區內有與市府通訊連線之停車場發布即時剩餘車位數，資料每分鐘更新
https://data.gov.tw/dataset/25940
資料下載網址:
https://data.tycg.gov.tw/opendata/datalist/datasetMeta/download?id=f4cc0b12-86ac-40f9-8745-885bddc18f79&rid=0daad6e6-0632-44f5-bd25-5e1de1e9146f
"""

import json
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties  # 步驟一
try:                            # 步驟1：導入Tkinter 模組
    import Tkinter as tk        # 在Python 2.x 匯入該Tkinter 函式庫
    import tkMessageBox         # Python 2.x 呼叫tkMessageBox 函式庫
    import urllib2 as httplib   # 2.x
except:
    import tkinter as tk                       # 在Python 3.x 匯入該tkinter 函式庫(pycharm預安裝好的package,只需要 import即可使用)
    import tkinter.messagebox as tkMessageBox  # Python 3.x 呼叫tkMessageBox 函式庫
    import urllib.request as httplib  # 3.x
#from tkinter import StringVar  # 也可以不用寫, 但下面用到 StringVar 的都要在前面加 tk. ;StringVar->module
from PIL import ImageTk, Image  # 匯入Pillow 影像函式庫 Pillow->package;ImageTk->module
from tkinter import ttk         # 匯入 ttk= Themed Tkinter -> module  主題化版本
import tkinter.font as tkFont   # 匯入字體 module
from tkinter import Canvas, Scrollbar, Frame, Listbox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv, sys, ssl

plt.rcParams['font.sans-serif'] = ['SimSun'] # 步驟一（替換sans-serif字型）
plt.rcParams['axes.unicode_minus'] = False  # 步驟二（解決座標軸負數的負號顯示問題）

print('Version 3')

# 找有空位的停車場
def find_surplusSpace():
    surplusWindow = tk.Toplevel(win)  # 開新視窗 surplusWindow
    surplusWindow.wm_title("仍有剩餘車位的停車場查詢")  # 設定新視窗標題
    surplusWindow.minsize(width=700, height=400)  # 調整新視窗大小
    surplusWindow.resizable(width=False, height=False)  # 禁止調整視窗大小

    surplus_result_list = []
    for i in data['parkingLots']:
        if int(i['surplusSpace']) > 0:
            if int(i['surplusSpace']) < 0 or int(i['totalSpace']) <= 0 or int(i['surplusSpace']) > int(i['totalSpace']):
                del i
            else:
                surplus_result_list.append((i['areaName'], i['surplusSpace'], i['parkName'],
                                         i['address'], i['payGuide'], int(i['totalSpace'])))

    frame = Frame(surplusWindow)
    frame.place(x=0, y=0, width=700, height=400)

    # 滚动条初始化（scrollBar为垂直滚动条，scrollBarx为水平滚动条）
    scrollBar = ttk.Scrollbar(frame)
    scrollBarx = ttk.Scrollbar(frame, orient='horizontal')
    # 靠右，充满Y轴
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
    # 靠下，充满X轴
    scrollBarx.pack(side=tk.BOTTOM, fill=tk.X)

    # 页面内显示表格
    # height 表示要显示几行数据（这个部件的宽度是根据列的多少以及每列的设置宽度一同定义的）
    tree = ttk.Treeview(frame, height=31,
                        columns=Parking_Lot_header,
                        show="headings",
                        yscrollcommand=scrollBar.set,
                        xscrollcommand=scrollBarx.set)
    # side=LEFT表示表格位于窗口左端，
    # fill=BOTH表示当窗口改变大小时会在X与Y方向填满窗口
    tree.pack(side=tk.LEFT, fill=tk.BOTH)
    # 而当用户操纵滚动条的时候，自动调用 Treeview 组件的 yview()与xview() 方法
    # 即滚动条与页面内容的位置同步
    scrollBar.config(command=tree.yview)
    scrollBarx.config(command=tree.xview)

    x = 0
    for col in Parking_Lot_header:
        if x == 1 or x == 5:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby_num(tree, c, 0))
            tree.column(col, width=tkFont.Font().measure(col.title()))
        else:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby(tree, c, 0))
            # adjust the column's width to the header string
            tree.column(col, width=tkFont.Font().measure(col.title()))
        x += 1

    for item in surplus_result_list:
        tree.insert('', 'end', values=item)
        # adjust column's width if necessary to fit each value
        # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
        for ix, val in enumerate(item):
            col_w = tkFont.Font().measure(val)
            if tree.column(Parking_Lot_header[ix], width=None) < col_w:
                tree.column(Parking_Lot_header[ix], width=col_w)

# 查特定行政區有哪些停車場及相關資訊
def find_Area():
    areaWindow = tk.Toplevel(win)  # 開新視窗 areaWindow
    areaWindow.wm_title("停車場所在行政區查詢")  # 設定新視窗標題
    areaWindow.minsize(width=700, height=400)  # 調整新視窗大小
    areaWindow.resizable(width=False,height=False)   # 禁止調整視窗大小

    area_result = tk.StringVar()
    area = entry_area.get()
    area_result_list = []
    for i in data['parkingLots']:
        if i['areaName'].find(area) >= 0:
            if int(i['surplusSpace']) < 0 or int(i['totalSpace']) <= 0 or int(i['surplusSpace']) >int(i['totalSpace']):
                del i
            else:
                area_result_list.append((i['areaName'],i['surplusSpace'],i['parkName'],
                                         i['address'],i['payGuide'],int(i['totalSpace'])))
    #print('\n搜尋完畢!')
    area_result.set(area_result_list)
    #print(area_result_list)

    frame = Frame(areaWindow)
    frame.place(x=0, y=0, width=700, height=400)

    # 滚动条初始化（scrollBar为垂直滚动条，scrollBarx为水平滚动条）
    scrollBar = ttk.Scrollbar(frame)
    scrollBarx = ttk.Scrollbar(frame, orient='horizontal')
    #靠右，充满Y轴
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
    # 靠下，充满X轴
    scrollBarx.pack(side=tk.BOTTOM, fill=tk.X)

    # 页面内显示表格
    # height 表示要显示几行数据（这个部件的宽度是根据列的多少以及每列的设置宽度一同定义的）
    tree = ttk.Treeview(frame, height = 31,
                    columns=Parking_Lot_header,
                    show="headings",
                    yscrollcommand=scrollBar.set,
                    xscrollcommand=scrollBarx.set)
    # side=LEFT表示表格位于窗口左端，
    # fill=BOTH表示当窗口改变大小时会在X与Y方向填满窗口
    tree.pack(side=tk.LEFT, fill=tk.BOTH)
    # 而当用户操纵滚动条的时候，自动调用 Treeview 组件的 yview()与xview() 方法
    # 即滚动条与页面内容的位置同步
    scrollBar.config(command=tree.yview)
    scrollBarx.config(command=tree.xview)

    x = 0
    for col in Parking_Lot_header:
        if x == 1 or x == 5:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby_num(tree, c, 0))
            tree.column(col, width=tkFont.Font().measure(col.title()))
        else:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby(tree, c, 0))
            # adjust the column's width to the header string
            tree.column(col, width=tkFont.Font().measure(col.title()))
        x += 1

    for item in area_result_list:
        tree.insert('', 'end', values=item)
        # adjust column's width if necessary to fit each value
        # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
        for ix, val in enumerate(item):
            col_w = tkFont.Font().measure(val)
            if tree.column(Parking_Lot_header[ix], width=None) < col_w:
                tree.column(Parking_Lot_header[ix], width=col_w)

# 停車場名稱 的關鍵字查詢
def find_parkName():
    nameWindow = tk.Toplevel(win)  # 開新視窗 nameWindow
    nameWindow.wm_title("停車場名稱查詢")  # 設定新視窗標題
    nameWindow.minsize(width=700, height=400)  # 調整新視窗大小
    nameWindow.resizable(width=False,height=False)   # 禁止調整視窗大小

    name_result = tk.StringVar()
    name = entry_parkName.get()
    name_result_list = []
    for i in data['parkingLots']:
        if i['parkName'].find(name) >= 0:
            if int(i['surplusSpace']) < 0 or int(i['totalSpace']) <= 0 or int(i['surplusSpace']) >int(i['totalSpace']):
                del i
            else:
                name_result_list.append((i['areaName'],i['surplusSpace'],i['parkName'],
                                         i['address'],i['payGuide'],int(i['totalSpace'])))
    #print('\n搜尋完畢!')
    name_result.set(name_result_list)
    #print(name_result_list)

    frame = Frame(nameWindow)
    frame.place(x=0, y=0, width=700, height=400)

    # 滚动条初始化（scrollBar为垂直滚动条，scrollBarx为水平滚动条）
    scrollBar = ttk.Scrollbar(frame)
    scrollBarx = ttk.Scrollbar(frame, orient='horizontal')
    #靠右，充满Y轴
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
    # 靠下，充满X轴
    scrollBarx.pack(side=tk.BOTTOM, fill=tk.X)

    # 页面内显示表格
    # height 表示要显示几行数据（这个部件的宽度是根据列的多少以及每列的设置宽度一同定义的）
    tree = ttk.Treeview(frame, height = 31,
                    columns=Parking_Lot_header,
                    show="headings",
                    yscrollcommand=scrollBar.set,
                    xscrollcommand=scrollBarx.set)
    # side=LEFT表示表格位于窗口左端，
    # fill=BOTH表示当窗口改变大小时会在X与Y方向填满窗口
    tree.pack(side=tk.LEFT, fill=tk.BOTH)
    # 而当用户操纵滚动条的时候，自动调用 Treeview 组件的 yview()与xview() 方法
    # 即滚动条与页面内容的位置同步
    scrollBar.config(command=tree.yview)
    scrollBarx.config(command=tree.xview)

    x = 0
    for col in Parking_Lot_header:
        if x == 1 or x == 5:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby_num(tree, c, 0))
            tree.column(col, width=tkFont.Font().measure(col.title()))
        else:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby(tree, c, 0))
            # adjust the column's width to the header string
            tree.column(col, width=tkFont.Font().measure(col.title()))
        x += 1

    for item in name_result_list:
        tree.insert('', 'end', values=item)
        # adjust column's width if necessary to fit each value
        # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
        for ix, val in enumerate(item):
            col_w = tkFont.Font().measure(val)
            if tree.column(Parking_Lot_header[ix], width=None) < col_w:
                tree.column(Parking_Lot_header[ix], width=col_w)

# 地址 的關鍵字查詢
def find_address():
    addressWindow = tk.Toplevel(win)  # 開新視窗 addressWindow
    addressWindow.wm_title("停車場所在地址查詢")  # 設定新視窗標題
    addressWindow.minsize(width=700, height=400)  # 調整新視窗大小
    addressWindow.resizable(width=False, height=False)  # 禁止調整視窗大小

    address_result = tk.StringVar()
    address = entry_address.get()
    address_result_list = []
    for i in data['parkingLots']:
        if i['address'].find(address) >= 0:
            if int(i['surplusSpace']) < 0 or int(i['totalSpace']) <= 0 or int(i['surplusSpace']) > int(i['totalSpace']):
                del i
            else:
                address_result_list.append((i['areaName'], i['surplusSpace'], i['parkName'],
                                         i['address'], i['payGuide'], int(i['totalSpace'])))
    # print('\n搜尋完畢!')
    address_result.set(address_result_list)
    # print(address_result_list)

    frame = Frame(addressWindow)
    frame.place(x=0, y=0, width=700, height=400)

    # 滚动条初始化（scrollBar为垂直滚动条，scrollBarx为水平滚动条）
    scrollBar = ttk.Scrollbar(frame)
    scrollBarx = ttk.Scrollbar(frame, orient='horizontal')
    # 靠右，充满Y轴
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
    # 靠下，充满X轴
    scrollBarx.pack(side=tk.BOTTOM, fill=tk.X)

    # 页面内显示表格
    # height 表示要显示几行数据（这个部件的宽度是根据列的多少以及每列的设置宽度一同定义的）
    tree = ttk.Treeview(frame, height=31,
                        columns=Parking_Lot_header,
                        show="headings",
                        yscrollcommand=scrollBar.set,
                        xscrollcommand=scrollBarx.set)
    # side=LEFT表示表格位于窗口左端，
    # fill=BOTH表示当窗口改变大小时会在X与Y方向填满窗口
    tree.pack(side=tk.LEFT, fill=tk.BOTH)
    # 而当用户操纵滚动条的时候，自动调用 Treeview 组件的 yview()与xview() 方法
    # 即滚动条与页面内容的位置同步
    scrollBar.config(command=tree.yview)
    scrollBarx.config(command=tree.xview)

    x = 0
    for col in Parking_Lot_header:
        if x == 1 or x == 5:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby_num(tree, c, 0))
            tree.column(col, width=tkFont.Font().measure(col.title()))
        else:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby(tree, c, 0))
            # adjust the column's width to the header string
            tree.column(col, width=tkFont.Font().measure(col.title()))
        x += 1

    for item in address_result_list:
        tree.insert('', 'end', values=item)
        # adjust column's width if necessary to fit each value
        # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
        for ix, val in enumerate(item):
            col_w = tkFont.Font().measure(val)
            if tree.column(Parking_Lot_header[ix], width=None) < col_w:
                tree.column(Parking_Lot_header[ix], width=col_w)

# 行政區,停車場名稱,地址 的綜合查詢
## name = input('請輸入關鍵字:')
def find_keyword():
    keywordWindow = tk.Toplevel(win)  # 開新視窗 keywordWindow
    keywordWindow.wm_title("停車場名稱查詢")  # 設定新視窗標題
    keywordWindow.minsize(width=700, height=400)  # 調整新視窗大小
    keywordWindow.resizable(width=False, height=False)  # 禁止調整視窗大小

    keyword_result = tk.StringVar()
    keyword = entry_keywordSearch.get()
    keyword_result_list = []
    for i in data['parkingLots']:
        if i['areaName'].find(keyword) >= 0 or i['parkName'].find(keyword) >= 0 or i['address'].find(keyword) >= 0:
            if int(i['surplusSpace']) < 0 or int(i['totalSpace']) <= 0 or int(i['surplusSpace']) > int(i['totalSpace']):
                del i
            else:
                keyword_result_list.append((i['areaName'], i['surplusSpace'], i['parkName'],
                                         i['address'], i['payGuide'], int(i['totalSpace'])))
    # print('\n搜尋完畢!')
    keyword_result.set(keyword_result_list)
    # print(address_result_list)

    frame = Frame(keywordWindow)
    frame.place(x=0, y=0, width=700, height=400)

    # 滚动条初始化（scrollBar为垂直滚动条，scrollBarx为水平滚动条）
    scrollBar = ttk.Scrollbar(frame)
    scrollBarx = ttk.Scrollbar(frame, orient='horizontal')
    # 靠右，充满Y轴
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
    # 靠下，充满X轴
    scrollBarx.pack(side=tk.BOTTOM, fill=tk.X)

    # 页面内显示表格
    # height 表示要显示几行数据（这个部件的宽度是根据列的多少以及每列的设置宽度一同定义的）
    tree = ttk.Treeview(frame, height=31,
                        columns=Parking_Lot_header,
                        show="headings",
                        yscrollcommand=scrollBar.set,
                        xscrollcommand=scrollBarx.set)
    # side=LEFT表示表格位于窗口左端，
    # fill=BOTH表示当窗口改变大小时会在X与Y方向填满窗口
    tree.pack(side=tk.LEFT, fill=tk.BOTH)
    # 而当用户操纵滚动条的时候，自动调用 Treeview 组件的 yview()与xview() 方法
    # 即滚动条与页面内容的位置同步
    scrollBar.config(command=tree.yview)
    scrollBarx.config(command=tree.xview)

    x = 0
    for col in Parking_Lot_header:
        if x == 1 or x == 5:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby_num(tree, c, 0))
            tree.column(col, width=tkFont.Font().measure(col.title()))
        else:
            tree.heading(col, text=col.title(), command=lambda c=col: sortby(tree, c, 0))
            # adjust the column's width to the header string
            tree.column(col, width=tkFont.Font().measure(col.title()))
        x += 1

    for item in keyword_result_list:
        tree.insert('', 'end', values=item)
        # adjust column's width if necessary to fit each value
        # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
        for ix, val in enumerate(item):
            col_w = tkFont.Font().measure(val)
            if tree.column(Parking_Lot_header[ix], width=None) < col_w:
                tree.column(Parking_Lot_header[ix], width=col_w)

# 計算各行政區停車格數量
def Count():
    countWindow = tk.Toplevel(win)                # 開新視窗 countWindow
    countWindow.wm_title("各行政區停車格數量總計")  # 設定新視窗標題
    countWindow.minsize(width=700, height=400)   # 調整新視窗大小
    countWindow.resizable(width=False, height=False)  # 禁止調整視窗大小

    count = {'桃園區':0,'中壢區':0,'平鎮區':0,
            '八德區':0,'楊梅區':0,'蘆竹區':0,
            '龜山區':0,'龍潭區':0,'大溪區':0,
            '大園區':0,'觀音區':0,'新屋區':0,
            '復興區':0}

    for x in range(0,len(Parking_Lot_list)):
        if Parking_Lot_list[x][0] in Using_rate:
            count[Parking_Lot_list[x][0]] += Parking_Lot_list[x][5]
        else:
            count[Parking_Lot_list[x][0]] = count[Parking_Lot_list[x][0]]
        x += 1

    figure3 = plt.Figure(figsize=(8, 5), dpi=100)
    ax3 = figure3.add_subplot(111)

    areas = list(count.keys())
    units = list(count.values())

    ax3.bar(areas, units)
    ax3.set_title('各行政區停車格總數')
    ax3.set_ylabel('數量(格)')

    canvas2 = FigureCanvasTkAgg(figure3, master=countWindow)
    canvas2.draw()
    canvas2.get_tk_widget().grid(row=0)

# 定義各行政區使用率畫圖方法
def rates_charts():
    ratesWindow = tk.Toplevel(win)  # 開新視窗 ratesWindow
    ratesWindow.wm_title("各行政區停車場總使用率")  # 設定新視窗標題
    ratesWindow.minsize(width=700, height=400)  # 調整新視窗大小
    ratesWindow.resizable(width=False, height=False)  # 禁止調整視窗大小
    #ratesWindow.geometry("+%d+%d" % (w / 2.7, h / 4))  # 調整新視窗開啟的位置
    #ratesWindow.grab_set()

    figure1 = plt.Figure(figsize=(8, 5), dpi=100)
    ax1 = figure1.add_subplot(111)

    areas = list(Using_rate.keys())
    rates_s = list(Using_rate.values())
    rates_f = []
    for i in rates_s:
        i = float(i)*100
        rates_f.append(i)
    ax1.bar(areas, rates_f)
    ax1.set_title('各行政區停車場總使用率')
    ax1.set_ylabel('單位:%')

    canvas1 = FigureCanvasTkAgg(figure1, master=ratesWindow)
    canvas1.draw()
    canvas1.get_tk_widget().grid(row=0)

# 各行政區停車場數量計算
def parkingLotsCount():
    LotscountWindow = tk.Toplevel(win)  # 開新視窗 LotscountWindow
    LotscountWindow.wm_title("各行政區停車場總數")  # 設定新視窗標題
    LotscountWindow.minsize(width=700, height=400)  # 調整新視窗大小
    LotscountWindow.resizable(width=False, height=False)  # 禁止調整視窗大小

    Lotscount= {'桃園區':0,'中壢區':0,'平鎮區':0,
            '八德區':0,'楊梅區':0,'蘆竹區':0,
            '龜山區':0,'龍潭區':0,'大溪區':0,
            '大園區':0,'觀音區':0,'新屋區':0,
            '復興區':0}

    for x in range(0,len(Parking_Lot_list)):
        if Parking_Lot_list[x][0] in Using_rate:
            Lotscount[Parking_Lot_list[x][0]] += 1
        else:
            Lotscount[Parking_Lot_list[x][0]] = count[Parking_Lot_list[x][0]]
        x += 1

    figure2 = plt.Figure(figsize=(8, 5), dpi=100)
    ax2 = figure2.add_subplot(111)

    areas = list(Lotscount.keys())
    quantity = list(Lotscount.values())

    ax2.bar(areas, quantity)
    ax2.set_title('各行政區停車場總數')
    ax2.set_ylabel('數量(座)')

    canvas2 = FigureCanvasTkAgg(figure2, master=LotscountWindow)
    canvas2.draw()
    canvas2.get_tk_widget().grid(row=0)



class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self):
        self.tree = None
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        #s = "消費紀錄"  (如果 frame 裡要有標題再加上這行及下一行)
        #msg = ttk.Label(wraplength="4i", justify="left", anchor="n",padding=(10, 2, 10, 6), text=s)
        # wraplength: 更改一行最多顯示的字數, 此處為超過 4英吋 就換行。
        # anchor: 位於表格中的位置, (n, s, w, e, ne, nw, sw, se, center)，nswe分別為東西南北的字首，默認為center。
        # justify: 將文字對齊，可用值為left靠左對齊、right靠右對齊、center置中對齊，預設值為center。
        # padding: To add more space around all four sides of the text and/or image,
        #          set this option to the desired dimension. You may also specify this option using a style.
        #msg.pack(fill='x')
        # pack:打包,將剛建立的控制元件通過打包的方法來放置到視窗中。
        # fill='x':寬度會填充滿整個視窗的寬度
        container = ttk.Frame()    # 製作一個 frame
        container.place(x=0,y=200, width=w,height=(h/2), anchor='nw')
        # container.pack(fill='x', expand=True, anchor="s",width=w,height=(h/2))
        # fill='both':X 和 Y 方向的結合，會自動在寬度和高度方向上填滿整個視窗。
        # 當 expand=True or 1 時，列表框就會鋪開列表中所有的元素。
        # 假如 expand 選項沒有選中的話，那麼列表框就預設的只顯示了前十個元素，
        # 後續的元素需要你選中列表框後通過滑鼠或者方向鍵移動才能夠顯示出來。

        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=Parking_Lot_header, show="headings")
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def _build_tree(self):
        x = 0
        for col in Parking_Lot_header:
            if x == 1 or x == 5:
                self.tree.heading(col, text=col.title(), command=lambda c=col: sortby_num(self.tree, c, 0))
                self.tree.column(col, width=tkFont.Font().measure(col.title()))
            else:
                self.tree.heading(col, text=col.title(), command=lambda c=col: sortby(self.tree, c, 0))
                # adjust the column's width to the header string
                self.tree.column(col, width=tkFont.Font().measure(col.title()))
            x += 1

        for item in Parking_Lot_list:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(Parking_Lot_header[ix],width=None)<col_w:
                    self.tree.column(Parking_Lot_header[ix], width=col_w)

def sortby(tree, col, descending):       # 重新排序 <-- 文字版
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]

    # if the data to be sorted is numeric change to float
    #data = change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    # 數字的排法(但文字部分就無法排序)
    #data.sort(key=lambda data: int(data[0]), reverse=descending)

    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)

    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))

def sortby_num(tree, col, descending):       # 重新排序 <-- 數字版
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]

    # if the data to be sorted is numeric change to float
    #data = change_numeric(data)
    # now sort the data in place
    #data.sort(reverse=descending)
    # 數字的排法(但文字部分就無法排序)
    data.sort(key=lambda data: int(data[0]), reverse=descending)

    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)

    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby_num(tree, col, \
        int(not descending)))

if __name__ == '__main__':
    win = tk.Tk()
    win.title("桃園市找車位神器")
    w = 800
    h = 400
    win.minsize(width=w, height=h)
    win.resizable(False,False)

    # Reading data back  讀已下載下來的檔案
    with open('路外停車資訊.json', 'r', encoding='utf-8') as f:
        # str1 = f.read()
        data = json.load(f)  # 讀檔案的時候要用沒有 s 的
        Parking_Lot_list = []
        for i in data['parkingLots']:
            # 刪除 剩餘空位小於 0 或 總車位小於等於 0 或 剩餘空位大於總車位 的無意義資料
            if int(i['surplusSpace']) < 0 or int(i['totalSpace']) <= 0 or int(i['surplusSpace']) >int(i['totalSpace']):
                del i
            else:
                Parking_Lot_list.append((i['areaName'],int(i['surplusSpace']),i['parkName'],i['address'],i['payGuide'],int(i['totalSpace'])))
        # 各行政區停車場使用率計算
        Taoyuan_total = 0
        Taoyuan_surplus = 0
        Taoyuan_using_rate = 0
        Zhongli_total = 0
        Zhongli_surplus = 0
        Zhongli_using_rate = 0
        Pingzhen_total = 0
        Pingzhen_surplus = 0
        Pingzhen_using_rate = 0
        Bade_total = 0
        Bade_surplus = 0
        Bade_using_rate = 0
        Yangmei_total = 0
        Yangmei_surplus = 0
        Yangmei_using_rate = 0
        Luzhu_total = 0
        Luzhu_surplus = 0
        Luzhu_using_rate = 0
        Guishan_total = 0
        Guishan_surplus = 0
        Guishan_using_rate = 0
        Longtan_total = 0
        Longtan_surplus = 0
        Longtan_using_rate = 0
        Daxi_total = 0
        Daxi_surplus = 0
        Daxi_using_rate = 0
        Dayuan_total = 0
        Dayuan_surplus = 0
        Dayuan_using_rate = 0
        Guanyin_total = 0
        Guanyin_surplus = 0
        Guanyin_using_rate = 0
        Xinwu_total = 0
        Xinwu_surplus = 0
        Xinwu_using_rate = 0
        Fuxing_total = 0
        Fuxing_surplus = 0
        Fuxing_using_rate = 0
        for i in data['parkingLots']:
            if i['areaName'] == '桃園區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Taoyuan_total = Taoyuan_total + int(i['totalSpace'])
                Taoyuan_surplus = Taoyuan_surplus + int(i['surplusSpace'])
                Taoyuan_using_rate = '%.2f' % ((Taoyuan_total - Taoyuan_surplus) / Taoyuan_total)
            elif i['areaName'] == '中壢區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Zhongli_total = Zhongli_total + int(i['totalSpace'])
                Zhongli_surplus = Zhongli_surplus + int(i['surplusSpace'])
                Zhongli_using_rate = '%.2f' % ((Zhongli_total - Zhongli_surplus) / Zhongli_total)
            elif i['areaName'] == '平鎮區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Pingzhen_total = Pingzhen_total + int(i['totalSpace'])
                Pingzhen_surplus = Pingzhen_surplus + int(i['surplusSpace'])
                Pingzhen_using_rate = '%.2f' % ((Pingzhen_total - Pingzhen_surplus) / Pingzhen_total)
            elif i['areaName'] == '八德區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Bade_total = Bade_total + int(i['totalSpace'])
                Bade_surplus = Bade_surplus + int(i['surplusSpace'])
                Bade_using_rate = '%.2f' % ((Bade_total - Bade_surplus) / Bade_total)
            elif i['areaName'] == '楊梅區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Yangmei_total = Yangmei_total + int(i['totalSpace'])
                Yangmei_surplus = Yangmei_surplus + int(i['surplusSpace'])
                Yangmei_using_rate = '%.2f' % ((Yangmei_total - Yangmei_surplus) / Yangmei_total)
            elif i['areaName'] == '蘆竹區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Luzhu_total = Luzhu_total + int(i['totalSpace'])
                Luzhu_surplus = Luzhu_surplus + int(i['surplusSpace'])
                Luzhu_using_rate = '%.2f' % ((Luzhu_total - Luzhu_surplus) / Luzhu_total)
            elif i['areaName'] == '龜山區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Guishan_total = Guishan_total + int(i['totalSpace'])
                Guishan_surplus = Guishan_surplus + int(i['surplusSpace'])
                Guishan_using_rate = '%.2f' % ((Guishan_total - Guishan_surplus) / Guishan_total)
            elif i['areaName'] == '龍潭區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Longtan_total = Longtan_total + int(i['totalSpace'])
                Longtan_surplus = Longtan_surplus + int(i['surplusSpace'])
                Longtan_using_rate = '%.2f' % ((Longtan_total - Longtan_surplus) / Longtan_total)
            elif i['areaName'] == '大溪區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Daxi_total = Daxi_total + int(i['totalSpace'])
                Daxi_surplus = Daxi_surplus + int(i['surplusSpace'])
                Daxi_using_rate = '%.2f' % ((Daxi_total - Daxi_surplus) / Daxi_total)
            elif i['areaName'] == '大園區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Dayuan_total = Dayuan_total + int(i['totalSpace'])
                Dayuan_surplus = Dayuan_surplus + int(i['surplusSpace'])
                Dayuan_using_rate = '%.2f' % ((Dayuan_total - Dayuan_surplus) / Dayuan_total)
            elif i['areaName'] == '觀音區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Guanyin_total = Guanyin_total + int(i['totalSpace'])
                Guanyin_surplus = Guanyin_surplus + int(i['surplusSpace'])
                Guanyin_using_rate = '%.2f' % ((Guanyin_total - Guanyin_surplus) / Guanyin_total)
            elif i['areaName'] == '新屋區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Xinwu_total = Xinwu_total + int(i['totalSpace'])
                Xinwu_surplus = Xinwu_surplus + int(i['surplusSpace'])
                Xinwu_using_rate = '%.2f' % ((Xinwu_total - Xinwu_surplus) / Xinwu_total)
            elif i['areaName'] == '復興區' and int(i['totalSpace']) > 0 and int(i['surplusSpace']) >= 0 and int(i['surplusSpace'])<=int(i['totalSpace']):
                Fuxing_total = Fuxing_total + int(i['totalSpace'])
                Fuxing_surplus = Fuxing_surplus + int(i['surplusSpace'])
                Fuxing_using_rate = '%.2f' % ((Fuxing_total - Fuxing_surplus) / Fuxing_total)
        Using_rate = {'桃園區':Taoyuan_using_rate,'中壢區':Zhongli_using_rate,'平鎮區':Pingzhen_using_rate,
                      '八德區':Bade_using_rate,'楊梅區':Yangmei_using_rate,'蘆竹區':Luzhu_using_rate,
                      '龜山區':Guishan_using_rate,'龍潭區':Longtan_using_rate,'大溪區':Daxi_using_rate,
                      '大園區':Dayuan_using_rate,'觀音區':Guanyin_using_rate,'新屋區':Xinwu_using_rate,
                      '復興區':Fuxing_using_rate}

        #print(Using_rate)
        #print(len(Parking_Lot_list))       # 刪除後停車場數量從 101 變為 99

        ## 設定字型
        ft1 = tkFont.Font(family="Ubuntu", size=30, weight="bold")
        ft2 = tkFont.Font(family="Ubuntu", size=13)
        ft3 = tkFont.Font(family="Ubuntu", size=12)

        background_image = ImageTk.PhotoImage(Image.open("pictures/wallpaper3.jpg"))  # 讀取背景圖並宣告變數
        background_label = tk.Label(win, image=background_image)  # 顯示圖片
        background_label.place(x=0, y=0, relwidth=1, relheight=1)  # 指定元件位置

        # 設定標題
        label0 = tk.Label(win, text="桃園市找車位神器", fg="black", font=(ft1))
        label0.place(x=20, y=20)

        # 練習題3:
        # 添加幾個 entry , 讓用戶可以直接在程式上 輸入 日期, 時間, 消費人, 品項, 總金額,
        label_area = tk.Label(win, text="行政區:", fg="black", font=ft3)
        label_area.place(x=20, y=90)

        entry_area = tk.Entry(win, width=20)
        entry_area.place(x=85, y=90)

        btn_Area = tk.Button(win, bg="light blue", text="行政區查詢", font=ft3, command=find_Area)  # command 等於定義的 function 的名稱
        btn_Area.place(x=240, y=85)

        label_parkName = tk.Label(win, text="名稱:", fg="black", font=ft3)
        label_parkName.place(x=20, y=120)

        entry_parkName = tk.Entry(win, width=20)
        entry_parkName.place(x=85, y=120)

        btn_parkName = tk.Button(win, bg="light blue", text="名稱查詢", font=ft3, command=find_parkName)  # command 等於定義的 function 的名稱
        btn_parkName.place(x=240, y=115)

        label_address = tk.Label(win, text="地址:", fg="black", font=ft3)
        label_address.place(x=20, y=150)

        entry_address = tk.Entry(win, width=20)
        entry_address.place(x=85, y=150)

        btn_address = tk.Button(win, bg="light blue", text="地址查詢", font=ft3, command=find_address)  # command 等於定義的 function 的名稱
        btn_address.place(x=240, y=145)


        # 設定關鍵字搜尋的 entry
        entry_keywordSearch = tk.Entry(win, width=20, font=ft2)
        entry_keywordSearch.place(x=456, y=40)

        btn_keywordSearch = tk.Button(win, bg="pink", text="綜合查詢", font=ft3, command=find_keyword)  # command 等於定義的 function 的名稱
        btn_keywordSearch.place(x=637, y=35)

        btn_surplusSpace = tk.Button(win, bg="green2", text="仍有剩餘車位的停車場查詢", font=ft3, command=find_surplusSpace)  # command 等於定義的 function 的名稱
        btn_surplusSpace.place(x=456, y=90)

        # command 的定義名稱不需要括號!!
        btn_parking_count = tk.Button(win, bg="yellow", text="停車格數量", font=ft3, command=Count)  # command 等於定義的 function 的名稱
        btn_parking_count.place(x=456, y=140)

        # command 的定義名稱不需要括號!!
        btn_rates = tk.Button(win, bg="yellow", text="使用率查詢", font=ft3, command=rates_charts)  # command 等於定義的 function 的名稱
        btn_rates.place(x=563, y=140)

        btn_lots_count = tk.Button(win, bg="yellow", text="停車場數量", font=ft3, command=parkingLotsCount)  # command 等於定義的 function 的名稱
        btn_lots_count.place(x=670, y=140)

        Parking_Lot_header = ['行政區', '剩餘空位' , '名稱', '地址', '計費方式','總格數']

        listbox = MultiColumnListbox()

        count = {'桃園區': 0, '中壢區': 0, '平鎮區': 0,
                 '八德區': 0, '楊梅區': 0, '蘆竹區': 0,
                 '龜山區': 0, '龍潭區': 0, '大溪區': 0,
                 '大園區': 0, '觀音區': 0, '新屋區': 0,
                 }
        #print(type(count['桃園區']))   # <class 'int'>
        #print(type(Using_rate[Parking_Lot_list[0][0]]))   #<class 'str'>
        #print(type(Using_rate.keys()))
        win.mainloop()


