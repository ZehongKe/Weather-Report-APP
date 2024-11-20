# Weather-Forecasting-App
Weather forecasting software based on Wafeng Weather api
## 项目简介

本项目是一个基于Python开发的天气预报应用，旨在为用户提供便捷的城市天气查询服务。通过集成和风天气API，实现了实时天气、未来天气预报等功能，并提供了多语言支持、城市管理和数据刷新等实用特性。
## Demo Video

<video width="600" controls>
  <source src="https://github.com/ZehongKe/Weather-Report-APP/blob/main/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
[![项目视频](https://github.com/ZehongKe/Weather-Report-APP/blob/main/icons/900-fill.png](https://www.bilibili.com/video/BV133SKYeE4K/)

## 依赖库
```bash
pip install cairosvg
pip install lxml
pip install wxPython
pip install matplotlib
pip install requests
```

## 使用说明
- **启动应用**：运行 `main.py` 文件，启动天气预报应用。
- **查询天气**：在搜索栏中输入城市名或从下拉列表中选择，点击搜索按钮查询天气。
- **编辑城市**：点击工具栏上的“编辑城市”按钮，弹出编辑窗口进行城市管理。
- **切换语言**：点击工具栏上的“切换语言”按钮，选择所需的显示语言。
- **刷新数据**：点击工具栏上的“数据更新”按钮，手动刷新天气数据。
## 功能介绍

### API接口选择
项目选择了和风天气的API服务，因其功能全面且支持免费使用的预警信息、多语言请求等服务，满足了项目的需求。

### 系统设计架构
- **工具栏**：包含城市编辑、语言切换、数据更新和城市搜索功能，方便用户操作。
- **内容页**：分为实时天气页和未来天气页，展示当前及未来天气情况。

### 实时天气页
- **布局**：页面采用竖直布局，从上至下分别为时间城市信息、实时天气信息和天气趋势图。
- **实时天气**：左侧显示最重要的天气信息，右侧则通过小模块展示其他信息，预警信息使用嵌入式滚动窗口呈现。
- **天气趋势**：使用notebook组件展示不同的折线图，支持鼠标悬停显示详细信息。

### 未来天气页
- **布局**：同样采用竖直布局，展示未来7天的天气信息。
- **小卡片**：每张小卡片展示一天的天气概况，点击卡片可展开查看更详细的信息。
- **交互**：支持鼠标悬停变色，增强用户体验。

### 工具栏功能
- **城市编辑**：允许用户批量管理城市列表，包括添加、删除、导入、导出等操作。
- **语言切换**：用户可以选择界面显示语言，当前支持中文和英文。
- **数据更新**：手动刷新数据，确保天气信息的实时性。
- **城市搜索**：支持用户通过模糊搜索或选择默认城市列表来查询天气。

## 技术栈
- **编程语言**：Python
- **GUI框架**：wxPython
- **图表库**：Matplotlib
- **API库**：requests
- **其他**：cairosvg, xml, os, datetime, wx.lib.agw.ribbon, wx.lib.wordwrap
## 注意事项
- 本应用默认语言为中文，城市为北京海淀区和广州白云区。
- 用户可以根据需要修改全局变量或直接编辑 `city_list.txt` 文件来添加或删除城市。
- 部分图标资源来自和风天气提供及阿里图标库。



感谢您使用本天气预报应用！希望它能为您的生活带来便利。
