'use strict'

// eslint-disable-next-line no-unused-vars
import Vue from 'vue'
import axios from 'axios'
import config from '../config/index'

// 设置配置 根据开发 和 生产环境不一样
const baseUrl = process.env.NODE_ENV === 'development' ? config.baseUrl.dev : config.baseUrl.pro

class HttpRequest {
  constructor (baseUrl) {
    this.baseUrl = baseUrl
  }

  getInsideConfig () {
    const config = {
      baseURL: this.baseUrl,
      header: {

      }
    }
    return config
  }

  interceptors (instance) {
    // 添加请求拦截器
    instance.interceptors.request.use(function (config) {
      // 在发送请求之前做些什么
      console.log('拦截处理请求')
      return config
    }, function (error) {
      // 对请求错误做些什么
      return Promise.reject(error)
    })

    // 添加响应拦截器
    instance.interceptors.response.use(function (response) {
      console.log('数据响应')
      // 对响应数据做点什么
      return response.data
    }, function (error) {
      console.log('公共错误做处理')
      console.log(error)
      // 对响应错误做点什么
      return Promise.reject(error)
    })
  }

  request (options) {
    // 请求
    // api/getList  /api/getHome
    const instance = axios.create()
    // 技巧 用户传递过来的option可以拼接上 this.getInsideConfig()
    options = { ...(this.getInsideConfig()), ...options }
    this.interceptors(instance)
    return instance(options)
  }
}

export default new HttpRequest(baseUrl)
