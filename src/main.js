import Vue from 'vue'
import './plugins/axios'
import App from './App.vue'
// import './registerServiceWorker' // 缓存机制 打包出问题
import router from './router'
import store from './store'
import './plugins/element.js'
import './plugins/umy.js'
import './plugins/wechatTitle.js'
// import './plugins/sortable.js'

Vue.config.productionTip = false

if (process.env.NODE_ENV === 'development') {
  require('@/api/mock')
} else {
  require('@/api/mock')
}

// 自定义16进制转10进制方法
Vue.prototype.hex2int = function (hex) {
  hex = hex.replace('0x', '')
  hex = hex.replace(' ', '')
  var len = hex.length; var a = new Array(len); var code
  for (var i = 0; i < len; i++) {
    code = hex.charCodeAt(i)
    if (code >= 48 && code < 58) {
      code -= 48
    } else {
      code = (code & 0xdf) - 65 + 10
    }
    a[i] = code
  }

  return a.reduce(function (acc, c) {
    acc = 16 * acc + c
    return acc
  }, 0)
}

// 10进制数转16进制字符串
Vue.prototype.int2hex = function (num) {
  return '0x' + num.toString(16)
}

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
