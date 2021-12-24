'use strict'

import { app, protocol, BrowserWindow } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import { startServerUp, stopSever, sendMsg2Server } from './main/modules/clientConnect'
import { tcpRecvProcess } from './main/modules/clientRecvProcess'
import initIpcEvent from './main/modules/ipcEvent'
import { Window } from './main/modules/window'
const cmd = require('./main/modules/cmd')
const isDevelopment = process.env.NODE_ENV !== 'production'

// Scheme must be registered before the app is ready
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])

async function createWindow () {
  // // Create the browser window.
  // const win = new BrowserWindow({
  //   width: 800,
  //   height: 600,
  //   webPreferences: {

  //     // Use pluginOptions.nodeIntegration, leave this alone
  //     // See nklayman.github.io/vue-cli-plugin-electron-builder/guide/security.html#node-integration for more info
  //     nodeIntegration: process.env.ELECTRON_NODE_INTEGRATION,
  //     contextIsolation: !process.env.ELECTRON_NODE_INTEGRATION
  //   }
  // })
  // global.win = win
  // global.subWin = new Window()
  // global.subWin.listen()
  // global.subWin.createTray()
  const window = new Window()
  window.listen()
  window.createWindows({ isMainWin: true, width: 1200, height: 750 })
  window.createTray()
  global.win = window.main
  global.window = window

  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Load the url of the dev server if in development mode
    await global.win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    // 打开开发者工具
    if (!process.env.IS_TEST) global.win.webContents.openDevTools()
  } else {
    createProtocol('app')
    // Load the index.html when not in development
    global.win.loadURL('app://./index.html')
  }

  // 初始化进程之间事件监听
  initIpcEvent()
}

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
    console.log('quit')
    stopSever() // 关闭服务端
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', async () => {
  // 运行服务端
  startServerUp(tcpRecvProcess)
  // 创建窗口
  createWindow()
})

// Exit cleanly on request from parent process in development mode.
if (isDevelopment) {
  if (process.platform === 'win32') {
    process.on('message', (data) => {
      if (data === 'graceful-exit') {
        app.quit()
      }
    })
  } else {
    process.on('SIGTERM', () => {
      app.quit()
    })
  }
}
