var canFrameBuf = { msg: 'can frame buff', f: [], id: [], t: [] }
var canTimer = false
var lastStr = ''

function canpBuffSend () {
  if (canFrameBuf.f.length !== 0) {
    global.win.webContents.send('main2can', canFrameBuf)
    canFrameBuf.f = []
    canFrameBuf.id = []
    canFrameBuf.t = []
  }
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
