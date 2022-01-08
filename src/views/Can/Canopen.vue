<template>
  <el-row style="min-width:1000px">
    <el-card>
      <i class="el-icon-s-tools"><span style="margin-left:10px;">CanOpen节点管理</span></i>
    </el-card>
    <el-card class="box-card" >
      <div>
        <el-col :span="4" :offset="1"><div><el-button type="success" style="width:100%; margin-bottom:20px" @click="btnCanopenAddNode">添加canopen节点</el-button></div></el-col>
        <!-- dialog -->
        <el-dialog title="节点配置" :visible.sync="dialogCanopenNodeVisible" style="min-width:1300px">
          <el-row >
            <el-col :span="4"><div style="margin-top:10px">节点ID(16进制): </div></el-col>
            <el-col :span="19" :offset="1"><div><el-input v-model="inputCanID" placeholder="请输入内容节点ID 0x00"></el-input></div></el-col>
            <el-col :span="20" style="margin-top:10px"><div><el-input v-model="inputEdsFile" readonly placeholder="请选择eds文件"></el-input></div></el-col>
            <el-col :span="3" :offset="1" style="margin-top:10px"><div><el-button type="primary" style="float: right" @click="btnChoiceEds">选择eds</el-button></div></el-col>
            <el-col :span="4" :offset="10" style="margin-top:20px"><div><el-button type="primary" style="float: right" @click="btnNodeSure">确认</el-button></div></el-col>
          </el-row>
        </el-dialog>
      </div>
    </el-card>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span style="color:#666699; margin-left: 50px">canopen节点管理</span>
      </div>
      <div>
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
  </el-row>
</template>

<script>
import { ipcRenderer } from 'electron'
import { windowCreate, windowCloseRoute } from '../../main/modules/windowApi'
const { dialog } = require('electron').remote
const canopenRouteHead = '/CanopenSub'
export default {
  data: function () {
    return {
      dialogCanopenNodeVisible: false,
      inputCanID: '',
      inputEdsFile: '',
      canopenDrawer: false,
      checkedCanopenID: [],
      canidManger: {}, // canid管理, 格式  {id: {eds: path}}
      isIndeterminate: true,
      checkAll: false,
      canopenTable: []
    }
  },
  methods: {
    // 添加节点按钮事件
    btnCanopenAddNode () {
      // windowCreate({
      //   title: canopenRouteHead,
      //   route: canopenRouteHead + '?id=' + 0 + '&eds=C:\\Users\\Wang\\Desktop\\e35-pudu.eds',
      //   width: 1000,
      //   height: 750,
      //   backgroundColor: '#f9f9f9',
      //   resizable: true,
      //   modal: true,
      //   maximize: false,
      //   autoHideMenuBar: true
      // })

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
      if (this.canidManger[id] !== undefined) {
        const route = canopenRouteHead + '?id=' + id + '&eds=' + this.canidManger[id].eds
        windowCloseRoute(route) // 关闭之前的窗口
      }

      ipcRenderer.send('canopen2main', { msg: 'canopen add node', node: id, eds: this.inputEdsFile })
      this.canidManger[id] = { eds: this.inputEdsFile }
    },
    // 刷新canopen的节点管理表格
    canopenTableViewFresh () {
      this.canopenTable.splice(0, this.canopenTable.length) // 清空数组
      for (var id in this.canidManger) {
        this.canopenTable.push({ canid: this.int2hex(Number(id)), eds: this.canidManger[id].eds })
      }
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
    // 节点删除
    rowDeleteClick (row) {
      // row.canid row.eds
      const id = this.hex2int(row.canid)
      ipcRenderer.send('canopen2main', { msg: 'canopen remove node', node: id })
      if (this.canidManger[id] !== undefined) {
        const route = canopenRouteHead + '?id=' + id + '&eds=' + this.canidManger[id].eds
        windowCloseRoute(route) // 关闭之前的窗口
        delete this.canidManger[id]
      }
      this.canopenTableViewFresh()
    }
  },
  mounted () {
    ipcRenderer.on('main2can', (event, arg) => {
      switch (arg.msg) {
        case 'canopen add node res':
          this.$notify({
            title: '添加节点',
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
</style>
