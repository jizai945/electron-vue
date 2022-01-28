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
          <el-table :data="canopenTable" :border="true" stripe style="width: 100%">
            <el-table-column type="index" label="number" width="80"></el-table-column>
            <el-table-column prop="canid" label="节点ID" width="180"></el-table-column>
            <el-table-column prop="eds" label="eds载入文件"> </el-table-column>
            <el-table-column fixed="right" label="操作" width="120">
              <template slot-scope="scope">
                <el-button @click="rowDialogClick(scope.row)" type="text" size="small">节点视图</el-button>
                <el-button @click="rowDeleteClick(scope.row)" type="text" size="small" style="color: red">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </div>
    </el-card>

    <el-card class="box-card" >
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
        <!-- 详情dialog -->
        <el-dialog title="详情" :visible.sync="idsDataVisible" style="min-width:1300px; margin-top:0px;">
           <el-table :data="dialogDetailsData" max-height="400" border style="width: 100%" :row-style="iRowStyle" :cell-style="iCellStyle">
            <el-table-column prop="key" label="key" width="180"></el-table-column>
            <el-table-column prop="value" label="value"></el-table-column>
          </el-table>
        </el-dialog>
        <el-col :span="20">
          <el-tabs v-model="editableTabsValue" :tab-position="tabPosition" @edit="handleTabsEdit" :before-leave='leaveTab'>
            <template v-for="(item) in editableTabs">
              <!-- table -->
              <el-tab-pane v-if="item.type=== tabType.table" :key="item.name" :label="item.title" :name="item.name">
                <el-row >
                  <el-col :span="6"></el-col>
                  <!-- 只要在el-table元素中定义了height属性，即可实现固定表头的表格，而不需要额外的代码。 -->
                  <el-col :span="24">
                    <el-switch
                      @change="updateChange(item.switch, item.name)"
                      v-model="item.switch"
                      :active-value="true"
                      :inactive-value="false"
                      active-text="开"
                      inactive-text="自动更新:关">
                    </el-switch>
                    <el-table ref="canTable" class="tableBox" max-height="600" :data="item.table" :border="true">
                      <el-table-column prop="Index" label="索引" width="100"></el-table-column>
                      <el-table-column prop="SubIndex" label="子索引" width="100"></el-table-column>
                      <el-table-column prop="ParameterName" label="名称"></el-table-column>
                      <el-table-column prop="Data" label="数据" width="100"> </el-table-column>
                      <el-table-column prop="DataType" label="数据类型" width="80"></el-table-column>
                      <el-table-column prop="ObjectType" label="对象类型" width="80"></el-table-column>
                      <el-table-column prop="AccessType" label="属性"> </el-table-column>
                      <el-table-column fixed="right" label="操作" width="120">
                        <template slot-scope="scope">
                          <el-tooltip class="item" effect="dark" placement="left-end">
                            <div slot="content">
                              <ul>
                                <li v-for="(item, index) in scope.row" :key="item.Index"> {{index}} : {{item}} </li>
                              </ul>
                            </div>
                            <el-button @click="rowEdsDataDttails(scope.row)" type="text" size="small" style="color: #8B658B;">详情</el-button>
                          </el-tooltip>
                          <el-button @click="rowEdsDataUpdata(scope.row)" type="text" size="small">更新</el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                    <el-pagination @size-change="handleSizeChange(item)"
                                  @current-change="handleCurrentChange(item)"
                                  :current-page.sync="item.pageForm.currentPage"
                                  :page-sizes="[100, 200, 300, 400, 1000, 2000]"
                                  :page-size.sync="item.pageForm.pageSize"
                                  :total="item.pageForm.total"
                                  layout="total, sizes, prev, pager, next, jumper">
                    </el-pagination>
                  </el-col>
                </el-row>
              </el-tab-pane>
              <!-- card -->
              <el-tab-pane v-if="item.type=== tabType.edsCard" :key="item.name" :label="item.title" :name="item.name">
                <el-card class="box-card">
                <span>EDS文件信息</span>
                <div>
                  <el-descriptions class="margin-top" :column="3" size="small" border>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-files"></i>文件名</template>{{item.card.edsFileName}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-film"></i>版本</template>{{item.card.edsFileVersion}}
                    </el-descriptions-item>
                    <el-descriptions-item><template slot="label"><i class="el-icon-collection-tag"></i>子版本</template>{{item.card.edsFileRevision}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-notebook-1"></i>EDS版本</template>{{item.card.edsEDSVersion}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-chat-dot-round"></i>描述</template>{{item.card.edsDescription}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i></i></template>
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-time"></i>创建时间</template>{{item.card.edsCreationTime}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-date"></i>创建日期</template>{{item.card.edsCreationDate}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-user"></i>创建者</template>{{item.card.edsCreatedBy}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-time"></i>修改时间</template>{{item.card.edsModificationTime}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-date"></i>修改日期</template>{{item.card.edsModificationDate}}
                    </el-descriptions-item>
                    <el-descriptions-item>
                      <template slot="label"><i class="el-icon-user-solid"></i>修改者</template>{{item.card.edsModifiedBy}}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-card>
              </el-tab-pane>

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
      idsDataVisible: false,
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
      editableTabs: [], // title: | name: | table:[] cacheTable:[] / card:{} | type: 类型(表明当前标签页内容)
      allTableCache: { currentId: undefined }, // 保存所有节点的tabs信息
      canTree: [],
      defaultProps: { children: 'children', label: 'label' },
      treeClickCount: 0,
      desShow: false,
      contextMenuTarget: null,
      contextMenuVisible: false,
      contextMenuTargetBlank: document.body,
      contextMenuBlankVisible: false,
      rightNodeCache: undefined,
      tabType: { table: 0, edsCard: 1 },
      dialogDetailsData: [{ key: '111', value: '2222' }], // key:xx  value:xx
      DataTypeMap: {
        0x01: 'BOOLEAN',
        0x02: 'INTEGER8',
        0x03: 'INTEGER16',
        0x04: 'INTEGER32',
        0x05: 'UNSIGNED8',
        0x06: 'UNSIGNED16',
        0x07: 'UNSIGNED32',
        0x08: 'REAL32',
        0x09: 'VISIBLE_STRING',
        0x0A: 'OCTET_STRING',
        0x0B: 'UNICODE_STRING',
        0x0C: 'UNICODE_STRING',
        0x0D: 'TIME_DIFFERENCE'
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
    // 根据 eds 的 section key 获取 value
    getValueFromEdsIdxKey (idx, key) {
      var value = ''
      if (this.config[idx] && this.config[idx][key] !== undefined) {
        value = this.config[idx][key]
      }
      return value
    },
    // 构建idx对象属性
    getIdxObj (idx) {
      var idxStr = ''; var subIdxStr = ''
      const pos = idx.indexOf('sub')
      if (pos !== -1) {
        idxStr = idx.substr(0, pos)
        subIdxStr = idx.substr(pos + 3)
      } else {
        idxStr = idx
      }
      return {
        Index: idxStr,
        SubIndex: subIdxStr,
        ParameterName: this.getValueFromEdsIdxKey(idx, 'ParameterName'),
        DataType: this.getValueFromEdsIdxKey(idx, 'DataType'), // 数据类型
        Data: '',
        AccessType: this.getValueFromEdsIdxKey(idx, 'AccessType'), // 读写权限
        PDOMapping: this.getValueFromEdsIdxKey(idx, 'PDOMapping'), // 是否被pdo映射
        ObjectType: this.getValueFromEdsIdxKey(idx, 'ObjectType'), // 对象类型
        ObjFlags: this.getValueFromEdsIdxKey(idx, 'ObjFlags'),
        DefaultValue: this.getValueFromEdsIdxKey(idx, 'DefaultValue')
      }
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

        table.push(this.getIdxObj(idx))
        if (config[idx] && 'SubNumber' in config[idx] && this.hex2int(config[idx].SubNumber) > 0) {
          var childNum = this.hex2int(config[idx].SubNumber)
          for (var i = 0; i < childNum; i++) {
            const subIdx = idx + 'sub' + i
            if (subIdx in config) {
              table.push(this.getIdxObj(subIdx))
            }
          }
        }
      }
    },
    // 通过id增加节点
    addById (id) {
      const idLabel = 'id: ' + this.int2hex(id)
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
        // tabs title | name | table []
        // add table
        const newTabName = id + ''
        var subTabs = {
          title: idLabel,
          name: newTabName,
          type: this.tabType.table
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
        this.allTableCache[id] = { tabs: [], currentTab: newTabName }
        this.allTableCache[id].tabs.push(subTabs)
        this.allTableCache.currentId = id
        this.editableTabs = this.allTableCache[id].tabs
        this.editableTabsValue = newTabName

        // add card
        subTabs = {
          title: 'edsInfo',
          name: 'edsInfo' + id,
          type: this.tabType.edsCard
        }
        subTabs.card = {
          edsFileName: '',
          edsFileVersion: '',
          edsFileRevision: '',
          edsEDSVersion: '',
          edsDescription: '',
          edsCreationTime: '',
          edsCreationDate: '',
          edsCreatedBy: '',
          edsModificationTime: '',
          edsModificationDate: '',
          edsModifiedBy: ''
        }
        if (subCfg.ini.FileInfo.FileRevision) subTabs.card.edsFileName = subCfg.ini.FileInfo.FileName
        if (subCfg.ini.FileInfo.FileRevision) subTabs.card.edsFileVersion = subCfg.ini.FileInfo.FileVersion
        if (subCfg.ini.FileInfo.FileRevision) subTabs.card.edsFileRevision = subCfg.ini.FileInfo.FileRevision
        if (subCfg.ini.FileInfo.EDSVersion) subTabs.card.edsEDSVersion = subCfg.ini.FileInfo.EDSVersion
        if (subCfg.ini.FileInfo.Description) subTabs.card.edsDescription = subCfg.ini.FileInfo.Description
        if (subCfg.ini.FileInfo.CreationTime) subTabs.card.edsCreationTime = subCfg.ini.FileInfo.CreationTime
        if (subCfg.ini.FileInfo.CreationDate) subTabs.card.edsCreationDate = subCfg.ini.FileInfo.CreationDate
        if (subCfg.ini.FileInfo.CreatedBy) subTabs.card.edsCreatedBy = subCfg.ini.FileInfo.CreatedBy
        if (subCfg.ini.FileInfo.ModificationTime) subTabs.card.edsModificationTime = subCfg.ini.FileInfo.ModificationTime
        if (subCfg.ini.FileInfo.ModificationDate) subTabs.card.edsModificationDate = subCfg.ini.FileInfo.ModificationDate
        if (subCfg.ini.FileInfo.ModifiedBy) subTabs.card.edsModifiedBy = subCfg.ini.FileInfo.ModifiedBy
        this.allTableCache[id].tabs.push(subTabs)

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
          console.log('删除显示节点')
          var nextID = -1
          Object.keys(this.allTableCache).forEach(function (key) {
            // id
            if (key !== 'currentId' && parseInt(key) !== id) {
              console.log(key, id)
              nextID = parseInt(key)
            }
          })
          this.allTableCache.currentId = nextID
          console.log('显示节点:' + this.allTableCache.currentId)
        }
        delete this.allTableCache[id]
        console.log(this.allTableCache)
        if (this.allTableCache.currentId && this.allTableCache.currentId > 0) {
          const showId = this.allTableCache.currentId
          this.editableTabs = this.allTableCache[showId].tabs
          this.editableTabsValue = this.allTableCache[showId].currentTab
        } else {
          this.editableTabs = []
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
    // 自动更新改变
    updateChange (state, name) {
      // console.log(this.allTableCache)
      var id = parseInt(name)
      if (state) {
        console.log('打开 id: ' + id + 'sdo更新')
      } else {
        console.log('关闭 id: ' + id + 'sdo更新')
      }
      ipcRenderer.send('canopen2main', {
        msg: 'canopen auto sdo',
        id: id,
        state: state ? 'open' : 'close'
      })
    },
    // 更新
    rowEdsDataUpdata (row) {
      const canID = this.allTableCache.currentId
      const index = row.Index
      const subIndex = row.SubIndex
      ipcRenderer.send('canopen2main', { msg: 'canopen read sdo', id: canID, idx: index, subIdx: subIndex })
      // console.log(row)
    },
    // 详情
    rowEdsDataDttails (row) {
      // console.log(row)
      this.dialogDetailsData = []
      for (const key in row) {
        this.dialogDetailsData.push({ key: key, value: row[key] })
        // console.log(key, ':', row[key])
      }
      this.idsDataVisible = true
    },
    // 详情悬浮
    dttailsTollTipShow (row) {
      return 'test'
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
    // 当前页改变
    handleCurrentChange (item) {
      const size = item.pageForm.pageSize
      const start = (item.pageForm.currentPage - 1) * size
      item.table = item.tableCache.slice(start, start + size)
    },
    // 页大小改变
    handleSizeChange (item) {
      this.handleCurrentChange(item)
    },
    createDatabaseOrTable () {
      this.contextMenuVisible = false
      console.log('create ')
    },
    // 标签tabs切换
    leaveTab (activeName, oldActiveName) {
      console.log(activeName, oldActiveName)
      this.allTableCache[this.allTableCache.currentId].currentTab = activeName
    },
    // 缩放图标切换
    zoom (state) {
      if (state) {
        return 'el-icon-minus'
      }
      return 'el-icon-plus'
    },
    // 右键显示
    showContextMenu (e, data, node) {
      e.preventDefault()
      this.rightNodeCache = { data: data, node: node }
      this.contextMenuVisible = true
      // console.log('showContextMenu', data, node)
      // console.log('0', e, '1', e.screenX, '2', e.screenY)
      // console.log(e.pageX, e.pageY)
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
    iRowStyle: function ({ row, rowIndex }) {
      return 'height:35px'
    },
    iCellStyle: function ({ row, column, rowIndex, columnIndex }) {
      return 'padding:3px'
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
    // this.testAddEdsFile('0x07', 'C:\\Users\\Wang\\Desktop\\demo.eds')
    // window.setInterval(() => {
    //   for (var i = 0; i < this.editableTabs.length; i++) {
    //     console.log(this.editableTabs[0].pageForm.currentPage)
    //   }
    // }, 1000)
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
          } else {
            // 如果是重新打开的节点，恢复自动更新开关状态
            if (this.allTableCache[arg.id]) {
              ipcRenderer.send('canopen2main', {
                msg: 'canopen auto sdo',
                id: arg.id,
                state: this.allTableCache[arg.id].tabs[0].switch ? 'open' : 'close'
              })
            }

            // if (this.allTableCache[arg.id]) {
            //   this.allTableCache[arg.id].tabs[0].switch = false
            // }
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
        // 读取sdo应答
        case 'canopen read sdo res':
          if (arg.result !== true) {
            this.$message({
              dangerouslyUseHTMLString: true,
              type: 'error',
              duration: 3000,
              showClose: true,
              message: '<i>读取sdo, id:' + arg.id + ' idx: ' + arg.idx + ' subIdx: ' + arg.subIdx + '失败</i>' + '<br><i>' + arg.describe + '</i>'
            })
          }
          break
        // 切换自动sdo状态
        case 'canopen auto sdo res':
          this.$notify({
            title: (arg.state === 'open' ? '打开 ' : '关闭') + 'canid: ' + arg.id + 'sdo',
            message: arg.result === true ? '成功' : '失败: ' + arg.describe,
            type: arg.result === true ? 'success' : 'error',
            position: 'bottom-left'
          })
          // 如果失败，把状态改变回来
          console.log(this.allTableCache)
          if (this.allTableCache[arg.id] && !arg.result) {
            this.allTableCache[arg.id].tabs[0].switch = (arg.state !== 'open')
          }
          console.log(this.allTableCache)
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
.el-table {
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
