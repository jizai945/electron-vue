# pudu-can-tool

## 环境安装

+ 客户端安装nodejs: 参考 [Node.js 安装配置 | 菜鸟教程 (runoob.com)](https://www.runoob.com/nodejs/nodejs-install-setup.html)
+ 修改npm源, 执行命令`npm config set registry http://registry.npm.taobao.org/`
+ 全局安装yarn: 执行命令`npm install -g yarn`
+ 全局安装vue-cli： 执行命令`npm install -g @vue/cli`
+ 全局安装electron: 执行命令`npm install electron -g`
+ 服务端安装python环境： [Download Python | Python.org](https://www.python.org/downloads/)
+ 修改pip源: 参考[Python更改pip源 - Seven丨Pounds - 博客园 (cnblogs.com)](https://www.cnblogs.com/zhx-blog/p/11619809.html)



## 安装工程需要的包

+ 客户端: `yarn install`
+ 服务端: `cd backend`      `pip install -r pipEnv.txt`



## 开发环境调试/热重启

+ 运行客户端:`yarn run electron:serve`
+ 重启服务端(默认客户端起来后会拉起服务端，这条命令可用于单独重启服务端):`python backed_up.py`



## 构建/发布

+ 运行脚本： `webpack.bat`， 没有yarn环境可以把脚本中的yarn改成npm



## 版本升级

版本升级需要修改两个文件:

+ 文件`package.json` 修改version字段为升级后的版本
+ 文件`update.json`描述版本更新内容



## 开发需求

+ can数据收发和展示  √
+ canopen协议栈移植  √
+ canopensdo数据收发  √
+ canopen pdo数据收发  ❌
+ mcu固件打包  √
+ eds文件转c文件  √❌ (有bug)
