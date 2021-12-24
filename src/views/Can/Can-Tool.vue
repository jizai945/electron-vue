<template>
  <el-row style="min-width:1000px">
    <el-card class="box-card" >
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
    <el-card class="box-card" style="margin-top:20px">
      <div>
        <el-col :span="3"><div><el-button type="danger" style="width:100%; margin-bottom:20px" @click="btnClear" >清空CAN日志</el-button></div></el-col>
        <el-col :span="3" :offset="1"><el-input v-model="canidInput" placeholder="CANID(0x02)"></el-input></el-col>
        <el-col :span="8" :offset="1"><el-input v-model="frameInput" placeholder="发送帧(0x01 0x02 0x03)"></el-input></el-col>
        <el-col :span="3" :offset="1"><div><el-button type="success" style="width:100%; margin-bottom:20px" @click="btnSend" >发送can数据</el-button></div></el-col>
        <el-col :span="3" :offset="1"><div><el-button type="warning" style="width:100%; margin-bottom:20px" @click="btnCanopen" >CanOpen视图</el-button></div></el-col>
      </div>
    </el-card>
    <el-card class="box-card" style="margin-top:20px;">
      <div slot="header" class="clearfix">
        <span>can日志数据</span>
      </div>
      <div>
        <el-col :span="24" style="margin-top:10px; margin-bottom:20px">
          <u-table :data="canTableData" :border="true" stripe style="width: 100%" max-height="500px">
            <u-table-column type="index" label="number" width="80"></u-table-column>
            <u-table-column prop="direction" label="方向" width="180"></u-table-column>
            <u-table-column prop="canid" label="帧ID" width="180"></u-table-column>
            <u-table-column prop="frame" label="数据"> </u-table-column>
          </u-table>
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
      canTableData: [
      ],
      canTableDataCache: [
      ],
      canidInput: '',
      frameInput: ''
    }
  },
  methods: {
    // 刷新按钮事件
    btnFreshPort () {
      this.portSelect = ''
      ipcRenderer.send('can2main', { msg: 'fresh port' })
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
        // 关闭串口
        this.btnFreshDisabled = false
        this.btnChangeDisabled = false
        this.selectPortDisabled = false
        this.$store.state.canBtnStr = '打开'
        // 请求关闭串口
        ipcRenderer.send('can2main', { msg: 'req port close', port: this.portSelect })
      }
    },
    btnClear () {
      this.canTableData = []
    },
    btnSend () {
      if (this.canidInput === '' || this.frameInput === '') {
        this.$message.error('canid 或 数据帧不允许为空')
      }
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
            this.portSelect = this.portList[0].label
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
          // console.log(arg.frame)
          if (this.canTableData.length > 30) {
            this.canTableData.shift()
          }
          this.canTableData.push({ direction: 'recv', canid: arg.canid, frame: arg.frame })
          this.$nextTick(() => {
            const container = this.$el.querySelector('.el-table__body-wrapper')
            container.scrollTop = container.scrollHeight
          })
          break
        case 'can frame buff':
          // console.log(arg)
          for (let i = 0; i < arg.f.length; i++) {
            if (this.canTableDataCache.length > 1000) {
              this.canTableDataCache.shift()
            }
            this.canTableDataCache.push({ direction: 'recv', canid: arg.id[i], frame: arg.f[i] })
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
      }
    })
  },
  computed: {
    portNextState () {
      return this.$store.state.canBtnStr
    }
  }
}
</script>
