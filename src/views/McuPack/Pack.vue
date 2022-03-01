<template style="min-width:1000px">
    <el-row style="min-width:1000px">
        <el-card class="pack-card">
            <el-form :model="dataForm" ref="dataForm" label-width="200px" class="demo-dataForm">
                <span>打包配置---格式版本: {{dataForm.protocolVersion}}</span>
                    <el-divider></el-divider>
                <el-form-item label="打包版本号" prop="version" :rules="rules.version">
                    <el-col :span="18">
                        <el-input v-model="dataForm.version"></el-input>
                    </el-col>
                </el-form-item>
                <el-form-item label="文件名" prop="fileName" :rules="rules.version">
                    <el-col :span="18">
                        <el-input v-model="dataForm.fileName"></el-input>
                    </el-col>
                </el-form-item>
                <span>烧录文件</span>
                    <el-divider></el-divider>
                <div v-for="(name, index) in firmwareName" :key="`${index}Firmware`">
                  <el-form-item :label="name" :prop="name" :rules="rules[`${name}`]">
                    <el-col :span="18">
                      <el-input v-model="dataForm[`${name}`]" :disabled=true></el-input>
                    </el-col>
                    <el-col :span="3" :offset="1">
                      <el-button type="primary" @click.prevent="fileChoiceClick(name)">选择文件</el-button>
                    </el-col>
                  </el-form-item>

                  <el-form-item :label='`${name}版本`' :prop="`${name}Version`" :rules="rules[`${name}Version`]">
                    <el-col :span="18">
                        <el-input v-model="dataForm[`${name}Version`]"></el-input>
                    </el-col>
                  </el-form-item>
                  <el-divider content-position="left"><i class="el-icon-finished"></i></el-divider>
                </div>
                <span>选填项</span>
                    <el-divider></el-divider>
                <el-form-item label="日志信息" >
                    <el-col :span="18">
                        <el-input v-model="dataForm.log"></el-input>
                    </el-col>
                </el-form-item>
                <el-form-item label="加密算法">
                    <el-select v-model="dataForm.encryption" placeholder="请选择加密算法">
                    <el-option label="无" value="none"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="依赖">
                    <el-switch v-model="dataForm.depFlag"></el-switch>
                </el-form-item>
                <el-form-item label="mcu型号" v-show="dataForm.depFlag">
                    <el-col :span="18">
                        <el-input v-model="dataForm.deps.mcu_model"></el-input>
                    </el-col>
                </el-form-item>
                <el-form-item
                    v-show="dataForm.depFlag"
                    v-for="(hv, index) in dataForm.deps.hver"
                    :label="'硬件依赖' + index"
                    :key="hv.key"
                    :prop="'deps.hver.' + index + '.value'"
                >
                    <el-col :span="18">
                        <el-input v-model="hv.value"></el-input>
                    </el-col>
                    <el-col :span="1">
                        <span> </span>
                    </el-col>
                    <el-col :span="2">
                        <el-button type="success" @click.prevent="addHver">增加</el-button>
                    </el-col>
                    <el-col :span="2" v-if="index !== 0">
                        <el-button type="danger" @click.prevent="removeHver(hv)">删除</el-button>
                    </el-col>
                </el-form-item>
                <el-form-item label="项目名" v-show="dataForm.depFlag">
                    <el-col :span="18">
                        <el-input v-model="dataForm.deps.prj"></el-input>
                    </el-col>
                </el-form-item>
                <el-form-item label="板卡类型" v-show="dataForm.depFlag">
                    <el-col :span="18">
                        <el-input v-model="dataForm.deps.btype"></el-input>
                    </el-col>
                </el-form-item>
                <el-form-item label="func" v-show="dataForm.depFlag">
                    <el-col :span="18">
                        <el-input v-model="dataForm.deps.func"></el-input>
                    </el-col>
                </el-form-item>
                <span>分区表信息(不可修改)</span>
                  <el-switch v-model="dataForm.partionVisible" active-text="显示" inactive-text="隐藏" style="margin-left:20px"></el-switch>
                  <el-divider></el-divider>
                <div v-for="(name, index) in partion_table" :key="`${index}Partion`">
                  <el-form-item :label='`${name} 起始地址`' :prop="`${name}PartStart`" :rules="rules[`${name}PartStart`]" v-show="dataForm.partionVisible">
                    <el-col :span="18">
                        <el-input v-model="dataForm[`${name}PartStart`]" :disabled=true></el-input>
                    </el-col>
                  </el-form-item>
                  <el-form-item label='分区大小' :prop="`${name}PartSize`" :rules="rules[`${name}PartSize`]" v-show="dataForm.partionVisible">
                    <el-col :span="18">
                        <el-input v-model="dataForm[`${name}PartSize`]" :disabled=true></el-input>
                    </el-col>
                  </el-form-item>
                  <el-form-item label='是否boot' :prop="`${name}PartBoot`" v-show="dataForm.partionVisible">
                    <el-col :span="18">
                        <el-switch v-model="dataForm[`${name}PartBoot`]" disabled></el-switch>
                    </el-col>
                  </el-form-item>
                  <div  v-show="dataForm.partionVisible">
                    <el-divider content-position="left"><i class="el-icon-finished"></i></el-divider>
                  </div>
                </div>
                <el-form-item>
                  <el-button type="primary" @click="startPack('dataForm')">打包</el-button>
                  <el-button @click="resetPack('dataForm')">重置</el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </el-row>
