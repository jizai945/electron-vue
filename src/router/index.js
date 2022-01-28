import Vue from 'vue'
import VueRouter from 'vue-router'
import Main from '../views/Main.vue'

const originPush = VueRouter.prototype.push
VueRouter.prototype.push = function push (location) {
  return originPush.call(this, location).catch(err => err)
}
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Main',
    component: Main,
    children: [
      {
        path: '/',
        name: 'can-tool',
        component: () => import('@/views/Can/Can-Tool'),
        meta: {
          keepAlive: true
        }
      },
      {
        path: '/',
        name: 'canopen',
        component: () => import('@/views/Can/Canopen'),
        meta: {
          keepAlive: true
        }
      },
      {
        path: '/test',
        name: 'home',
        component: () => import('@/views/Home/Home'),
        meta: {
          keepAlive: true
        }
      },
      {
        path: '/message',
        name: 'message',
        component: () => import('@/views/Message/Message'),
        meta: {
          keepAlive: true
        }
      }
    ]
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About')
  },
  {
    path: '/canopenSub',
    name: 'CanopenSub',
    component: () => import('@/views/Can/CanopenSub'),
    meta: {
      title: '标题'
    }
  }
]

const router = new VueRouter({
  // mode: 'history',
  mode: 'hash',
  base: process.env.BASE_URL,
  routes
})

export default router
