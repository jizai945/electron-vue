<template>
  <el-row style="min-width:1000px">
    <!-- <el-card>
      <div>
        <i class="el-icon-s-tools"></i><span style="margin-left:10px;">CanOpen节点管理</span>
        <el-button type="success" style="float:right; margin-bottom:20px" @click="btnCanopenAddNode">添加canopen节点</el-button>
      </div>
    </el-card> -->
    <div>
        <!-- dialog -->
        <el-dialog title="节点配置" :visible.sync="dialogCanopenNodeVisible" :close-on-click-modal="false" style="min-width:1300px">
          <el-row >
            <el-col :span="4"><div style="margin-top:10px">节点ID(16进制): </div></el-col>
            <el-col :span="19" :offset="1"><div><el-input v-model="inputCanID" placeholder="请输入内容节点ID 0x00"></el-input></div></el-col>
            <el-col :span="20" style="margin-top:10px"><div><el-input v-model="inputEdsFile" readonly placeholder="请选择eds文件"></el-input></div></el-col>
            <el-col :span="3" :offset="1" style="margin-top:10px"><div><el-button type="primary" style="float: right" @click="btnChoiceEds">选择eds</el-button></div></el-col>
            <el-col :span="4" :offset="10" style="margin-top:20px"><div><el-button type="primary" style="float: right" @click="btnNodeSure">确认</el-button></div></el-col>
          </el-row>
        </el-dialog>
      </div>

    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span style="color:#666699; margin-left: 20px">canopen节点详细信息</span>
        <el-button size="small" style="float: right; margin-bottom:10px" :class="zoom(desShow)" @click="desShow=!desShow"></el-button>
      </div>
      <div v-if="desShow">
        <el-col :span="24" style="margin-top:10px; margin-bottom:20px">
          <u-table :data="canopenTable" :border="true" stripe style="width: 100%">
            <u-table-column type="index" label="number" width="80"></u-table-column>
            <u-table-column prop="canid" label="节点ID" width="180"></u-table-column>
            <u-table-column prop="eds" label="eds载入文件"> </u-table-column>
            <u-table-column fixed="right" label="操作" width="120">
              <template slot-scope="scope">
                <el-button @click="rowDialogClick(scope.row)" type="text" size="small">节点视图</el-button>
                <el-button @click="rowDeleteClick(scope.row)" type="text" size="small" style="color: red">删除</el-button>
              </template>
            </u-table-column>
          </u-table>
        </el-col>
      </div>
    </el-card>

    <el-card class="box-card" >
      <!-- <div @contextmenu="showContextMenu">右键点击此区域</div> -->
      <div slot="header" class="clearfix">
        <i style="margin-left: 0px" :class="iconClass"></i>
        <span style="color:#666699;margin-left: 10px">节点数据</span>
      </div>
      <el-row >
        <el-col :span="4">
          <el-tree :data="canTree" :props="defaultProps" @node-click="handleNodeClick" @node-contextmenu="showContextMenu" @contextmenu="showContextMenu"></el-tree>
          <context-menu class="right-menu"
              :target="contextMenuTarget"
              :show="contextMenuVisible"
              @update:show="(show) => contextMenuVisible = show">
            <a href="javascript:;" @click="rightMenuAddNode">添加节点</a>
            <a href="javascript:;" @click="rightMenuDelNode(rightNodeCache)">删除节点</a>
          </context-menu>
          <context-menu class="blank-right-menu"
              :target="contextMenuTargetBlank"
              :show="contextMenuBlankVisible"
              @update:show="(show) => contextMenuBlankVisible = show">
            <a href="javascript:;" @click="rightMenuAddNode">添加节点</a>
          </context-menu>
        </el-col>
        <el-col :span="20">
          <el-tabs v-model="editableTabsValue" :tab-position="tabPosition" @edit="handleTabsEdit">
            <template v-for="(item) in editableTabs">
              <el-tab-pane
                :key="item.name"
                v-if="odOnlineShow(item.title)"
                :label="item.title"
                :name="item.name">
                <el-row >
                  <el-col :span="18"><span style="color:#666699; margin-left: 50px">{{item.content}}</span></el-col>
                  <el-col :span="6"></el-col>
                  <!-- 只要在u-table元素中定义了height属性，即可实现固定表头的表格，而不需要额外的代码。 -->
                  <el-col :span="24">
                    <u-table ref="canTable" class="tableBox" max-height="600" :data="item.table" :border="true"
                    :pagination-show="true" :total="item.pageForm.total" :page-size.sync="item.pageForm.pageSize" :current-page.sync="item.pageForm.currentPage"
                    @handlePageSize="handlePageSize"  @current-change="handleCurrentChange" @size-change="handleSizeChange" :page-sizes="[100, 200, 300, 400, 1000, 2000]">
                      <u-table-column prop="index" label="索引" width="100"></u-table-column>
                      <u-table-column prop="subIndex" label="子索引" width="100"></u-table-column>
                      <u-table-column prop="name" label="名称"></u-table-column>
                      <u-table-column prop="size" label="数据范围" width="80"></u-table-column>
                      <u-table-column prop="data" label="数据" width="100"> </u-table-column>
                      <u-table-column prop="explain" label="说明"> </u-table-column>
                    </u-table>
                  </el-col>
                </el-row>
              </el-tab-pane>
              <!-- <el-tab-pane label="0x06-odOnline" :key="item.name">0x06-odOnline</el-tab-pane> -->
            </template>
          </el-tabs>
        </el-col>
      </el-row>
    </el-card>
  </el-row>
