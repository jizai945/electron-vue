export default {
  state: {
    isCollapse: true, // true隐藏  false展开
    currentMenu: null,
    tabList: [
      {
        path: '/can',
        name: 'can-tool',
        label: 'CAN',
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
      state.currentMenu = val.path
      // 新增tabList
      const result = state.tabList.findIndex(item => item.name === val.name)
      // eslint-disable-next-line no-unused-expressions
      result === -1 ? state.tabList.push(val) : ''
    },
    closeTag (state, val) {
      const result = state.tabList.findIndex(item => item.name === val.name)
      state.tabList.splice(result, 1)
    }
  }
}
