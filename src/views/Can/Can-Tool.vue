<template>
  <el-row style="min-width:1000px">
    <el-card>
      <i class="el-icon-s-tools"><span style="margin-left:10px;">CAN-Serial</span></i>
    </el-card>
    <el-card class="box-card">
      <div>
        <el-col :span="2"><div><el-button type="primary" style="width:100%;" @click="btnFreshPort" :disabled="btnFreshDisabled">刷新</el-button></div></el-col>
        <el-col :span="17" :offset="1"><div><el-select v-model="portSelect" style="width:100%" placeholder="请选择" :disabled="selectPortDisabled">
                                <el-option
                                v-for="item in portList"
                                :key="item.value"
                                :label="item.label"
                                :value="item.value">
                                </el-option>
                            </el-select></div></el-col>
        <el-col :span="3" :offset="1"><div><el-button type="primary" style="width:100%; margin-bottom: 20px" @click="btnChangePort" :disabled="btnChangeDisabled">{{portNextState}}</el-button></div></el-col>
      </div>
    </el-card>
    <el-card class="box-card">
      <div>
        <el-col :span="3"><div><el-button type="danger" style="width:100%; margin-bottom:20px" @click="btnClear" >清空CAN日志</el-button></div></el-col>
        <el-col :span="3" :offset="1"><el-input v-model="canidInput" placeholder="CANID( FF 00 )"></el-input></el-col>
        <el-col :span="8" :offset="1"><el-input v-model="frameInput" placeholder="帧数据( F0 F1 F2 ...)"></el-input></el-col>
        <el-col :span="3" :offset="1"><div><el-button type="success" style="width:100%; margin-bottom:20px" @click="btnSend" >发送can数据</el-button></div></el-col>
        <el-col :span="3" :offset="1"><div><el-button type="warning" style="width:100%; margin-bottom:20px" @click="btnCanopen" >节点管理</el-button></div></el-col>
      </div>
    </el-card>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>can数据(上面为最新,最大缓存1000条)</span>
        <el-checkbox v-model="recvChecked" style="margin-left: 20px">接收</el-checkbox>
      </div>
      <div>
        <el-col :span="24" style="margin-top:10px; margin-bottom:20px">
          <!-- 只要在el-table元素中定义了height属性，即可实现固定表头的表格，而不需要额外的代码。 -->
          <el-table ref="canTable" class="tableBox" max-height="600" :row-class-name="tableRowClassName" :data="canTableData" :border="true" >
            <!-- <el-table-column type="index" label="number" width="80"></el-table-column> -->
            <el-table-column prop="num" label="nu" width="50"></el-table-column>
            <el-table-column prop="time" label="time" width="200"></el-table-column>
            <el-table-column prop="direction" label="方向" width="80"></el-table-column>
            <el-table-column prop="canid" label="帧ID" width="150"></el-table-column>
            <el-table-column prop="frame" label="数据(16进制)"> </el-table-column>
          </el-table>
        </el-col>
      </div>
    </el-card>
  </el-row>
</template>

<style>

</style>