</template>

<script>
import { ipcRenderer } from 'electron'
import { windowCreate, windowCloseRoute } from '../../main/modules/windowApi'
const { dialog } = require('electron').remote
const canopenRouteHead = '/CanopenSub'
var fs = require('fs')
var ini = require('ini')
export default {
  data: function () {
    return {
      iconClass: 'el-icon-s-flag',
      dialogCanopenNodeVisible: false,
      inputCanID: '',
      inputEdsFile: '',
      canopenDrawer: false,
      checkedCanopenID: [],
      canidManger: {}, // canid管理, 格式  {id: {eds: path}}
      isIndeterminate: true,
      checkAll: false,
      config: {},
      canopenTable: [],
      tabPosition: 'top',
      editableTabsValue: '2',
      editableTabs: [], // title | name | content | table []
      allTableCache: { currentId: undefined }, // 保存所有节点的tabs信息
      canTree: [],
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      treeClickCount: 0,
      desShow: false,
      contextMenuTarget: null,
      contextMenuVisible: false,
      contextMenuTargetBlank: document.body,
      contextMenuBlankVisible: false,
      rightNodeCache: undefined,
      contextMenuOffset: {
        left: 0,
        top: 0
      }
    }
  },
  methods: {
    // 获取文件名
    getFileName (path) {
      var pos1 = path.lastIndexOf('/')
      var pos2 = path.lastIndexOf('\\')
      var pos = Math.max(pos1, pos2)
      if (pos < 0) { return path } else { return path.substring(pos + 1) }
    },
    // 添加节点按钮事件
    btnCanopenAddNode () {
      if (this.$store.state.canBtnStr !== '关闭') {
        this.$notify.error({
          title: '无法添加',
          message: '请先打开can口',
          position: 'bottom-left'
        })
        return
      }

      this.dialogCanopenNodeVisible = true
    },
    // 选择eds文件
    btnChoiceEds () {
      dialog.showOpenDialog({
        title: '请选择你的文件',
        defaultPath: '%userprofile%/Desktop', // 默认打开的文件路径选择
        filters: [{ // 过滤掉你不需要的文件格式
          name: 'eds',
          extensions: ['eds']
        }]
      }).then(res => {
        // console.log(res)
        if (res.filePaths[0] !== '') {
          this.inputEdsFile = res.filePaths[0]
        }
      }).catch(req => {
        console.log(req)
      })
    },
    // node节点确认
    btnNodeSure () {
      if (this.inputCanID === '' || this.inputEdsFile === '') {
        this.$notify.warning({
          title: '警告',
          message: '节点ID和eds文件不能为空',
          position: 'bottom-left'
        })
        return
      }
      this.dialogCanopenNodeVisible = false

      const id = this.hex2int(this.inputCanID)
      this.deleteAllById(id)
      this.addById(id)
    },
    // 节点子窗口
    rowDialogClick (row) {
      // row.canid row.eds
      windowCreate({
        title: canopenRouteHead,
        route: canopenRouteHead + '?id=' + this.hex2int(row.canid) + '&eds=' + row.eds,
        width: 1000,
        height: 750,
        backgroundColor: '#f9f9f9',
        resizable: true,
        modal: true,
        maximize: false,
        autoHideMenuBar: true
      })
    },
    // 刷新canopen的节点管理表格
    canopenTableViewFresh () {
      this.canopenTable.splice(0, this.canopenTable.length) // 清空数组
      for (var id in this.canidManger) {
        this.canopenTable.push({ canid: this.int2hex(Number(id)), eds: this.canidManger[id].eds })
      }
    },
    // 获取idx描述名
    getIdxParam (idx) {
      var lab = ' '
      if (this.config[idx] && this.config[idx].ParameterName !== undefined) {
        lab = this.config[idx].ParameterName
      }
      return lab
    },
    // 获取idx的 数据类型
    getIdxDataType (idx) {
      var dat = ' '
      if (this.config[idx] && this.config[idx].DataType !== undefined) {
        dat = this.config[idx].DataType
      }
      return dat
    },
    // 获取idx的参数权限
    getIdxAccessType (idx) {
      var acc = ' '
      if (this.config[idx] && this.config[idx].AccessType !== undefined) {
        acc = this.config[idx].AccessType
      }
      return acc
    },
    // 分析eds文件节点信息
    // config: eds文件经过ini解析后的对象
    // subSection: 要解析的片段
    // table: 保存的对象
    edsFileAnalysis (config, subSection, table) {
      // console.log(config)
      for (var key in subSection) {
        if (key === 'SupportedObjects') {
          continue
        }
        const idx = subSection[key].substring(2) // 去掉0x
        table.push({
          index: idx,
          subIndex: '',
          name: this.getIdxParam(idx),
          size: this.getIdxDataType(idx),
          data: '',
          explain: this.getIdxAccessType(idx)
        })
        if (config[idx] && 'SubNumber' in config[idx] && this.hex2int(config[idx].SubNumber) > 0) {
          var childNum = this.hex2int(config[idx].SubNumber)
          for (var i = 0; i < childNum; i++) {
            const subIdx = idx + 'sub' + i
            if (subIdx in config) {
              table.push({
                index: idx,
                subIndex: i,
                name: this.getIdxParam(subIdx),
                size: this.getIdxDataType(subIdx),
                data: '',
                explain: this.getIdxAccessType(subIdx)
              })
            }
          }
        }
      }
    },
    // 通过id增加节点
    addById (id) {
      const idLabel = 'id: 0x' + this.int2hex(id)
      ipcRenderer.send('canopen2main', { msg: 'canopen add node', node: id, eds: this.inputEdsFile })
      this.canidManger[id] = { eds: this.inputEdsFile }
      var subCfg = { label: idLabel, children: [], id: id }

      // 加载ini
      this.config = ini.parse(fs.readFileSync(this.inputEdsFile, 'utf-8'))
      subCfg.ini = this.config
      // console.log(subCfg)

      this.iconClass = 'el-icon-loading' // 图标改成加载中
      setTimeout(() => {
        this.canTree.push(subCfg) // tree添加
        // tabs title | name | content | table []
        const newTabName = id + ''
        var subTabs = {
          title: idLabel,
          name: newTabName,
          content: idLabel + ' --- ' + this.getFileName(this.inputEdsFile)
        }
        subTabs.table = []
        subTabs.tableCache = []
        this.edsFileAnalysis(subCfg.ini, subCfg.ini.MandatoryObjects, subTabs.tableCache)
        this.edsFileAnalysis(subCfg.ini, subCfg.ini.OptionalObjects, subTabs.tableCache)
        this.edsFileAnalysis(subCfg.ini, subCfg.ini.ManufacturerObjects, subTabs.tableCache)
        subTabs.pageForm = {}
        subTabs.pageForm.total = subTabs.tableCache.length
        subTabs.pageForm.pageSize = 100
        subTabs.pageForm.currentPage = 1
        const start = (subTabs.pageForm.currentPage - 1) * 100
        subTabs.table = subTabs.tableCache.slice(start, start + 100)
        // this.editableTabs.push(subTabs)
        this.editableTabsValue = newTabName
        this.allTableCache[id] = { tabs: [], currentTab: newTabName }
        this.allTableCache[id].tabs.push(subTabs)
        this.allTableCache.currentId = id
        this.editableTabs = this.allTableCache[id].tabs

        this.iconClass = 'el-icon-s-tools' // 图标恢复
      }, 100)
    },
    // 通过id删除节点
    deleteAllById (id) {
      if (this.canidManger[id] !== undefined) {
        ipcRenderer.send('canopen2main', { msg: 'canopen remove node', node: id })
        const route = canopenRouteHead + '?id=' + id + '&eds=' + this.canidManger[id].eds
        windowCloseRoute(route) // 关闭之前的窗口
        delete this.canidManger[id]

        // 删除tree中的旧节点
        this.canTree.forEach((tr, index) => {
          if (tr.id === id) {
            this.canTree.splice(index, 1)
          }
        })

        // 删除tabs
        if (this.allTableCache.currentId === id) {
          var nextID = -1
          Object.keys(this.allTableCache).forEach(function (key) {
            // id
            if (typeof (key) === typeof (1) && key !== id) {
              nextID = id
            }
          })
          this.allTableCache.currentId = nextID
        }
        delete this.allTableCache.id
        if (this.allTableCache.currentId && this.allTableCache.currentId > 0) {
          const showId = this.allTableCache.currentId
          this.editableTabs = this.allTableCache[showId].tabs
          this.editableTabsValue = this.allTableCache[showId].currentTab
        }

        // const targetName = id + ''
        // const tabs = this.editableTabs
        // let activeName = this.editableTabsValue
        // if (activeName === targetName) {
        //   tabs.forEach((tab, index) => {
        //     if (tab.name === targetName) {
        //       const nextTab = tabs[index + 1] || tabs[index - 1]
        //       if (nextTab) {
        //         activeName = nextTab.name
        //       }
        //     }
        //   })
        // }
        // this.editableTabsValue = activeName
        // this.editableTabs = tabs.filter(tab => tab.name !== targetName)
      }
      this.canopenTableViewFresh()
    },
    // 节点删除
    rowDeleteClick (row) {
      // row.canid row.eds
      const id = this.hex2int(row.canid)
      this.deleteAllById(id)
    },
    // 树节点点击事件
    handleNodeClick (data) {
      // 记录点击次数
      this.treeClickCount++
      // 单次点击次数超过2次不作处理,直接返回,也可以拓展成多击事件
      if (this.treeClickCount >= 2) {
        return
      }
      // 计时器,计算300毫秒为单位,可自行修改 实现双击事件
      this.timer = window.setTimeout(() => {
        if (this.treeClickCount === 1) {
          // 把次数归零
          this.treeClickCount = 0
          // 单击事件处理
          console.log(data.id + ' 单击事件,可在此处理对应逻辑')
        } else if (this.treeClickCount > 1) {
          // 把次数归零
          this.treeClickCount = 0
          // 双击事件
          console.log(data.id + ' 双击事件,可在此处理对应逻辑')
          // this.editableTabsValue = data.id + ''
          if (this.allTableCache.currentId === data.id) {
            console.log('id 相同，无需切换')
            this.editableTabs[0].pageForm.currentPage++
            return
          }
          console.log(this.allTableCache.currentId)
          console.log(this.editableTabs)
          this.allTableCache[this.allTableCache.currentId].tabs = this.editableTabs
          this.allTableCache.currentId = data.id
          this.editableTabs = this.allTableCache[data.id].tabs
          this.editableTabsValue = this.allTableCache[data.id].currentTab
        }
      }, 300)

      // console.log(data)
    },
    handleTabsEdit (targetName, action) {
      if (action === 'add') {
        this.btnCanopenAddNode()
      }
      if (action === 'remove') {
        const tabs = this.editableTabs
        let activeName = this.editableTabsValue
        if (activeName === targetName) {
          tabs.forEach((tab, index) => {
            if (tab.name === targetName) {
              const nextTab = tabs[index + 1] || tabs[index - 1]
              if (nextTab) {
                activeName = nextTab.name
              }
            }
          })
        }

        this.editableTabsValue = activeName
        this.editableTabs = tabs.filter(tab => tab.name !== targetName) // 删除
      }
    },
    // 分页事件
    handlePageSize ({ page, size }) {
      // console.log(page, size)
      this.editableTabs.forEach((tr, index) => {
        if (tr.name === this.editableTabsValue) {
          const start = (page - 1) * size
          tr.table = tr.tableCache.slice(start, start + size)
        }
      })
      // subTabs.table = subTabs.tableCache.slice(start, start + 100)
    },
    handleCurrentChange (val) {
      console.log(`当前页: ${val}`)
    },
    handleSizeChange (val) {
      console.log(`每页 ${val} 条`)
    },
    // 当前页变化
    currentPageChange (val) {
      console.log(val)
      // console.log(size)
    },
    createDatabaseOrTable () {
      this.contextMenuVisible = false
      console.log('create ')
    },
    // 缩放图标切换
    zoom (state) {
      if (state) {
        return 'el-icon-minus'
      }
      return 'el-icon-plus'
    },
    // 是否显示od onlie
    odOnlineShow (name) {
      console.log(name)
      return name.indexOf('0x') !== -1
      // return name.indexOf('odOnline') !== -1
    },
    // 右键显示
    showContextMenu (e, data, node) {
      e.preventDefault()
      this.rightNodeCache = { data: data, node: node }
      this.contextMenuVisible = true
      // console.log('showContextMenu', data, node)
      // console.log('0', e, '1', e.screenX, '2', e.screenY)
      // console.log(e.pageX, e.pageY)
      // this.contextMenuOffset = {
      //   left: e.pageX,
      //   top: e.pageY
      // }
    },
    // 右键菜单添加节点
    rightMenuAddNode () {
      this.contextMenuVisible = false
      this.btnCanopenAddNode()
    },
    // 右键菜单删除节点
    rightMenuDelNode (nodeCache) {
      this.contextMenuVisible = false
      console.log(nodeCache)
      console.log('删除节点:' + nodeCache.data.id)
      this.deleteAllById(nodeCache.data.id)
    },
    testAddEdsFile (ID, file) {
      this.inputCanID = ID
      this.inputEdsFile = file
      this.dialogCanopenNodeVisible = false
      const id = this.hex2int(this.inputCanID)
      this.deleteAllById(id)
      this.addById(id)
    }
  },
  mounted () {
    // -------------------------------- for test -------------------------------------------
    this.testAddEdsFile('0x06', 'C:\\Users\\Wang\\Desktop\\e35-pudu.eds')
    window.setInterval(() => {
      for (var i = 0; i < this.editableTabs.length; i++) {
        console.log(this.editableTabs[0].pageForm.currentPage)
      }
    }, 1000)
    // ---------------------------------------------------------------------------------------

    ipcRenderer.on('main2can', (event, arg) => {
      switch (arg.msg) {
        case 'canopen add node res':
          this.$notify({
            title: '添加节点: ' + arg.id,
            message: arg.result === true ? '添加成功' : '添加失败: ' + arg.describe,
            type: arg.result === true ? 'success' : 'error',
            position: 'bottom-left'
          })

          if (arg.result === false) {
            // 删除该节点管理
            if (this.canidManger[arg.id] !== undefined) {
              delete this.canidManger[arg.id]
            }
          }
          this.canopenTableViewFresh()
          break
        // 请求打开端口反馈 （如果是重新打开can则把载入的eds节点重新添加上）
        case 'req port open res':
          if (arg.result === true) {
            for (var id in this.canidManger) {
              ipcRenderer.send('canopen2main', { msg: 'canopen add node', node: this.hex2int(id), eds: this.canidManger[id].eds })
            }
          }
          break
      }
    })
  },
  destroyed () {
    // 销毁的事情要记得
    ipcRenderer.removeAllListeners() // ！！！
  }
}
</script>

