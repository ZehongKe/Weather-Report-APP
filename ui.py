# -*- coding: utf-8 -*-
import cairosvg
import xml.etree.ElementTree as ET
import os
import getmes
import wx
import wx.xrc
import wx.aui
import wx.lib.agw.ribbon as rb
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.figure as mfigure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.transforms import Bbox
import wx.lib.wordwrap as wordwrap

lan = 'cn'
city_list = ['北京海淀区', '广州白云']
city = '北京海淀区'
citycode = 101010200
cityfullname = '中国北京市北京海淀区'
# id 对照 1 2 3对应上面三个按钮 4对应搜索按钮


#读取icons文件夹下所有svg文件并转化成png文件，需要修改svg中的width和height属性来保证最后分辨率
def transfersvg_png():
    for file in os.listdir('icons'):
        if file.endswith('.svg'):
            # 解析SVG文件
            tree = ET.parse('icons/'+file)
            root = tree.getroot()

            # 设置width和height属性
            root.attrib['width'] = '300'
            root.attrib['height'] = '300'

            # 将更改写回文件
            tree.write('icons/'+file)

            # 将SVG转换为PNG
            cairosvg.svg2png(url='icons/'+file, write_to='icons/'+file[:-4]+'.png')


# 解析时间字符串，返回格式化时间
def parse_time(time_str):
	time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M%z')
	return time.strftime("%Y-%m-%d %H:%M")


