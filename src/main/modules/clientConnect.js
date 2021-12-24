// 本文件作用
// 1. 运行服务端(并进行消息接收回调)
// 2. 发消息给服务端
const cmd = require('./cmd')
const net = require('net')
const cmdList = (process.env.NODE_ENV === 'development') ? ['python', './backend/backend_up.py'] : ['./backend/dist/backend_up.exe']
const PORT = 9998
const client = new net.Socket()
const TCPEND = '|END' // TCP结束符
var restartTime

// console.log(cmd)
function startServerUp (cb = undefined) {
  // client.setTimeout(1000) // 多久不活动将关闭连接

  cmd.run_shell(cmdList)
  // 等待服务端起来1s后再连接
  setTimeout(() => {
    client.connect(PORT, 'localhost')
    client.setEncoding('utf8')

    client.on('error', (e) => {
      console.log(e)
      restartTime = setTimeout(() => {
        cmd.run_shell(cmdList)
      }, 1000)
    })

    client.on('ready', () => {
      try {
        clearTimeout(restartTime)
      } catch (err) {
        console.log(err)
      }
      console.log('connect ok, server is up')
      sendMsg2Server(JSON.stringify({ msg: 'hello' }))
    })

    client.on('data', (data) => {
      // console.log('on data: ' + data)
      if (cb !== undefined) {
        cb(data)
      }
    })

    client.on('close', (data) => {
      console.log('client on close: ' + data)
      setTimeout(() => {
        client.destroy()
        client.connect(PORT, 'localhost')
      }, 1000)
    })
  }, 1000)
}

function stopSever () {
  client.on('error', (e) => {
  })

  client.on('ready', () => {
  })

  client.on('data', (data) => {
  })

  client.on('close', (data) => {
  })

  client.write('exit', 'utf8')
}

// 该函数会在数据尾部增加结束符
function sendMsg2Server (data) {
  if (client.readyState !== 'open') {
    console.log('server up fail')
    return false
  }

  console.log('client state: ' + client.readyState)
  console.log('client will send:' + data)
  client.write(data + TCPEND, 'utf8')
  return true
}

// startServerUp()
export { startServerUp, stopSever, sendMsg2Server }