<style>
.el-card {
  margin-top: 20px;
}
.u-table {
  margin-top: 20px;
}

.right-menu {
  font-size: 14px;
  position: fixed;
  background: #fff;
  border: solid 1px rgba(0, 0, 0, .2);
  border-radius: 3px;
  z-index: 999;
  display: none;
}
.right-menu a {
  width: 150px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  display: block;
  color: #1a1a1a;
}
.right-menu a:hover {
  background: #eee;
  color: #fff;
}
.right-menu {
    border: 1px solid #eee;
    box-shadow: 0 0.5em 1em 0 rgba(0,0,0,.1);
    border-radius: 1px;
}
a {
    text-decoration: none;
}
.right-menu a {
    padding: 2px;
}
.right-menu a:hover {
    background: #99A9BF;
}

.blank-right-menu {
  font-size: 14px;
  position: fixed;
  background: #fff;
  border: solid 1px rgba(0, 0, 0, .2);
  border-radius: 3px;
  z-index: 999;
  display: none;
}
.blank-right-menu a {
  width: 150px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  display: block;
  color: #1a1a1a;
}
.blank-right-menu a:hover {
  background: #eee;
  color: #fff;
}
.blank-right-menu {
    border: 1px solid #eee;
    box-shadow: 0 0.5em 1em 0 rgba(0,0,0,.1);
    border-radius: 1px;
}
a {
    text-decoration: none;
}
.blank-right-menu a {
    padding: 2px;
}
.blank-right-menu a:hover {
    background: #99A9BF;
}
</style>
