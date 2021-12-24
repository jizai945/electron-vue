<template>
  <div class="canopen">
      <router-view/>
    <h1>This is an canopen sub page</h1>
  </div>
</template>
<script>
export default {
  data: function () {
    return {

    }
  },
  mounted () {
    console.log('???')
    console.log(location.href)
  }

}
</script>
