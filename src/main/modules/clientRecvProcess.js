import { getQueryVariableFromStr } from './util'
var canFrameBuf = { msg: 'can frame buff', f: [], id: [], t: [] }
var canTimer = false
var lastStr = ''
var canopenWinMap = new Map()

function canpBuffSend () {
  if (canFrameBuf.f.length !== 0) {
    global.win.webContents.send('main2can', canFrameBuf)
    canFrameBuf.f = []
    canFrameBuf.id = []
    canFrameBuf.t = []
  }
}

function findCanoIDWind (id) {
  for (var i in global.window.group) {
    var canID = decodeURIComponent(getQueryVariableFromStr(global.window.group[i].route, 'id'))
    if (parseInt(canID) === id) {
      canopenWinMap.set(id, global.window.group[i].win)
      return true
    }
  }
  return false
}

function tcpRecvSubProcess (recvJson) {
  if (recvJson !== undefined) {
    switch (recvJson.msg) {
      case 'fresh port res': // 端口刷新
      case 'can err': // 出错通知
        global.win.webContents.send('main2can', recvJson)
        break
      case 'req port open res':
        if (recvJson.result === true) {
          if (canTimer !== false) {
            clearInterval(canTimer)
            canTimer = false
          }
          canTimer = setInterval(canpBuffSend, 300)
        }
        global.win.webContents.send('main2can', recvJson)
        break
      case 'can frame':
        canFrameBuf.f.push(recvJson.frame)
        canFrameBuf.id.push(recvJson.canid)
        canFrameBuf.t.push(recvJson.time)
        // global.win.webContents.send('main2can', recvJson)
        break
      case 'canopen add node res': // canopen添加节点
        global.win.webContents.send('main2can', recvJson)
        break
      case 'canopen upload start res': // 升级结果
        // 查找一下 map中对应canid的子窗口是否存在
        var id = recvJson.id
        if (!canopenWinMap.has(id)) {
          if (findCanoIDWind(id) === false) break // 窗口查找失败，建立map映射失败
        }

        try {
          canopenWinMap.get(id).webContents.send('main2canopenSub', recvJson)
        } catch (err) {
          if (err.message === 'Object has been destroyed') {
            // 删除原来map
            canopenWinMap.delete(id)
            // 重新查找窗口
            findCanoIDWind(id)
          }
          try {
            canopenWinMap.get(id).webContents.send('main2canopenSub', recvJson)
          } catch (err) {
            console.log(err)
          }
        }

        break
    }
  }
}

function tcpRecvProcess (recv) {
  // 太长不显示
  if (recv.length < 256) {
    console.log('[client]:py -> js: ' + recv)
  } else {
    console.log('[client]:py -> js, length: ' + recv.length)
  }
  var recvList = (lastStr + recv).split('|END') // 分包
  lastStr = ''
  for (var sub of recvList) {
    if (sub === '') continue
    try {
      const recvJson = JSON.parse(sub)
      tcpRecvSubProcess(recvJson)
    } catch (err) {
      lastStr = sub
    }
  }
}

export { tcpRecvProcess }
