const cmd = require('../main/modules/cmd')
const net = require('net')
const client = new net.Socket()
const PORT = 9998

function startServerUp (cb = undefined) {
  cmd.run_shell(['python', './backend/backend_up.py'])

  // 等待服务端起来1s后再连接
  setTimeout(() => {
    // client.setTimeout(1000) // 多久不活动将关闭连接
    client.connect(PORT, 'localhost')
    client.setEncoding('utf8')

    client.on('error', (e) => {
      console.log(e)
      setTimeout(() => {
        cmd.run_shell(['python', './backend/backend_up.py'])
        //   client.destroy()
        //   client.connect(PORT, 'localhost')
      }, 1000)
    })

    client.on('ready', () => {
      console.log('connect ok, server is up')
      sendMsg2Server(JSON.stringify({ msg: 'hello' }))
    })

    client.on('data', (data) => {
      console.log('on data: ' + data)
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

function sendMsg2Server (data) {
  if (client.readyState !== 'open') {
    console.log('server up fail')
    return false
  }
  console.log('client state: ' + client.readyState)
  console.log('client will send:' + data)
  client.write(data, 'utf8')
  return true
}

startServerUp()
