<template>
  <div class="canopen" v-wechat-title="title">
    <el-row style="min-width:1000px">
      <el-col :span="22" :offset="1">
        <el-card class="box-card">
          <span>EDS文件信息</span>
          <el-button size="small" style="float: right; margin-bottom:10px" :class="zoom(desShow)" @click="desShow=!desShow"></el-button>
          <div v-if="desShow">
            <el-descriptions class="margin-top" :column="3" size="small" border>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-files"></i>文件名</template>{{edsFileName}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-film"></i>版本</template>{{edsFileVersion}}
              </el-descriptions-item>
              <el-descriptions-item><template slot="label"><i class="el-icon-collection-tag"></i>子版本</template>{{edsFileRevision}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-notebook-1"></i>EDS版本</template>{{edsEDSVersion}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-chat-dot-round"></i>描述</template>{{edsDescription}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i></i></template>
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-time"></i>创建时间</template>{{edsCreationTime}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-date"></i>创建日期</template>{{edsCreationDate}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-user"></i>创建者</template>{{edsCreatedBy}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-time"></i>修改时间</template>{{edsModificationTime}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-date"></i>修改日期</template>{{edsModificationDate}}
              </el-descriptions-item>
              <el-descriptions-item>
                <template slot="label"><i class="el-icon-user-solid"></i>修改者</template>{{edsModifiedBy}}
              </el-descriptions-item>
            </el-descriptions>
          </div>

        </el-card>
      </el-col>
      <el-col :span="22" :offset="1">
        <el-card class="box-card">
          <el-row>
            <el-col :span="16" ><el-input placeholder="输入关键字进行过滤" size="mid" v-model="filterText"></el-input></el-col>
            <el-col :span="2"><el-button type="success" style="float: right" size="mid" @click="btnNodeExpand(pdoData)">展开</el-button></el-col>
            <el-col :span="2"><el-button type="warning" style="float: right" size="mid" @click="btnNodeShrink(pdoData)">折叠</el-button></el-col>
            <el-col :span="2" :offset="2"><el-button size="small" style="float: right" :class="zoom(treeShow)" @click="treeShow=!treeShow"></el-button></el-col>
          </el-row>

          <div v-if="treeShow">
            <el-divider></el-divider>
            <el-col :span="22" :offset="1" style="margin-top:20px">
              <!-- <el-card class="box-card"> -->
                <div class="custom-tree-container">
                  <div class="tree" :style="treeHeight">
                    <!-- show-checkbox -->
                    <el-tree
                      class="filter-tree"
                      :data="pdoData"
                      :props="defaultProps"
                      :filter-node-method="filterNode"
                      :default-expand-all=false
                      @check-change="handleCheckChange"
                      :render-content="renderContent"
                      :expand-on-click-node="false"
                      node-key="id"
                      ref="pdoTree">
                    </el-tree>
                  </div>
                </div>
              <!-- </el-card> -->
            </el-col>
          </div>
        </el-card>
      </el-col>

      <el-col :span="22" :offset="1">
        <el-card class="box-card">
          <el-row>
            <el-col :span="3"><el-button type="danger" size="small" @click="btnNodeClear()">清空监视</el-button></el-col>
            <el-col :span="2" :offset="19"><el-button style="float: right;" size="small" :class="zoom(tableShow)" @click="tableShow=!tableShow"></el-button></el-col>
            <div v-if="tableShow">
              <el-col :span="24" style="margin-top:5px;">
                <el-divider></el-divider>
                <u-table :data="canopenTable" :border="true" :maxHeight="tableheight" row-key="id" stripe>
                  <u-table-column prop="tableIdex" label="Idex" width="90" fixed="left" sortable></u-table-column>
                  <u-table-column prop="tableValue" label="Value" width="150"> </u-table-column>
                  <u-table-column prop="tableParameterName" label="ParameterName" width="150"></u-table-column>
                  <u-table-column prop="tableAccessType" label="AccessType" width="150" sortable></u-table-column>
                  <u-table-column prop="tableObjectType" label="ObjectType" width="150"> </u-table-column>
                  <u-table-column prop="tableDataType" label="DataType" width="150"> </u-table-column>
                  <u-table-column prop="tableDefaultValue" label="DefaultValue" width="150"> </u-table-column>
                  <u-table-column fixed="right" label="操作" width="50">
                      <template slot-scope="scope">
                        <el-button @click="canopnIdcRemoveClick(scope.$index, scope.row)" type="text" size="small">删除</el-button>
                      </template>
                    </u-table-column>
                </u-table>
              </el-col>
            </div>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="22" :offset="1">
        <el-card class="box-card">
          <el-row>
            <el-col :span="4"><span> 升级功能</span></el-col>
            <el-col :span="2" :offset="18"><el-button style="float: right;" size="small" :class="zoom(uploadShow)" @click="uploadShow=!uploadShow"></el-button></el-col>
            <div v-if="uploadShow" style="margin-top:50px">
              <el-col :span="16"><el-input placeholder="文件路径" v-model="uploadInput" :disabled="true"></el-input></el-col>
              <el-col :span="3" :offset="1"><el-button style="width:100%" type="primary" @click="chioceUploadFile">选择升级文件</el-button></el-col>
              <el-col :span="2" :offset="1"><el-button type="success" @click="uploadStart" :disabled="uploadDisabled">开始升级</el-button></el-col>
              <el-col :span="24" style="margin-top:20px">
                <el-input>
                  id="uploadId"
                  type="upload"
                  :rows=logRows
                  readonly
                  show-word-limi
                  placeholder="日志"
                  v-model="textarea">
                </el-input>
              </el-col>
            </div>

          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import { getQueryVariable } from '../../main/modules/util'
import { ipcRenderer } from 'electron'
const { dialog } = require('electron').remote
// import Sortable from 'sortablejs'
var fs = require('fs')
var ini = require('ini')
export default {
  data: function () {
    return {
      canID: 0,
      edsPath: '',
      desShow: false,
      treeShow: true,
      tableShow: true,
      uploadShow: true,
      uploadDisabled: false,
      title: 'test',
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
      edsModifiedBy: '',
      filterText: '',
      uploadInput: '',
      currentID: 1,
      config: {},
      pdoData: [],
      defaultProps: {
        children: 'children', // 指定子树为节点对象的某个属性值
        label: 'label' // 指定节点标签为节点对象的某个属性值
      },
      canopenTable: [],
      tableheight: ((window.innerHeight + 100) * 0.5), // 参考 https://blog.csdn.net/weixin_43852094/article/details/112390905?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~aggregatepage~first_rank_ecpm_v1~rank_v31_ecpm-1-112390905.pc_agg_new_rank&utm_term=%E5%89%8D%E7%AB%AF%E8%8E%B7%E5%8F%96%E9%A1%B5%E9%9D%A2%E9%AB%98%E5%BA%A6&spm=1000.2123.3001.4430
      treeHeight: { maxHeight: ((window.innerHeight + 100) * 0.5) + 'px' },
      sdoFreshTimer: undefined
    }
  },
  watch: {
    filterText (val) {
      if (this.treeShow) {
        this.$refs.pdoTree.filter(val)
      }
    }
  },
  methods: {
    filterNode (value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },
    // 缩放图标切换
    zoom (state) {
      if (state) {
        return 'el-icon-minus'
      }
      return 'el-icon-plus'
    },
    // 监视按钮
    watchIdx (data) {
      // console.log(data)
      // todo 这里把idx 添加到监视定时器中
      if (data.children && data.children.length > 0) {
        data.children.forEach((chl) => {
          this.watchIdx(chl)
        })
        return
      }

      var exitFlag = false
      this.canopenTable.forEach((sub) => {
        if (sub.tableIdex === data.idx) {
          exitFlag = true
        }
      })

      if (exitFlag) {
        // 已添加过监视了
        return
      }

      this.canopenTable.push({
        tableIdex: data.idx,
        tableValue: '',
        tableParameterName: this.getIdxParam(data.idx),
        tableAccessType: this.getIdxAccessType(data.idx),
        tableObjectType: this.getIdxObjectType(data.idx),
        tableDataType: this.getIdxDataType(data.idx),
        tableDefaultValue: this.getIdxDefaultValue(data.idx)
      })
    },
    handleCheckChange (data, checked, indeterminate) {
      // 节点所对应的对象、节点本身是否被选中、节点的子树中是否有被选中的节点
      console.log(data, checked, indeterminate)
    },
    renderContent (h, { node, data, store }) {
      // console.log(node)
      return (
        <span class="custom-tree-node">
          <span>{node.label}</span>
          <span>
            <el-button size="mini" type="text" on-click={ () => this.watchIdx(data) }>监视</el-button>
          </span>
        </span>)
    },
    // 展开
    btnNodeExpand (data) {
      if (!this.treeShow) return
      const self = this
      data.forEach((el) => {
        self.$refs.pdoTree.store.nodesMap[el.id].expanded = true
        if (el.children && el.children.length > 0) {
          self.btnNodeExpand(el.children) // 子级递归
        }
      })
    },
    // 收缩
    btnNodeShrink (data) {
      if (!this.treeShow) return
      const self = this
      data.forEach((el) => {
        self.$refs.pdoTree.store.nodesMap[el.id].expanded = false
        if (el.children && el.children.length > 0) {
          self.btnNodeShrink(el.children) // 子级递归
        }
      })
    },
    // 清空监视
    btnNodeClear () {
      this.canopenTable.splice(0, this.canopenTable.length)
    },
    // 删除监视按钮
    canopnIdcRemoveClick (idx, data) {
      // todo 从监视定时器中删除

      // console.log(data)
      this.canopenTable.splice(idx, 1)
    },
    // 寻找前置节点，不存在则创建一个
    findFrontNode (front) {
      var ret
      this.pdoData.forEach((el) => {
        // console.log(el)
        if (el.label.substr(0, front.length) === front) {
          ret = el
        }
      })
      if (ret) return ret
      var tail = ''
      for (var i = 0; i < (4 - front.length); i++) {
        tail += 'x'
      }
      var node = { id: this.currentID, label: front + tail, children: [] }
      this.pdoData.push(node)
      this.currentID++
      return node
    },
    // 获取idx描述名
    getIdxParam (idx) {
      var lab = ' '
      if (this.config[idx] && this.config[idx].ParameterName !== undefined) {
        lab = this.config[idx].ParameterName
      }
      return lab
    },
    // 获取idx的参数权限
    getIdxAccessType (idx) {
      var acc = ' '
      if (this.config[idx] && this.config[idx].AccessType !== undefined) {
        acc = this.config[idx].AccessType
      }
      return acc
    },
    // 获取idx的 对象类型
    getIdxObjectType (idx) {
      var ojt = ' '
      if (this.config[idx] && this.config[idx].ObjectType !== undefined) {
        ojt = this.config[idx].ObjectType
      }
      return ojt
    },
    // 获取idx的 数据类型
    getIdxDataType (idx) {
      var dat = ' '
      if (this.config[idx] && this.config[idx].DataType !== undefined) {
        dat = this.config[idx].DataType
      }
      return dat
    },
    // 获取idx的 数据类型
    getIdxDefaultValue (idx) {
      var val = ' '
      if (this.config[idx] && this.config[idx].DefaultValue !== undefined) {
        val = this.config[idx].DefaultValue
      }
      return val
    },
    // 分析节点信息
    analysisNode (config, subSection) {
      for (var key in subSection) {
        if (key === 'SupportedObjects') {
          continue
        }
        const idx = subSection[key].substring(2)// 去掉0x

        // console.log(idx)
        var parent = this.findFrontNode(idx.substr(0, 1))
        // console.log(parent)
        if (config[idx] && 'SubNumber' in config[idx] && this.hex2int(config[idx].SubNumber) > 0) {
          var childNum = this.hex2int(config[idx].SubNumber)
          // console.log('sub size: ' + childNum)
          var child = []

          for (var i = 0; i < childNum; i++) {
            const subIdx = idx + 'sub' + i
            if (subIdx in config) {
              child.push({
                id: this.currentID,
                label: subIdx + '---' + this.getIdxParam(subIdx) + '---' + this.getIdxAccessType(subIdx),
                idx: subIdx
              })
              this.currentID++
            }
          }
          parent.children.push({
            id: this.currentID,
            label: idx + '---' + this.getIdxParam(idx) + '---' + this.getIdxAccessType(idx),
            children: child,
            idx: idx
          })
          this.currentID++
        } else {
          // console.log('sub size empty')
          parent.children.push({
            id: this.currentID,
            label: idx + '---' + this.getIdxParam(idx) + '---' + this.getIdxAccessType(idx),
            idx: idx
          })
          this.currentID++
        }
      }
    },
    chioceUploadFile () {
      dialog.showOpenDialog({
        title: '选择升级文件',
        defaultPath: '%userprofile%/Desktop', // 默认打开的文件路径选择
        filters: [{ // 过滤掉你不需要的文件格式
          name: 'bin',
          extensions: ['bin']
        }]
      }).then(res => {
        // console.log(res)
        if (res.filePaths[0] !== '') {
          this.uploadInput = res.filePaths[0]
        }
      }).catch(req => {
        console.log(req)
      })
    },
    uploadStart () {
      if (this.uploadInput === '') {
        this.$notify.error({
          title: '升级失败',
          message: '未选择文件',
          position: 'bottom-left'
        })
      } else {
        ipcRenderer.send('canopenSub2main', { msg: 'canopen upload start', id: this.canID, file: this.uploadInput })
        this.uploadDisabled = true // 升级按钮失效
      }
    }
  },
  mounted () {
    // 页面加载好后执行
    // 修改窗口标题
    // console.log(document.URL) # 页面url
    const eds = decodeURIComponent(getQueryVariable('eds')) // 获得eds参数并转换乱码
    const canID = decodeURIComponent(getQueryVariable('id'))
    // console.log(eds)
    this.edsFile = eds
    this.title = 'ID: ' + canID
    this.canID = parseInt(canID)
    this.edsPath = eds

    // 加载ini
    this.config = ini.parse(fs.readFileSync(eds, 'utf-8'))
    // console.log(config)
    if (this.config.FileInfo.FileName) this.edsFileName = this.config.FileInfo.FileName
    if (this.config.FileInfo.FileVersion) this.edsFileVersion = this.config.FileInfo.FileVersion
    if (this.config.FileInfo.FileRevision) this.edsFileRevision = this.config.FileInfo.FileRevision
    if (this.config.FileInfo.EDSVersion) this.edsEDSVersion = this.config.FileInfo.EDSVersion
    if (this.config.FileInfo.Description) this.edsDescription = this.config.FileInfo.Description
    if (this.config.FileInfo.CreationTime) this.edsCreationTime = this.config.FileInfo.CreationTime
    if (this.config.FileInfo.CreationDate) this.edsCreationDate = this.config.FileInfo.CreationDate
    if (this.config.FileInfo.CreatedBy) this.edsCreatedBy = this.config.FileInfo.CreatedBy
    if (this.config.FileInfo.ModificationTime) this.edsModificationTime = this.config.FileInfo.ModificationTime
    if (this.config.FileInfo.ModificationDate) this.edsModificationDate = this.config.FileInfo.ModificationDate
    if (this.config.FileInfo.ModifiedBy) this.edsModifiedBy = this.config.FileInfo.ModifiedBy

    this.pdoData.splice(0, this.pdoData.length) // 清空数组

    this.currentID = 1
    this.analysisNode(this.config, this.config.MandatoryObjects)
    this.analysisNode(this.config, this.config.OptionalObjects)
    this.analysisNode(this.config, this.config.ManufacturerObjects)

    window.onresize = () => {
      this.tableheight = ((window.innerHeight + 100) * 0.5)
      this.treeHeight = { maxHeight: ((window.innerHeight + 100) * 0.5) + 'px' }
    }

    this.sdoFreshTimer = window.setInterval(() => {
      if (!this.tableShow) return
      if (this.canopenTable.length === 0) return

      for (var i = 0; i < this.canopenTable.length; i++) {
        // console.log(this.canopenTable[i].tableParameterName)
      }
    }, 1000)

    ipcRenderer.on('main2canopenSub', (event, arg) => {
      // console.log(arg)
      switch (arg.msg) {
        case 'canopen upload start res':
          if (arg.id !== this.canID) {
            return
          }
          this.uploadDisabled = false // 升级按钮使能
          this.$notify({
            title: '升级结果',
            message: arg.result === true ? '升级成功' : '升级失败: ' + arg.describe,
            type: arg.result === true ? 'success' : 'error',
            position: arg.result === true ? 'bottom-left' : 'top-right',
            duration: arg.result === true ? 3000 : 0
          })

          break
      }
    })
  },
  destroyed () {
    if (this.sdoFreshTimer) {
      window.clearInterval(this.sdoFreshTimer)
    }
  }

}
</script>

<style>
  .custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
  }

  .tree{
      overflow-y: scroll;
      overflow-x: scroll;
      width: 100%;
      /* height: 50vh; */
  }
 .el-tree {
     min-width: 100%;
     display:inline-block !important;
 }
 .el-tree>.el-tree-node {
   min-width:100%;
   display:inlin-block !important;
 }
 .table{
      overflow-y: scroll;
      overflow-x: scroll;
      width: 100%;
      /* height: 50vh; */
  }
.el-card {
  margin-top: 20px;
  padding-bottom: 20px;
}
</style>
