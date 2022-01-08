<template>
  <el-container style="height:100%">
    <el-aside width="auto"><common-aside></common-aside></el-aside>
    <el-container>
      <!-- <el-header>
        <common-header></common-header>
      </el-header> -->
      <!-- <common-tag></common-tag> -->
        <el-main>
          <!-- keep alive 会缓存组件 -->
          <keep-alive><router-view v-if="$route.meta.keepAlive"></router-view></keep-alive>
          <!-- 不缓存的组件会被刷新 -->
          <router-view v-if="!$route.meta.keepAlive"></router-view>
        </el-main>
    </el-container>
  </el-container>
</template>

<script>
import CommonAside from '../components/CommonAside.vue'
// import CommonHeader from '../components/CommonHeader.vue'
// import CommonTag from '../components/CommonTag.vue'
// @ is an alias to /src

export default {
  name: 'Main',
  components: {
    CommonAside
    // CommonHeader,
    // CommonTag
  },
  data () {
    return {
      list: [
        'can-tool'
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.el-header{
  background: #6E7B8B;
}

.el-main {
  padding-top: 30px;
}
</style>
