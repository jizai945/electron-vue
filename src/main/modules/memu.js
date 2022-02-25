// import { shell } from 'electron'
// import { Window } from './window'
export const memus = [
  {
    label: 'help',
    submenu: [
      {
        label: '版本',
        role: 'help',
        click: function () {
          // shell.openExternal('https://www.jianshu.com/u/1699a0673cfe')
          console.log('test')
          const args = {
            title: '版本',
            route: '/version',
            width: 800,
            height: 800,
            backgroundColor: '#f9f9f9',
            resizable: true,
            modal: true,
            maximize: false,
            autoHideMenuBar: true
          }
          global.window.createWindows(args)
        }
      }
    ]
  }
]
