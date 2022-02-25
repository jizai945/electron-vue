<template>
<el-menu
    class="leftMenu"
    :collapse="isCollapse"
    background-color="#ffffff"
    text-color="#000000"
    active-text-color="#00BFFF"
    default-active="/can"
    :active="menuActive"
    ref="leftMenu"
>
  <h3 v-show="!isCollapse">Can-Tool</h3>
  <h3 v-show="isCollapse" >Can</h3>
  <el-button v-show="isCollapse" plain icon="el-icon-menu" size="mini" @click="handleMenu" style="display:block;margin:0 auto"></el-button>
  <el-button v-show="!isCollapse" plain icon="el-icon-menu" size="mini" @click="handleMenu" style="display:block;margin:0 auto;width: 80%;"></el-button>
  <div style="margin-top:10px"></div>
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
      menuActive: '/can',
      menu: [
        {
          path: '/can',
          name: 'can-tool',
          label: 'can工具',
          icon: 's-tools',
          url: 'Can/Can-Tool'
        },
        {
          path: '/canopen',
          name: 'canopen',
          label: 'canopen',
          icon: 'set-up',
          url: 'Can/Canopen'
        },
        {
          path: '/eds2c',
          name: 'eds2c',
          label: 'EDS转C',
          icon: 'orange',
          url: 'Can/CanopenEds2C'
        },
        {
          path: '/mucpack',
          name: 'mcupack',
          label: 'mcu固件打包',
          icon: 'folder',
          url: 'McuPack/Pack'
        }
        // {
        //   path: '/',
        //   name: 'home',
        //   label: '测试',
        //   icon: 's-home',
        //   url: 'Home/Home'
        // },
        // {
        //   label: '其他',
        //   icon: 'location',
        //   children: [
        //     {
        //       path: '/page1',
        //       name: 'page1',
        //       label: '页面1',
        //       icon: 'setting',
        //       url: 'Other/PageOne'
        //     },
        //     {
        //       path: '/page2',
        //       name: 'page2',
        //       label: '页面2',
        //       icon: 'setting',
        //       url: 'Other/PageTwo'
        //     }
        //   ]
        // },
        // {
        //   path: '/message',
        //   name: 'message',
        //   label: '消息盒子',
        //   icon: 'bell',
        //   url: 'Message/Message'
        // }
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
    // 页面加载好后执行

  },
  watch: {
    // canTableData () {
    //   this.$nextTick(() => {
    //     console.log(this.$refs.canTable)
    //     // this.$refs.canTable.bodyWrapper.scrollTop = this.$refs.canTable.bodyWrapper.scrollHeight
    //   })
    // }
    '$store.state.tab.currentMenu' (val) {
      this.$refs.leftMenu.activeIndex = val
    }
  }
}
</script>

<style lang="scss" scoped>
.el-menu {
  min-height: 100vh;
  height: 100%;
  border: none;
  h3 {
    color: #000000;
    text-align: center;
    line-height: 48px;
  }
}
.leftMenu:not(.el-menu--collapse) {
  width: 150px;
  min-height: 100%;
  height: 200vh;
}
</style>
