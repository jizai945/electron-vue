import Vue from 'vue'
import Vuex from 'vuex'
import tab from './tab'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    canBtnStr: '打开'
  },
  mutations: {
  },
  actions: {
  },
  modules: {
    tab
  }
})