</template>
<script>
import { ipcRenderer } from 'electron'
const { dialog } = require('electron').remote
const fs = require('fs')
export default {
  data: function () {
    return {
      cachePath: './tmp',
      cacheFile: 'pack.json',
      firmwareName: ['runtime', 'bsp', 'user', 'upgrade'], // 固件名列表
      partion_table: ['parameters', 'bsp', 'runtime', 'user', 'parameters_bk'], // 分区表名称
      dataForm: {
        partionVisible: false, // 是否展示分区表信息
        protocolVersion: '0.1.0', // 格式版本
        version: '0.0.1', // 版本号
        fileName: '/firmware/user', // 文件名
        encryption: '无', // 加密方式
        depFlag: false, // 是否有依赖
        deps: {
          mcu_model: 'stm32f103c8t6',
          hver: [{ value: '', key: Date.now() }],
          prj: 'HOLA_PJ0003',
          btype: 'motorboard',
          func: 'MOTOR_DRIVER'
        },
        log: '', // 日志信息
        /* ------------ 固件信息----------- */
        runtime: '',
        runtimeVersion: '0.1.0',
        bsp: '',
        bspVersion: '0.1.0',
        user: '',
        userVersion: '0.1.0',
        upgrade: '',
        upgradeVersion: '0.1.0',
        /* --------------------------------- */
        /* ------------ 分区表信息----------- */
        parametersPartBoot: false,
        parametersPartStart: '0x800c000',
        parametersPartSize: 8192,
        bspPartBoot: false,
        bspPartStart: '0x8010000',
        bspPartSize: 0x10000,
        runtimePartBoot: true,
        runtimePartStart: '0x8020000',
        runtimePartSize: 0x20000,
        userPartBoot: false,
        userPartStart: '0x8040000',
        userPartSize: 131072,
        parameters_bkPartBoot: false,
        parameters_bkPartStart: '0x8060000',
        parameters_bkPartSize: '131072'
        /* --------------------------------- */
      },
      rules: {
        version: [{ required: true, message: '版本不能为空' }],
        fileName: [{ required: true, message: '文件名不能为空' }],
        runtime: [{ required: true, message: 'runtime不能为空' }],
        runtimeVersion: [{ required: true, message: '版本不能为空' }],
        bsp: [{ required: true, message: 'bsp不能为空' }],
        bspVersion: [{ required: true, message: '版本不能为空' }],
        user: [{ required: true, message: 'user不能为空' }],
        userVersion: [{ required: true, message: '版本不能为空' }],
        upgrade: [{ required: true, message: 'upgrade不能为空' }],
        upgradeVersion: [{ required: true, message: '版本不能为空' }],
        parametersPartStart: [{ required: true, message: '起始地址不能为空' }],
        parametersPartSize: [{ required: true, message: '分区大小不能为空' }],
        bspPartStart: [{ required: true, message: '起始地址不能为空' }],
        bspPartSize: [{ required: true, message: '分区大小不能为空' }],
        runtimePartStart: [{ required: true, message: '起始地址不能为空' }],
        runtimePartSize: [{ required: true, message: '分区大小不能为空' }],
        userPartStart: [{ required: true, message: '起始地址不能为空' }],
        userPartSize: [{ required: true, message: '分区大小不能为空' }],
        parameters_bkPartStart: [{ required: true, message: '起始地址不能为空' }],
        parameters_bkPartSize: [{ required: true, message: '分区大小不能为空' }]
      },
      numberValidateForm: {
        age: '123'
      }
    }
  },
  methods: {
    fileChoiceClick (type) {
      dialog.showOpenDialog({
        title: '请选择你的' + type + '文件',
        filters: [{ // 过滤掉你不需要的文件格式
          name: 'bin/hex',
          extensions: ['bin', 'hex']
        }]
      }).then(res => {
        // console.log(res)
        if (res.filePaths[0] !== '') {
          this.dataForm[type] = res.filePaths[0]
        }
      }).catch(req => {
        console.log(req)
      })
    },
    removeHver (item) {
      var index = this.dataForm.deps.hver.indexOf(item)
      if (index !== -1) {
        this.dataForm.deps.hver.splice(index, 1)
      }
    },
    addHver () {
      this.dataForm.deps.hver.push({
        value: '',
        key: Date.now()
      })
    },
    startPack (data) {
      this.$refs[data].validate((valid) => {
        if (valid) {
          dialog.showSaveDialog({
            title: '请选择要保存的文件名',
            buttonLabel: '保存',
            filters: [
              { name: 'bin', extensions: ['bin'] }
            ]
          }).then(result => {
            console.log(result)
            if (result.canceled === false) {
              this.$message('开始打包....')
              ipcRenderer.send('pack2main', { msg: 'start pack', data: this.dataForm, target: result.filePath })
            }
          }).catch(err => {
            console.log(err)
          })
        } else {
        //   console.log('error submit!!')
          this.$message.error('参数不全')
          return false
        }
      })
    },
    resetPack (data) {
      this.$refs[data].resetFields()
    }
  },
  watch: {
    dataForm: {
      handler (newVal) {
        const data = JSON.stringify(newVal)
        fs.writeFileSync(this.cachePath + '/' + this.cacheFile, data)
      },
      deep: true,
      immediate: false
    }
  },
  mounted () {
    // -------------- 加载缓存配置 ------------------
    // 从后端读取分区表配置
    ipcRenderer.send('pack2main', { msg: 'read pack toml cfg' })

    if (!fs.existsSync(this.cachePath)) {
      fs.mkdirSync(this.cachePath)
    }

    try {
      const rawdata = fs.readFileSync(this.cachePath + '/' + this.cacheFile)
      const dataobj = JSON.parse(rawdata)
      //   console.log(dataobj)
      this.dataForm = dataobj
    } catch (err) {
      console.log(err)
      console.log('read json err')
      const data = JSON.stringify(this.dataForm)
      fs.writeFileSync(this.cachePath + '/' + this.cacheFile, data)
    }
    // -----------------------------------------------------
    ipcRenderer.on('main2can', (event, arg) => {
      switch (arg.msg) {
        case 'pack res':
          this.$notify({
            title: '打包',
            message: arg.result === true ? '打包成功' : '打包失败: ' + arg.describe,
            type: arg.result === true ? 'success' : 'error',
            position: 'bottom-left'
          })
          break
        case 'read pack toml cfg res':
          console.log(arg)
          if (arg.result === false) {
            this.$notify({
              title: '读取分区参数出错',
              message: arg.describe,
              type: 'error',
              position: 'bottom-left'
            })
            return
          }

          try {
            for (let i = 0; i < arg.data.partion_table.length; i++) {
              // console.log(this.int2hex(arg.data.partion_table[i].start_addr))
              this.dataForm[arg.data.partion_table[i].label + 'PartStart'] = this.int2hex(arg.data.partion_table[i].start_addr)
              this.dataForm[arg.data.partion_table[i].label + 'PartSize'] = arg.data.partion_table[i].size
              this.dataForm[arg.data.partion_table[i].label + 'PartBoot'] = arg.data.partion_table[i].is_bootable
            }
          } catch (err) {
            this.$notify({
              title: '分区参数解析出错',
              message: '' + err,
              type: 'error',
              position: 'bottom-left'
            })
          }

          break
        default:
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
.el-col {
  min-height: 1px
}
</style>>
