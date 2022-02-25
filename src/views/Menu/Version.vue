<template>
   <el-row v-wechat-title="title">
      <el-card class="pack-card" style="min-width:480px; min-height:480px">
        <i style="margin-left: 0px" class="el-icon-sunny"></i>
        <span style="color:#666699;margin-left: 10px">版本</span>
        <el-divider></el-divider>
        <div class="block">
          <el-timeline>
            <el-timeline-item
            v-for="(ver, index) in version_line"
            :key="index"
            :timestamp="ver.time"
            placement="top">
              <el-card>
                <h4>{{ver.version}}</h4>
                <p>{{ver.change}}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
   </el-row>
</template>
<script>
const fs = require('fs')
export default {
  data: function () {
    return {
      title: '版本线',
      version_file: './update.json',
      version_line: [
        {
          time: 'xxxx',
          version: 'x.x.x',
          change: '获取版本错误'
        }
      ]
    }
  },
  mounted () {
    // ------------------------ 加载资源 --------------------------------
    try {
      const rawdata = fs.readFileSync(this.version_file)
      const dataobj = JSON.parse(rawdata)
      //   console.log(dataobj)
      this.version_line = dataobj.version_line
    } catch (err) {
      console.log(err)
    }
    // ----------------------------------------------------------------------
  }

}
</script>