#构造页面1，放置实时天气信息和24h天气
class page1(wx.ScrolledWindow):
	
	#继承wx.ScrolledWindow类，建立第一个页面
	#page1包含两个部分，分别放置实时天气和未来24h天气
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		# 设置滚动条
		self.SetScrollbars(20, 20, 50, 50)
		#获取实时天气信息
		update_time, now_data = getmes.weathernow(lan, citycode)
		#获取未来24h天气信息
		update_time, hours_data = getmes.weatherfeature(lan, citycode)
		

		#总体为竖直布局
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		#设置一个水平布局，放置更新时间、当前城市
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		#先添加更新时间
		if lan == 'cn':
			title = wx.StaticText(self, label="更新时间：")
		elif lan == 'en':
			title = wx.StaticText(self, label="Update Time:")
		hbox.Add(title, 0, wx.ALL, 5)
		#再添加更新时间
		title = wx.StaticText(self, label=parse_time(update_time)+'  ')
		hbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		#再添加城市
		if lan == 'cn':
			title = wx.StaticText(self, label="城市：")
		elif lan == 'en':
			title = wx.StaticText(self, label="City:")
		hbox.Add(title, 0, wx.ALL, 5)
		# 城市名为国家+一级行政区+上级行政区
		title = wx.StaticText(self, label=cityfullname)
		hbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		#再设置一个水平布局，放置实时天气信息
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		#先添加当前天气的图标，根据data['icon']来选择图标
		img = wx.Image('icons/'+now_data['icon']+'.png').Scale(150, 150, wx.IMAGE_QUALITY_HIGH)
		bitmap = wx.Bitmap(img)
		weathericon = wx.StaticBitmap(self, bitmap=bitmap, size=(150,150))
		hbox1.Add(weathericon, 0, wx.ALL, 5)
		#添加气温，字号稍微大一点，与图标对齐
		font = wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title = wx.StaticText(self, label=now_data['temp']+'℃')
		title.SetFont(font)  # 将新的字体设置为wx.StaticText的字体
		hbox1.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 10)

		#再放置天气描述、风力风向、体感温度、相对湿度, 用预先定义的小模块避免代码重复
		girdmodels = wx.GridSizer(2, 2, 0, 0)
		if lan == 'cn':
			title = "天气："
		elif lan == 'en':
			title = "Weather:"
		weathergird = self.modlegrid(title, 'tianqi', now_data['text'])
		girdmodels.Add(weathergird, 0, wx.EXPAND|wx.ALL, 5)

		if lan == 'cn':
			title = "风力风向："
			windgird = self.modlegrid(title, 'wind', now_data['windDir']+now_data['windScale']+'级')
		elif lan == 'en':
			title = "Wind:"
			windgird = self.modlegrid(title, 'wind', now_data['windDir']+' Level'+now_data['windScale'])
		girdmodels.Add(windgird, 0, wx.EXPAND|wx.ALL, 5)

		if lan == 'cn':
			title = "体感温度："
		elif lan == 'en':
			title = "Feels Like:"
		feelgird = self.modlegrid(title, 'tem', now_data['feelsLike']+'℃')
		girdmodels.Add(feelgird, 0, wx.EXPAND|wx.ALL, 5)
		
		if lan == 'cn':
			title = "相对湿度："
		elif lan == 'en':
			title = "Humidity:"
		humigird = self.modlegrid(title, 'wet', now_data['humidity']+'%')
		girdmodels.Add(humigird, 0, wx.EXPAND|wx.ALL, 5)
		hbox1.Add(girdmodels, 0, wx.ALL, 5)


		# 创建一个可以滚动的窗口
		scroll = wx.ScrolledWindow(self, -1,style=wx.SUNKEN_BORDER)
		scroll.SetSizeHints(700, 180, 700, 180)
		scroll.SetScrollbars(0, 1, 0, 400)
		#再添加预警信息panel，放置预警信息图标，如果有预警信息，显示预警信息，否则显示无预警信息,考虑信息可能很多，用滑动条
		update_time, warn_data = getmes.getwarn(lan, citycode)
		panel=wx.Panel(scroll, style=wx.RAISED_BORDER)
		# 整体为竖直布局
		vbox = wx.BoxSizer(wx.VERTICAL)
		#添加天气预警标题
		if lan == 'cn':
			title = wx.StaticText(panel, label="天气预警")
		elif lan == 'en':
			title = wx.StaticText(panel, label="Warning")
		vbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		if warn_data == []:
			if lan == 'cn':
				title = wx.StaticText(panel, label="无预警信息")
			elif lan == 'en':
				title = wx.StaticText(panel, label="No Warning")
			vbox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		else:
			if lan == 'cn':
				title = wx.StaticText(panel, label="预警信息")
			elif lan == 'en':
				title = wx.StaticText(panel, label="Warning")
			vbox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
			for i in range(len(warn_data)):
				#添加一个水平布局，放置预警图标和预警信息标题、预警开始结束时间
				hboxwarn = wx.BoxSizer(wx.HORIZONTAL)
				#添加预警图标
				img = wx.Image('icons/'+warn_data[i]['type']+'.png').Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
				bitmap = wx.Bitmap(img)
				weathericon = wx.StaticBitmap(panel, bitmap=bitmap, size=(30,30))
				hboxwarn.Add(weathericon, 0, wx.ALL|wx.ALIGN_CENTER, 5)
				#添加预警信息标题、预警开始结束时间
				vboxwarn = wx.BoxSizer(wx.VERTICAL)
				if lan == 'cn':
					title = wx.StaticText(panel, label=warn_data[i]['title'])
				elif lan == 'en':
					title = wx.StaticText(panel, label=warn_data[i]['title'])
				vboxwarn.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
				if lan == 'cn':
					title = wx.StaticText(panel, label=parse_time(warn_data[i]['startTime'])+'至'+parse_time(warn_data[i]['endTime']))
				elif lan == 'en':
					title = wx.StaticText(panel, label=parse_time(warn_data[i]['startTime'])+'to'+parse_time(warn_data[i]['endTime']))
				vboxwarn.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
				hboxwarn.Add(vboxwarn, 0, wx.ALL|wx.ALIGN_LEFT, 5)
				vbox.Add(hboxwarn, 0, wx.ALL|wx.ALIGN_LEFT, 5)

				# 使用wordwrap函数将文本换行
				wrapped_text = wordwrap.wordwrap(warn_data[i]['text'], 700, wx.ClientDC(panel))
				# 创建一个wx.StaticText，将换行后的文本设置为其标签
				title = wx.StaticText(panel, label=wrapped_text)
				vbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
				
		panel.SetSizer(vbox)
		#将panel加入滑动条
		scroll_sizer = wx.BoxSizer(wx.VERTICAL)
		scroll_sizer.Add(panel, 0, wx.EXPAND|wx.ALIGN_LEFT, 5)
		scroll.SetSizer(scroll_sizer)
		#将滑动条加入水平布局
		hbox1.Add(scroll, 0, wx.ALL, 5)
		#将水平布局加入竖直布局
		sizer.Add(hbox, 0, wx.EXPAND|wx.ALL, 5)
		sizer.Add(hbox1, 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizer(sizer)

		#再设置一个水平布局，放置未来24h天气信息的折线图，不同折线图类似标签页的切换
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		
		#先添加一个notebook，用于放置折线图
		self.notebook = wx.aui.AuiNotebook( self, wx.ID_ANY,style = wx.aui.AUI_NB_TOP)
		
		#再添加两个页面，分别放置温度，风力风向和降雨量, 为了方便调试，这三个页面的构造函数单独给出
		self.page3 = modleplt(self, hours_data, 'temp')
		self.page4 = modleplt(self, hours_data, 'windSpeed')
		self.page5 = modleplt(self, hours_data, 'precip')
		
		#将三个页面加入notebook
		if lan == 'cn':
			self.notebook.AddPage(self.page3, "温度")
			self.notebook.AddPage(self.page4, "风力")
			self.notebook.AddPage(self.page5, "降雨量")
		elif lan == 'en':
			self.notebook.AddPage(self.page3, "Temperature")
			self.notebook.AddPage(self.page4, "WindSpeed")
			self.notebook.AddPage(self.page5, "Rainfall")

		# 为页面加上图标
		self.icon3 = wx.Image('icons/tem.png').Scale(20, 20, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
		self.icon4 = wx.Image('icons/wind.png').Scale(20, 20, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
		self.icon5 = wx.Image('icons/rain.png').Scale(20, 20, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
		self.notebook.SetPageBitmap(0, self.icon3)
		self.notebook.SetPageBitmap(1, self.icon4)
		self.notebook.SetPageBitmap(2, self.icon5)
		hbox2.Add(self.notebook, 1, wx.EXPAND|wx.ALL, 5)
		#将水平布局加入竖直布局
		sizer.Add(hbox2, 1, wx.EXPAND|wx.ALL, 5)


	#构造小模块，输入title，iconname和对应数值，返回一个grid，包含图标和文字
	def modlegrid(self,titlename, iconname, data):	
		panel = wx.Panel(self, style=wx.RAISED_BORDER)
		grid = wx.GridSizer(1, 2, 0, 0)
		panel.SetSizer(grid)
		img = wx.Image('icons/'+iconname+'.png').Scale(60, 60, wx.IMAGE_QUALITY_HIGH)
		bitmap = wx.Bitmap(img)
		weathericon = wx.StaticBitmap(panel, bitmap=bitmap, size=(60,60))
		grid.Add(weathericon, 0, wx.ALL, 5)
		title = wx.StaticText(panel, label=titlename+'\n'+data)
		# 调整字体大小
		font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font) 
		grid.Add(title, 0, wx.ALL, 5)
		
		return panel


#构造单独的类，输入hours_data和对应数值，返回一个折线图,从panel继承
class modleplt(wx.Panel):
	#用于放置图表的panel
	def __init__(self,parent,hours_data, name):
		wx.Panel.__init__(self, parent)
		self.canvas = FigureCanvas(self, -1, self.create_figure(hours_data, name))
		self.canvas.mpl_connect('motion_notify_event', self.on_move)
		# 加入到panel
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND|wx.ALL, 5)
		self.SetSizer(sizer)

	
	def create_figure(self, hours_data, name):
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)
		# 创建一个matplotlib的图形和一个子图,均靠左放置
		fig = mfigure.Figure(figsize=(5,4), dpi=100)
		ax = fig.add_subplot(111)
		#设置x轴的刻度，用时间表示, 取解析后的时间的最后5个字符，即小时，每隔2个小时显示一个刻度
		x = [parse_time(i['fxTime'])[-5:] for i in hours_data]
		ax.set_xticks(range(0, len(x), 2))
		ax.set_xticklabels(x[::2])
		#设置y轴的刻度，根据name选择不同的刻度，特别的，降雨量需要用柱状图表示,折线图用空心圆点表示数据
		if name == 'precip':
			y = [float(i['precip']) for i in hours_data]
			ax.bar(x, y, width=0.5, color='blue')
		else:
			y = [float(i[name]) for i in hours_data]
			ax.plot(x, y, 'o-', color='blue', fillstyle='none', linewidth=1, markersize=1)
		
		#调整图表框线
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['bottom'].set_visible(False)
		ax.spines['left'].set_visible(False)

		#对不同name，进行不同的注解、纵坐标单位处理
		self.annotations=[]
		for i in range(len(x)):
			
			# 标注点的坐标
			point_x=x[i]
			point_y=y[i]
			point,  = ax.plot(point_x, point_y, 'o', color='blue', markersize=1)
			#标注框的位置
			xytext=(10,-15)
			bbox=dict(boxstyle='round', fc='gray', alpha=0.6)
			
			#标注字体
			plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 指定默认字体为微软雅黑
			plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
			# 标注点的注释
			if name == 'temp':
				ax.set_ylabel('℃',rotation='horizontal', loc='top')
				
				#添加注解显示时间、温度和天气描述
				annotation=ax.annotate(parse_time(hours_data[i]['fxTime'])[-5:]+'\n'+hours_data[i]['temp']+'℃\n'+str(hours_data[i]['text']), 
						xy=(x[i], y[i]), xytext=xytext, textcoords='offset points', bbox=bbox, size = 10)
				# 隐藏注解直到鼠标移动到对应点
				annotation.set_visible(False)
				self.annotations.append([point, annotation])
			
			elif name == 'windSpeed':
				ax.set_ylabel('km/h',rotation='horizontal', loc='top')
				
				#添加注解显示时间、风向和风力
				if lan == 'cn':
					annotation=ax.annotate(parse_time(hours_data[i]['fxTime'])[-5:]+'\n'+hours_data[i]['windDir']+'\n'+hours_data[i]['windScale']+'级',
						xy=(x[i], y[i]), xytext=xytext, textcoords='offset points', bbox=bbox, size = 10)
				elif lan == 'en':
					annotation=ax.annotate(parse_time(hours_data[i]['fxTime'])[-5:]+'\n'+hours_data[i]['windDir']+'\nLevel '+hours_data[i]['windScale'],
						xy=(x[i], y[i]), xytext=xytext, textcoords='offset points', bbox=bbox, size = 10)
				# 隐藏注解直到鼠标移动到对应点
				annotation.set_visible(False)
				self.annotations.append([point, annotation])

			elif name == 'precip':
				ax.set_ylabel('mm',rotation='horizontal', loc='top')
				
				#添加注解显示时间、降雨量
				annotation=ax.annotate(parse_time(hours_data[i]['fxTime'])[-5:]+'\n'+hours_data[i]['precip']+'mm',
						xy=(x[i], y[i]), xytext=xytext, textcoords='offset points', bbox=bbox, size = 10)
				# 隐藏注解直到鼠标移动到对应点
				annotation.set_visible(False)
				self.annotations.append([point,annotation])
		#返回图形
		return fig

		#鼠标移动到对应点时显示注解	
	def on_move(self, event):
		
		visibility_changed = False
        # 检查鼠标是否在数据点上
		for point, annotation in self.annotations:
			should_be_visible = (point.contains(event)[0] == True)
			if should_be_visible != annotation.get_visible():
				visibility_changed = True
				annotation.set_visible(should_be_visible)
		if visibility_changed:
			# 重绘图形
			self.canvas.draw()


#构造页面2，放置未来7天天气信息
class page2(wx.Panel):
	def __init__(self, parent):

	#page2包含一个子页面，放置未来7天天气，有日期图标最高最低温等信息
		wx.Panel.__init__(self, parent)
		# 获取信息
		update_time, self.days_data = getmes.weather7d(lan, citycode)
		# 整体为竖直布局
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		
		#设置一个水平布局，放置更新时间、当前城市
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)
		#先添加更新时间
		if lan == 'cn':
			title = wx.StaticText(self, label="更新时间：")
		elif lan == 'en':
			title = wx.StaticText(self, label="Update Time:")
		self.hbox.Add(title, 0, wx.ALL, 5)
		title = wx.StaticText(self, label=parse_time(update_time)+'  ')
		self.hbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		#再添加城市
		if lan == 'cn':
			title = wx.StaticText(self, label="城市：")
		elif lan == 'en':
			title = wx.StaticText(self, label="City:")
		self.hbox.Add(title, 0, wx.ALL, 5)
		if lan == 'cn':
			title = wx.StaticText(self, label=cityfullname)
		elif lan == 'en':
			title = wx.StaticText(self, label=cityfullname)
		self.hbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		self.SetSizer(self.sizer)
		
		#再设置一个带滑动条的水平布局，放置未来7天天气信息的小模块，每个模块为一个panel，单独给出构造
		self.window1 = wx.ScrolledWindow(self, -1, style=wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
		self.window1.SetScrollbars(20, 20, 50, 50)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		self.panel_dict = {}
		for i in range(len(self.days_data)):
			panel = self.modlegrid(self.window1, self.days_data[i])
			self.panel_dict[id(panel)] = i
			hbox1.Add(panel, 0, wx.ALL, 5)
			# 绑定事件
			panel.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
			panel.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
			panel.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
		self.window1.SetSizer(hbox1)

	
		#再添加一个panel，用于显示详细信息
		self.panel = self.modlepanel(self.days_data[0])
		
		#将水平布局加入竖直布局
		self.sizer.Add(self.hbox, 0, wx.EXPAND|wx.ALL, 5)
		self.sizer.Add(self.window1, 1, wx.EXPAND|wx.ALL, 5)
		self.sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL, 5)
		self.SetSizer(self.sizer)
	
	#构造小模块，输入day_data，返回一个panel，包含日期、图标、最高最低温等信息
	def modlegrid(self, parent, day_data):
		# 整体为竖直布局
		panel = wx.Panel(parent, style=wx.RAISED_BORDER)
		vbox = wx.BoxSizer(wx.VERTICAL)

		#先添加日期
		title = wx.StaticText(panel, label=day_data['fxDate']+'\n')
		# 调整字体大小
		font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		vbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		#日夜天气用水平布局放置
		hbox = wx.GridSizer(1, 2, 0, 0)

		#添加白天小模块，从上到下显示图标、最高温度、天气描述、风力风向
		daypanel = wx.Panel(panel)
		daybox = wx.BoxSizer(wx.VERTICAL)
		#添加图标
		img = wx.Image('icons/'+day_data['iconDay']+'.png').Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
		bitmap = wx.Bitmap(img)
		weathericon = wx.StaticBitmap(daypanel, bitmap=bitmap, size=(30,30))
		daybox.Add(weathericon, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		#添加最高温度
		title = wx.StaticText(daypanel, label=day_data['tempMax']+'℃')# 调整字体大小
		font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		daybox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		#添加天气描述
		title = wx.StaticText(daypanel, label=day_data['textDay'])
		daybox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		#添加风力风向
		if lan == 'cn':
			title = wx.StaticText(daypanel, label=day_data['windDirDay']+day_data['windScaleDay']+'级')
		elif lan == 'en':
			title = wx.StaticText(daypanel, label=day_data['windDirDay']+' Level '+day_data['windScaleDay'])
		daybox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		daypanel.SetSizer(daybox)

		#添加夜晚小模块，从上到下显示图标、最低温度、天气描述、风力风向
		nightpanel = wx.Panel(panel)
		nightbox = wx.BoxSizer(wx.VERTICAL)
		#添加图标
		img = wx.Image('icons/'+day_data['iconNight']+'.png').Scale(30, 30, wx.IMAGE_QUALITY_HIGH)
		bitmap = wx.Bitmap(img)
		weathericon = wx.StaticBitmap(nightpanel, bitmap=bitmap, size=(30,30))
		nightbox.Add(weathericon, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		#添加最低温度
		title = wx.StaticText(nightpanel, label=day_data['tempMin']+'℃')
		# 调整字体大小
		font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		nightbox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		#添加天气描述
		title = wx.StaticText(nightpanel, label=day_data['textNight'])
		nightbox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		#添加风力风向
		if lan == 'cn':
			title = wx.StaticText(nightpanel, label=day_data['windDirNight']+day_data['windScaleNight']+'级')
		elif lan == 'en':
			title = wx.StaticText(nightpanel, label=day_data['windDirNight']+' Level '+day_data['windScaleNight'])
		nightbox.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)
		nightpanel.SetSizer(nightbox)

		#将白天和夜晚小模块加入水平布局
		hbox.Add(daypanel, 0, wx.EXPAND|wx.ALL, 5)
		hbox.Add(nightpanel, 0, wx.EXPAND|wx.ALL, 5)
		#将水平布局加入竖直布局
		vbox.Add(hbox, 0,wx.EXPAND|wx.ALL, 5)

		#添加一个水平布局放置降水、紫外线强度指数、相对湿度
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		#添加降水
		if lan == 'cn':
			title = wx.StaticText(panel, label='降水：'+day_data['precip']+'mm')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Precipitation:'+day_data['precip']+'mm')
		hbox.Add(title, 0, wx.ALL, 5)
		#添加紫外线强度指数
		if lan == 'cn':
			title = wx.StaticText(panel, label='紫外线强度指数：'+day_data['uvIndex'])
		elif lan == 'en':
			title = wx.StaticText(panel, label='UV Index:'+day_data['uvIndex'])
		hbox.Add(title, 0, wx.ALL, 5)
		#添加相对湿度
		if lan == 'cn':
			title = wx.StaticText(panel, label='相对湿度：'+day_data['humidity']+'%')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Humidity:'+day_data['humidity']+'%')
		hbox.Add(title, 0, wx.ALL, 5)
		#将水平布局加入竖直布局
		vbox.Add(hbox, 0, wx.ALL, 5)

		panel.SetSizer(vbox)
		return panel

	#构造详细信息模块，输入day_data，返回一个panel，包含日期、图标、最高最低温，日升日落等信息
	def modlepanel(self, day_data):
		# 整体为竖直布局
		panel = wx.Panel(self, style=wx.BORDER_SIMPLE)
		vbox0=wx.BoxSizer(wx.VERTICAL)
		hbox = wx.GridSizer(1,3,25,25)
		# 先添加日期
		title = wx.StaticText(panel, label=day_data['fxDate'])
		vbox0.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 第一个竖直布局放置白天的信息，日出日落、湿度、气压
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		# 添加标题
		if lan == 'cn':
			title = wx.StaticText(panel, label='白天')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Day')
		vbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 添加天气图标、温度,用水平布局
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		img = wx.Image('icons/'+day_data['iconDay']+'.png').Scale(75, 75, wx.IMAGE_QUALITY_HIGH)
		bitmap = wx.Bitmap(img)
		weathericon = wx.StaticBitmap(panel, bitmap=bitmap, size=(75,75))
		hbox1.Add(weathericon, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		title = wx.StaticText(panel, label=day_data['tempMax']+'℃')
		# 调整字体大小
		font = wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		hbox1.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 添加天气描述
		if lan == 'cn':
			title = wx.StaticText(panel, label=day_data['textDay'])
		elif lan == 'en':
			title = wx.StaticText(panel, label=day_data['textDay'])
		#调整字体大小
		font = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		hbox1.Add(title, 0, wx.ALL|wx.ALIGN_BOTTOM, 5)
		vbox.Add(hbox1, 0, wx.ALL, 5)

		# 添加日出日落,考虑为空是显示--
		if day_data['sunrise'] == '':
			day_data['sunrise'] = '--'
		if day_data['sunset'] == '':
			day_data['sunset'] = '--'
		if lan == 'cn':
			title = wx.StaticText(panel, label='日出：'+day_data['sunrise']+' 日落：'+day_data['sunset'])
		elif lan == 'en':
			title = wx.StaticText(panel, label='Sunrise:'+day_data['sunrise']+' Sunset:'+day_data['sunset'])
		vbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 添加湿度
		if lan == 'cn':
			title = wx.StaticText(panel, label='湿度：'+day_data['humidity']+'%')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Humidity:'+day_data['humidity']+'%')
		vbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 添加气压
		if lan == 'cn':
			title = wx.StaticText(panel, label='气压：'+day_data['pressure']+'hPa')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Pressure:'+day_data['pressure']+'hPa')
		vbox.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 第二个竖直布局放置夜晚的天气，月升月落、紫外线、可见度
		vbox1 = wx.BoxSizer(wx.VERTICAL)

		# 添加标题
		if lan == 'cn':
			title = wx.StaticText(panel, label='夜晚')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Night')
		vbox1.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 添加天气图标、温度,用水平布局
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		img = wx.Image('icons/'+day_data['iconNight']+'.png').Scale(75, 75, wx.IMAGE_QUALITY_HIGH)
		bitmap = wx.Bitmap(img)
		weathericon = wx.StaticBitmap(panel, bitmap=bitmap, size=(75,75))
		hbox2.Add(weathericon, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		title = wx.StaticText(panel, label=day_data['tempMin']+'℃')
		# 调整字体大小
		font = wx.Font(25, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		hbox2.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		# 添加天气描述
		if lan == 'cn':
			title = wx.StaticText(panel, label=day_data['textNight'])
		elif lan == 'en':
			title = wx.StaticText(panel, label=day_data['textNight'])
		#调整字体大小
		font = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		hbox2.Add(title, 0, wx.ALL|wx.ALIGN_BOTTOM, 5)
		vbox1.Add(hbox2, 0, wx.ALL, 5)

		# 添加月升月落，考虑为空时显示--
		if day_data['moonrise'] == '':
			day_data['moonrise'] = '--'
		if day_data['moonset'] == '':
			day_data['moonset'] = '--'
		if lan == 'cn':
			title = wx.StaticText(panel, label='月升：'+day_data['moonrise']+' 月落：'+day_data['moonset'])
		elif lan == 'en':
			title = wx.StaticText(panel, label='Moonrise:'+day_data['moonrise']+' Moonset:'+day_data['moonset'])
		vbox1.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 添加紫外线
		if lan == 'cn':
			title = wx.StaticText(panel, label='紫外线：'+day_data['uvIndex'])
		elif lan == 'en':
			title = wx.StaticText(panel, label='UV Index:'+day_data['uvIndex'])
		vbox1.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 添加可见度
		if lan == 'cn':
			title = wx.StaticText(panel, label='可见度：'+day_data['vis']+'km')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Visibility:'+day_data['vis']+'km')
		vbox1.Add(title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

		# 第三个竖直布局放置月相描述
		vbox2 = wx.BoxSizer(wx.VERTICAL)

		# 添加标题
		if lan == 'cn':
			title = wx.StaticText(panel, label='月相')
		elif lan == 'en':
			title = wx.StaticText(panel, label='Moon')
		vbox2.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)

		# 添加月相图标
		img = wx.Image('icons/'+day_data['moonPhaseIcon']+'.png').Scale(60, 60, wx.IMAGE_QUALITY_HIGH)
		bitmap = wx.Bitmap(img)
		weathericon = wx.StaticBitmap(panel, bitmap=bitmap, size=(60,60))
		vbox2.Add(weathericon, 0, wx.ALL|wx.ALIGN_CENTER, 5)

		# 添加文字
		if lan == 'cn':
			title = wx.StaticText(panel, label=day_data['moonPhase'])
		elif lan == 'en':
			title = wx.StaticText(panel, label=day_data['moonPhase'])
		#调整字体大小
		font = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		title.SetFont(font)
		vbox2.Add(title, 0, wx.ALL|wx.ALIGN_CENTER, 5)

		# 将三个竖直布局加入水平布局
		hbox.Add(vbox, 0, wx.ALL, 5)
		hbox.Add(vbox1, 0, wx.ALL, 5)
		hbox.Add(vbox2, 0, wx.ALL, 5)
		hbox.Layout()
		vbox0.Add(hbox, 0, wx.ALL, 5)
		panel.SetSizer(vbox0)
		return panel

	#鼠标点击事件，点击小模块，显示详细信息
	def OnClick(self, event):
		panel = event.GetEventObject()
		self.panel.Destroy()
		self.panel = self.modlepanel(self.days_data[self.panel_dict[id(panel)]])
		self.panel.Layout()
		self.panel.Refresh()
		self.panel.Update()
		self.sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL, 5)
		self.sizer.Layout()
		event.Skip()

	#鼠标移动到小模块，使该模块变蓝色
	def OnEnter(self, event):
		panel = event.GetEventObject()
		panel.SetBackgroundColour(wx.Colour(200, 220, 240))
		panel.Refresh()
		panel.Update()
		event.Skip()

	#鼠标离开小模块，使该模块变灰色，即原色
	def OnLeave(self, event):
		panel = event.GetEventObject()
		panel.SetBackgroundColour(wx.Colour(240, 240, 240))
		panel.Refresh()
		panel.Update()
		event.Skip()


#城市编辑窗口，用于编辑城市列表
class CityEditFrame(wx.Frame):
	def __init__(self, parent, title, size, city_list,comobox):
		wx.Frame.__init__(self, parent, title=title, size=size)
		self.city_list = city_list
		self.panel = wx.Panel(self)
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.comobox = comobox
        # 创建一个listbox，用于显示城市列表
		self.listbox = wx.ListBox(self.panel, -1, choices=city_list,size=(200,200),style=wx.LB_SINGLE)

        # 创建一个垂直布局，用于放置按钮
		self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 创建按钮，用于添加/删除/导入/导出城市
		if lan == 'cn':
			self.addbutton = wx.Button(self.panel, label='添加')
			self.delbutton = wx.Button(self.panel, label='删除')
			self.importbutton = wx.Button(self.panel, label='导入')
			self.exportbutton = wx.Button(self.panel, label='导出')
		elif lan == 'en':
			self.addbutton = wx.Button(self.panel, label='Add')
			self.delbutton = wx.Button(self.panel, label='Delete')
			self.importbutton = wx.Button(self.panel, label='Import')
			self.exportbutton = wx.Button(self.panel, label='Export')

		# 将按钮加入垂直布局
		self.vbox.Add(self.addbutton, 0, wx.ALL, 5)
		self.vbox.Add(self.delbutton, 0, wx.ALL, 5)
		self.vbox.Add(self.importbutton, 0, wx.ALL, 5)
		self.vbox.Add(self.exportbutton, 0, wx.ALL, 5)

		# 将listbox和垂直布局加入水平布局
		self.sizer.Add(self.listbox, 1, wx.ALL|wx.EXPAND, 5)
		self.sizer.Add(self.vbox, 0, wx.ALL|wx.EXPAND, 5)
		self.sizer.Layout()
		# 将水平布局加入panel
		self.panel.SetSizer(self.sizer)

		# 绑定按钮事件
		self.addbutton.Bind(wx.EVT_BUTTON, self.addcity)
		self.delbutton.Bind(wx.EVT_BUTTON, self.delcity)
		self.importbutton.Bind(wx.EVT_BUTTON, self.importcity)
		self.exportbutton.Bind(wx.EVT_BUTTON, self.exportcity)

	# 添加城市
	def addcity(self, event):
		if lan == 'cn':
			dialog = wx.TextEntryDialog(None, '请输入城市名称', '添加城市', '城市名称')
		elif lan == 'en':
			dialog = wx.TextEntryDialog(None, 'Please enter the city name', 'Add City', 'City Name')
		if dialog.ShowModal() == wx.ID_OK:
			cityname = dialog.GetValue()
			self.city_list.append(cityname)
			self.listbox.Append(cityname)
		global city_list
		city_list = self.city_list
		self.comobox.SetItems(city_list)
		dialog.Destroy()
		event.Skip()

	# 删除城市
	def delcity(self, event):
		selection = self.listbox.GetSelection()
		if selection != -1:
			self.city_list.pop(selection)
			self.listbox.Delete(selection)
		global city_list
		city_list = self.city_list
		self.comobox.SetItems(city_list)
		event.Skip()

	# 导入城市
	def importcity(self, event):
		if lan == 'cn':
			dialog = wx.FileDialog(None, '选择文件', os.getcwd(), '', '*.txt', wx.FD_OPEN)
		elif lan == 'en':
			dialog = wx.FileDialog(None, 'Select File', os.getcwd(), '', '*.txt', wx.FD_OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			filename = dialog.GetPath()
			self.listbox.Clear()
			self.city_list.clear()
			with open(filename, 'r') as f:
				for line in f.readlines():
					self.city_list.append(line.strip())
					self.listbox.Append(line.strip())
		global city_list
		city_list = self.city_list
		self.comobox.SetItems(city_list)
		dialog.Destroy()
		event.Skip()

	# 导出城市
	def exportcity(self, event):
		if lan == 'cn':
			dialog = wx.FileDialog(None, '选择文件', os.getcwd(), '', '*.txt', wx.FD_SAVE)
		elif lan == 'en':
			dialog = wx.FileDialog(None, 'Select File', os.getcwd(), '', '*.txt', wx.FD_SAVE)
		if dialog.ShowModal() == wx.ID_OK:
			filename = dialog.GetPath()
			with open(filename, 'w') as f:
				for city in self.city_list:
					f.write(city+'\n')
		dialog.Destroy()
		event.Skip()
	
        
# 主框架 放置工具栏和notebook
class appframe (wx.Frame):
	def __init__(self, parent):		
		wx.Frame.__init__ (self, parent,id = wx.ID_ANY, title = '天气预报', style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		self.SetSizeHints((800,600))

		#为方便布局，ribbonsizer作为一个单独sizer，放工具和notebook
		ribbonsizer = wx.BoxSizer(wx.VERTICAL)
		self.ribbon = rb.RibbonBar(self,wx.ID_ANY)
		self.report = rb.RibbonPage( self.ribbon,wx.ID_ANY )
		self.ribbon.SetActivePage( self.report ) 
		
		#创建panel，用于放置按钮和文字框，按钮用于搜索、切换城市，语言和刷新
		#先处理三个图标
		img1 = r'icons/refresh.png'
		self.bitmap1 = self.transfer(img1)
		img2 = r'icons/edit.png'
		self.bitmap2 = self.transfer(img2)
		img3 = r'icons/language.png'
		self.bitmap3 = self.transfer(img3)
		img4 = r'icons/search.png'
		self.bitmap4 = self.transfer(img4)

		#创建三个panel，用于放置三个按钮
		self.panel1 = rb.RibbonPanel( self.report,wx.ID_ANY ,"", wx.NullBitmap)
		self.buttonBar1 = rb.RibbonButtonBar( self.panel1)
		self.buttonBar1.AddSimpleButton(1, u"编辑城市",self.bitmap2 , "")
		self.Bind(rb.EVT_RIBBONBUTTONBAR_CLICKED, self.city_edit,id=1)

		self.panel2 = rb.RibbonPanel( self.report,wx.ID_ANY, "", wx.NullBitmap)
		self.buttonBar2 = rb.RibbonButtonBar( self.panel2)
		self.buttonBar2.AddSimpleButton(2, u"切换语言",self.bitmap3, "")
		self.Bind( rb.EVT_RIBBONBUTTONBAR_CLICKED, self.language_choose,id=2)

		self.panel3 = rb.RibbonPanel( self.report,wx.ID_ANY, "", wx.NullBitmap)
		self.buttonBar3 = rb.RibbonButtonBar( self.panel3)
		self.buttonBar3.AddSimpleButton(3 ,u"刷新数据",self.bitmap1, "")
		self.Bind( rb.EVT_RIBBONBUTTONBAR_CLICKED, self.refresh,id=3)

		#将ribbonbar加入ribbonsizer
		self.ribbon.Realize()
		ribbonsizer.Add( self.ribbon, 0, wx.EXPAND|wx.ALL, 0 )

		#添加一个水平布局，用于放comobox和搜索按钮，后续在这里可以增加扩展功能
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.combo = wx.ComboBox(self, wx.ID_ANY, choices=city_list, size= (270,22), style=wx.CB_DROPDOWN)
		self.combo.SetValue(city)
		font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)  # 创建一个新的字体，好调整大小
		self.combo.SetFont(font)  # 将新的字体设置为wx.ComboBox的字体

		searchbutton = wx.BitmapButton(self, 4, self.bitmap4)
		self.Bind(wx.EVT_BUTTON, self.getcity, searchbutton)
		hbox.Add(self.combo, 0,wx.ALL|wx.ALIGN_CENTER,5)
		hbox.Add(searchbutton, 0, wx.ALL|wx.ALIGN_CENTER,5)

		#将hbox加入ribbonsizer
		ribbonsizer.Add(hbox, 0, wx.EXPAND|wx.ALL, 0)

		#添加一个notebook，用于放置天气信息
		self.notebook = wx.aui.AuiNotebook( self, wx.ID_ANY,style = wx.aui.AUI_NB_TOP)
		
		#在notebook中添加两个页面，分别放实时天气和未来7天天气，为了方便调试，这两个页面的构造函数单独给出
		self.page1 = page1(self.notebook)
		self.page2 = page2(self.notebook)
		self.notebook.AddPage(self.page1, "实时天气")
		self.notebook.AddPage(self.page2, "未来7天天气")

		# 为页面加上图标
		self.icon1 = self.transfer('icons/hours.png')
		self.icon2 = self.transfer('icons/sevenday.png')
		self.notebook.SetPageBitmap(0, self.icon1)
		self.notebook.SetPageBitmap(1, self.icon2)
		ribbonsizer.Add( self.notebook, 1, wx.EXPAND|wx.ALL, 0 )
		self.SetSizer( ribbonsizer )

		# 设置窗口的背景颜色
		self.SetBackgroundColour(wx.Colour(240,240,240))  # 设置为兼容的灰色
		self.Layout()
		self.Centre( wx.BOTH )


	def __del__( self ):
		pass
				
	#将png文件转化成wxpython中的bitmap
	def transfer(self, img):
		img = wx.Image(img, wx.BITMAP_TYPE_ANY)
		pl_width = 20
		pl_height = 20
		img = img.Scale(int(pl_width), int(pl_height), wx.IMAGE_QUALITY_HIGH)
		return img.ConvertToBitmap()

	# 弹出一个窗口，显示其中的城市，从中选择一个，可以编辑添加删除城市，也可以导入或导出txt文件
	def city_edit( self, event ):
		global city_list
		global city
		global citycode
		# 创建一个CityEditFrame实例
		editframe = CityEditFrame(None, title='城市编辑', size=(300, 300), city_list=city_list, comobox=self.combo)
		editframe.Show()
		event.Skip()
	
	def getcity(self, event):
		global city
		global citycode
		global cityfullname
		inputcity = self.combo.GetValue()
		city_data = getmes.city_data(lan, inputcity)
		if city_data['code']=='200':
			city = city_data['location'][0]['adm2']+city_data['location'][0]['name']
			citycode = city_data['location'][0]['id']
			cityfullname = city_data['location'][0]['country']+city_data['location'][0]['adm1']+city_data['location'][0]['adm2']+city_data['location'][0]['name']
			#如果不在城市列表中，添加到列表中
			if city not in city_list:
				city_list.append(city)
		else:
			# print("没有找到匹配的城市数据请检查输入或api接口是否可用")
			if lan == 'cn':
				dlg = wx.MessageDialog(None, '没有找到匹配的城市数据\n请检查输入或api接口是否可用', '错误', wx.OK | wx.ICON_ERROR)
			elif lan == 'en':
				dlg = wx.MessageDialog(None, 'No matching city data found\nPlease check input or api', 'Error', wx.OK | wx.ICON_ERROR)  
			dlg.ShowModal()
			dlg.Destroy()
		self.combo.SetValue(city)
		self.combo.SetItems(city_list)
		self.refresh(event)
		event.Skip()

	#切换语言，目前支持中英文，弹出一个对话框，勾选语言
	def language_choose(self, event):
		lans = ['中文','English']
		global lan
		
		#检测目前语言lan，将对应选项勾选上
		if lan == 'cn':
			dialog = wx.SingleChoiceDialog(None, '请选择语言', '语言选择', lans)
			dialog.SetSelection(0)

		elif lan == 'en':
			dialog = wx.SingleChoiceDialog(None, 'Please choose a language', 'Language', lans)
			dialog.SetSelection(1)
		
		if dialog.ShowModal() == wx.ID_OK:
			choice = dialog.GetSelection()
			if choice == 0:
				lan = 'cn'
			elif choice == 1:
				lan = 'en'
		
		# 根据当前语言，删除按钮后重新加载
		self.buttonBar1.ClearButtons()
		self.buttonBar2.ClearButtons()
		self.buttonBar3.ClearButtons()
		if lan == 'cn':
			self.buttonBar1.AddSimpleButton(1, u"编辑城市",self.bitmap2 , "")
			self.buttonBar2.AddSimpleButton(2, u"切换语言",self.bitmap3, "")
			self.buttonBar3.AddSimpleButton(3 ,u"刷新数据",self.bitmap1, "")
		elif lan == 'en':
			self.buttonBar1.AddSimpleButton(1, u"Edit Citylist",self.bitmap2 , "")
			self.buttonBar2.AddSimpleButton(2, u"Switch Language",self.bitmap3, "")
			self.buttonBar3.AddSimpleButton(3 ,u"Refresh Data",self.bitmap1, "")
		self.refresh(event)
		self.ribbon.Realize()
		self.Layout()
		dialog.Destroy()
		event.Skip()

	#刷新数据，重新获取数据并重新显示，实际是移除page1和page2后再一次初始化，可以将鼠标变成加载状态
	def refresh( self, event ):
		self.notebook.DeletePage(0)
		self.notebook.DeletePage(0)
		self.page1 = page1(self.notebook)
		self.page2 = page2(self.notebook)
		if lan == 'cn':
			self.notebook.AddPage(self.page1, "实时天气")
			self.notebook.AddPage(self.page2, "未来7天天气")
		elif lan == 'en':
			self.notebook.AddPage(self.page1, "Realtime Weather")
			self.notebook.AddPage(self.page2, "7 Days Weather")
		self.notebook.SetPageBitmap(0, self.icon1)
		self.notebook.SetPageBitmap(1, self.icon2)
		self.Layout()
		event.Skip()
	
app = wx.App(False)
frame = appframe(None)
icon = wx.Icon('icons/app.png')
frame.SetIcon(icon)
frame.Show()
app.MainLoop()