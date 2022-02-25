<template style="min-width:1000px">
    <el-row style="min-width:1000px">
        <el-card class="pack-card">
            <i style="margin-left: 0px" class="el-icon-coin"></i>
            <span style="color:#666699;margin-left: 10px">EDS转C</span>
            <el-divider></el-divider>
            <el-form :model="dataForm" ref="dataForm" label-width="200px" class="demo-dataForm">
                <el-form-item label="eds文件" prop="eds" :rules="rules.eds">
                    <el-col :span="18">
                        <el-input v-model="dataForm.eds" :disabled=true></el-input>
                    </el-col>
                    <el-col :span="3" :offset="1">
                        <el-button type="primary" @click.prevent="fileChoiceClick('eds')">选择文件</el-button>
                    </el-col>
                </el-form-item>
                <el-form-item label="runtime_c:" prop="runtime" :rules="rules.runtime">
                    <el-col :span="18">
                        <el-input v-model="dataForm.runtime" :disabled=true></el-input>
                    </el-col>
                    <el-col :span="3" :offset="1">
                        <el-button type="primary" @click.prevent="fileChoiceClick('runtime')">选择保存</el-button>
                    </el-col>
                </el-form-item>
                <el-form-item label="user_c:" prop="user" :rules="rules.user">
                    <el-col :span="18">
                        <el-input v-model="dataForm.user" :disabled=true></el-input>
                    </el-col>
                    <el-col :span="3" :offset="1">
                        <el-button type="primary" @click.prevent="fileChoiceClick('user')">选择保存</el-button>
                    </el-col>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="startConvert">开始生成</el-button>
                    <el-button @click="resetConvert('dataForm')">清空</el-button>
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
      dataForm: {
        eds: '',
        runtime: '',
        user: ''
      },
      rules: {
        eds: [{ required: true, message: 'eds文件不能为空' }],
        runtime: [{ required: true, message: 'runtime文件不能为空' }],
        user: [{ required: true, message: 'user文件不能为空' }]
      },
      cachePath: './tmp',
      cacheFile: 'eds2c.json'
    }
  },
  methods: {
    fileChoiceClick (type) {
      switch (type) {
        case 'eds':
          dialog.showOpenDialog({
            title: '请选择你的eds文件',
            defaultPath: '%userprofile%/Desktop', // 默认打开的文件路径选择
            filters: [{ // 过滤掉你不需要的文件格式
              name: 'eds',
              extensions: ['eds']
            }]
          }).then(res => {
            // console.log(res)
            if (res.filePaths[0] !== '') {
              this.dataForm.eds = res.filePaths[0]
            }
          }).catch(req => {
            console.log(req)
          })
          break
        default:
          dialog.showSaveDialog({
            title: '请选择' + type + '要保存的文件名',
            buttonLabel: '保存',
            filters: [
              { name: 'c', extensions: ['c'] }
            ]
          }).then(result => {
            console.log(result)
            if (result.canceled === false) {
              this.dataForm[type] = result.filePath
            }
          }).catch(err => {
            console.log(err)
          })

          break
      }
    },
    startConvert () {
      this.$refs.dataForm.validate((valid) => {
        if (valid) {
          ipcRenderer.send('edsconvert2main', { msg: 'eds convert', data: this.dataForm })
        } else {
          this.$message.error('参数不全')
          return false
        }
      })
    },
    resetConvert (data) {
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
    // ------------------------- 加载缓存配置 ------------------------------------
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
    // ---------------------------------------------------------------------------
    ipcRenderer.on('main2can', (event, arg) => {
      switch (arg.msg) {
        case 'eds convert res':
          this.$notify({
            title: '转换',
            message: arg.result === true ? '转换成功' : '转换失败: ' + arg.describe,
            type: arg.result === true ? 'success' : 'error',
            position: 'bottom-left'
          })
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
