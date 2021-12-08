export default {
  state: {
    isCollapse: false,
    currentMenu: null,
    tabList: [
      {
        path: '/',
        name: 'home',
        label: '首页',
        icon: 'home'
      }
    ]
  },
  mutations: {
    collapseMenu (state) {
      state.isCollapse = !state.isCollapse
    },
    selectMenu (state, val) {
      // val.name === 'home' ? (state.currentMenu = null) : state.currentMenu = val

      if (val.name === 'home') {
        state.currentMenu = null
      } else {
        state.currentMenu = val
        // 新增tabList
        const result = state.tabList.findIndex(item => item.name === val.name)
        // eslint-disable-next-line no-unused-expressions
        result === -1 ? state.tabList.push(val) : ''
      }
    },
    closeTag (state, val) {
      const result = state.tabList.findIndex(item => item.name === val.name)
      state.tabList.splice(result, 1)
    }
  }
}
