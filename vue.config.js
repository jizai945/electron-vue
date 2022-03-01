module.exports = {
  pluginOptions: {
    electronBuilder: {
      nodeIntegration: true,
      builderOptions: {
        nsis: {
          allowToChangeInstallationDirectory: true,
          oneClick: false
        },
        win: {
          icon: './public/icon/icon.ico'
        },
        mac: {
          icon: './public/icon/icon.icns'
        },
        extraFiles: [
          {
            from: './backend/dist', // 项目资源
            to: './backend/dist'// 打包后输出到的按照目录资源
          },
          {
            from: './update.json', // 项目资源
            to: './'// 打包后输出到的按照目录资源
          }
        ],
        productName: 'pudu-can-tool'
      }
    }
  }
}
