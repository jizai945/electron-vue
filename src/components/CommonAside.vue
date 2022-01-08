<template>
<el-menu
    class="el-menu-vertical-demo"
    :collapse="isCollapse"
    background-color="#6E7B8B"
    text-color="#fff"
    active-text-color="#ffd04b"
>
  <h3 v-show="!isCollapse">Can-Tool</h3>
  <h3 v-show="isCollapse" >Can</h3>
  <el-button v-show="isCollapse" plain icon="el-icon-menu" size="mini" @click="handleMenu" style="display:block;margin:0 auto"></el-button>
  <el-button v-show="!isCollapse" plain icon="el-icon-menu" size="mini" @click="handleMenu" style="display:block;margin:0 auto;width: 80%;"></el-button>
    <el-menu-item
      :index="item.path"
      v-for="item in noChildren"
      :key="item.path"
      @click="clickMenu(item)"
      ref="commonAside"
    >
    <i :class="'el-icon-'+item.icon"></i>
    <span slot="title">{{item.label}}</span>
  </el-menu-item>
  <el-submenu :index="item.label" v-for="item in hasChildren" :key="item.path">
    <template slot="title">
      <i :class="'el-icon-'+item.icon"></i>
      <span slot="title">{{item.label}}</span>
    </template>
    <el-menu-item-group>
      <el-menu-item
        :index="subItem.path"
        v-for="(subItem, subIndex) in item.children"
        :key="subIndex"
        >
        <i :class="'el-icon-'+subItem.icon"></i>
        <span slot="title">{{subItem.label}}</span>
        </el-menu-item>
    </el-menu-item-group>
  </el-submenu>

</el-menu>
</template>

<script>
export default {
  data () {
    return {
      menu: [
        {
          path: '/can',
          name: 'can-tool',
          label: 'can工具',
          icon: 'paperclip',
          url: 'Can/Can-Tool'
        },
        {
          path: '/canopen',
          name: 'canopen',
          label: 'canopen',
          icon: 'star-off',
          url: 'Can/Canopen'
        },
        {
          path: '/',
          name: 'home',
          label: '测试',
          icon: 's-home',
          url: 'Home/Home'
        },
        {
          label: '其他',
          icon: 'location',
          children: [
            {
              path: '/page1',
              name: 'page1',
              label: '页面1',
              icon: 'setting',
              url: 'Other/PageOne'
            },
            {
              path: '/page2',
              name: 'page2',
              label: '页面2',
              icon: 'setting',
              url: 'Other/PageTwo'
            }
          ]
        }
      ]
    }
  },
  methods: {
    // handleOpen(key, keyPath) {
    //   console.log(key, keyPath);
    // },
    // handleClose(key, keyPath) {
    //   console.log(key, keyPath);
    // },
    clickMenu (item) {
      this.$router.push({ name: item.name })
      this.$store.commit('selectMenu', item)
    },
    handleMenu () {
      this.$store.commit('collapseMenu')
    }
  },
  computed: {
    noChildren () {
      return this.menu.filter((item) => !item.children)
    },
    hasChildren () {
      return this.menu.filter((item) => item.children)
    },
    isCollapse () {
      return this.$store.state.tab.isCollapse
    }
  },
  mounted () {

  }
}
</script>

<style lang="scss" scoped>
.el-menu {
  height: 100vh;
  border: none;
  h3 {
    color: #ffffff;
    text-align: center;
    line-height: 48px;
  }
}
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 100%;
  height: 100vh;
}
</style>
