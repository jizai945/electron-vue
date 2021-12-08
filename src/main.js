import Vue from 'vue'
import './plugins/axios'
import App from './App.vue'
// import './registerServiceWorker' // 缓存机制 打包出问题
import router from './router'
import store from './store'
import './plugins/element.js'

Vue.config.productionTip = false

if (process.env.NODE_ENV === 'development') {
  require('@/api/mock')
} else {
  require('@/api/mock')
}

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
