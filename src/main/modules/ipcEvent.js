/* eslint-disable camelcase */
// 本文件作用
// 1. electron主进程消息监听
import { ipcMain } from 'electron'
import { sendMsg2Server } from './clientConnect'

export default function () {
  ipcMain.on('can2main', (event, arg) => {
    const json_str = JSON.stringify(arg)
    console.log('ipcmain[can->main]: ' + json_str)
    switch (arg.msg) {
      // 这里做分支是为了以后需要特殊处理做预留
      case 'fresh port':
      case 'req port open':
      case 'req port close':
        sendMsg2Server(json_str)
        break
      default:
        sendMsg2Server(json_str)
        break
    }
  })
  ipcMain.on('canopen2main', (event, arg) => {
    const json_str = JSON.stringify(arg)
    console.log('ipcmain[canopen->main]: ' + json_str)
    switch (arg.msg) {
      default:
        sendMsg2Server(json_str)
        break
    }
  })
  ipcMain.on('canopenSub2main', (event, arg) => {
    const json_str = JSON.stringify(arg)
    console.log('ipcmain[canopenSub->main]: ' + json_str)
    switch (arg.msg) {
      default:
        sendMsg2Server(json_str)
        break
    }
  })
  ipcMain.on('pack2main', (event, arg) => {
    const json_str = JSON.stringify(arg)
    console.log('ipcmain[pack->main]: ' + json_str)
    switch (arg.msg) {
      default:
        sendMsg2Server(json_str)
        break
    }
  })
  ipcMain.on('edsconvert2main', (event, arg) => {
    const json_str = JSON.stringify(arg)
    console.log('ipcmain[edsconvert->main]: ' + json_str)
    switch (arg.msg) {
      default:
        sendMsg2Server(json_str)
        break
    }
  })
}