<script>
import { ipcRenderer } from 'electron'
export default {
  data: function () {
    return {
      portList: [],
      portSelect: '',
      // portNextState: this.$store.state.canBtnStr,
      btnFreshDisabled: false,
      btnChangeDisabled: false,
      selectPortDisabled: false,
      recvChecked: true,
      canTableData: [
      ],
      canTableDataCache: [
      ],
      canidInput: '',
      frameInput: '',
      canNum: 0
    }
  },
  methods: {
    // 刷新按钮事件
    btnFreshPort () {
      this.portSelect = ''
      ipcRenderer.send('can2main', { msg: 'fresh port' })
    },
    close_can () {
      // 关闭串口
      this.btnFreshDisabled = false
      this.btnChangeDisabled = false
      this.selectPortDisabled = false
      this.$store.state.canBtnStr = '打开'
      // 请求关闭串口
      ipcRenderer.send('can2main', { msg: 'req port close', port: this.portSelect })
    },
    // 打开 / 关闭 按钮事件
    btnChangePort () {
      if (this.portNextState === '打开') {
        if (this.portSelect === '') { // 未选中
          this.$notify({
            title: '无法打开',
            message: '未选中任何串口',
            type: 'warning',
            position: 'bottom-left'
          })
          return
        }
        // 按钮禁用
        this.btnFreshDisabled = true
        this.btnChangeDisabled = true
        this.selectPortDisabled = true
        this.$store.state.canBtnStr = '打开中...'
        // 请求打开串口
        ipcRenderer.send('can2main', { msg: 'req port open', port: this.portSelect })
      } else {
        this.close_can()
      }
    },
    btnClear () {
      this.canTableData = []
      this.canTableDataCache = []
      this.canNum = 0
    },
    btnSend () {
      if (this.canidInput === '' || this.frameInput === '') {
        this.$message.error('canid 或 数据帧不允许为空')
        return
      }
      const canID = this.hex2int(this.canidInput)
      // 发送
      ipcRenderer.send('can2main', { msg: 'can send frame', canID: canID, frame: this.frameInput })
    },
    btnCanopen () {
      if (this.$store.state.canBtnStr !== '关闭') {
        this.$notify({
          title: '警告',
          message: '请先打开can设备',
          type: 'warning',
          position: 'bottom-left'
        })
        return
      }

      const item = {
        path: '/canopen',
        name: 'canopen',
        label: 'canopen',
        icon: 'star-off',
        url: 'Can/Canopen'
      }
      this.$router.push({ name: 'canopen' })
      this.$store.commit('selectMenu', item)
    },
    // 表格状态
    tableRowClassName ({ row, rowIndex }) {
      // console.log(row)
      if (row.direction === 'recv') {
        // return 'recv-row'
        if (rowIndex % 2) {
          return 'recv-row'
        }
        return ''
      }
      return 'send-row'
    }
  },
  mounted () {
    this.btnFreshPort()
    ipcRenderer.on('main2can', (event, arg) => {
      // console.log(arg)
      switch (arg.msg) {
        // 刷新端口反馈
        case 'fresh port res':
          this.$notify({
            title: '刷新',
            message: '刷新完成',
            type: 'success',
            position: 'bottom-left'
          })
          this.portList = []
          for (var i = 0; i < arg.port_value.length; i++) {
            this.portList.push({ value: arg.port_value[i], label: arg.port_label[i] })
          }
          // 默认选取第一个
          if (this.portList.length) {
            this.portSelect = this.portList[0].value
          }
          break
        // 请求打开端口反馈
        case 'req port open res':
          if (arg.result === true) {
            this.$store.state.canBtnStr = '关闭'
            this.btnChangeDisabled = false
            this.$notify({
              title: 'open' + this.portSelect,
              message: '打开成功',
              type: 'success',
              position: 'bottom-left'
            })
          } else {
            this.$store.state.canBtnStr = '打开'
            this.btnFreshDisabled = false
            this.btnChangeDisabled = false
            this.selectPortDisabled = false
            this.$notify.error({
              title: '打开失败',
              message: arg.code,
              position: 'bottom-left'
            })
          }
          break
        // can数据上报
        case 'can frame':
          if (this.recvChecked === false && arg.dir === 'r') {
            break
          }
          // console.log(arg.frame)
          if (this.canTableDataCache.length > 10) {
            this.canTableDataCache.pop()
          }
          this.canTableDataCache.unshift({
            num: this.canNum,
            time: arg.time,
            direction: arg.d[i] === 'r' ? 'recv' : 'send',
            canid: arg.canid,
            frame: arg.frame
          })
          this.canNum++
          this.canTableData = this.canTableDataCache // 缓存方式刷新缓解了界面刷新卡顿的问题
          break
        case 'can frame buff':
          // console.log(arg)
          var newDate = new Date()
          for (let i = 0; i < arg.f.length; i++) {
            if (this.canTableDataCache.length > 1000) {
              this.canTableDataCache.pop()
            }
            if (this.recvChecked === false && arg.d[i] === 'r') {
              continue
            }
            newDate.setTime(arg.t[i] * 1000)
            this.canTableDataCache.unshift({
              num: this.canNum,
              time: newDate.toLocaleString(),
              direction: arg.d[i] === 'r' ? 'recv' : 'send',
              canid: this.int2hex(arg.id[i]),
              frame: arg.f[i]
            })
            this.canNum++
          }
          this.canTableData = this.canTableDataCache // 缓存方式刷新缓解了界面刷新卡顿的问题
          break
        case 'can err':
          this.$notify.error({
            title: 'can 错误',
            message: arg.describe,
            duration: 0,
            position: 'bottom-right'
          })
          break
        case 'can send frame res': // 发送错误反馈
          if (arg.result !== false) break
          this.$notify.error({
            title: 'can 发送错误',
            message: arg.code,
            position: 'bottom-left'
          })
          break
      }
    })
  },
  watch: {
    // canTableData () {
    //   this.$nextTick(() => {
    //     console.log(this.$refs.canTable)
    //     // this.$refs.canTable.bodyWrapper.scrollTop = this.$refs.canTable.bodyWrapper.scrollHeight
    //   })
    // }
  },
  computed: {
    portNextState () {
      return this.$store.state.canBtnStr
    }
  },
  destroyed () {
    // 销毁的事情要记得
    ipcRenderer.removeAllListeners() // ！！！
  }
}
</script>

<style>
.el-card{
  margin-top: 20px;
}

.el-table .send-row {
  background: rgb(236, 193, 193);
}

.el-table .recv-row {
  background: #f0f9eb;
}
</style>

<style lang="scss">
.tableBox {
  width: 100%;
  th {
    padding: 0 !important;
    height: 10px;
    line-height: 30px;
  }
  td {
    padding: 0 !important;
    height:30px;
    line-height: 30px;
  }
}

</style>
