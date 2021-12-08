<template>
  <div id="app">
    <div>
      <router-view/>
    </div>
  </div>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'

export default {
  data () {
    return {
      radio: '1'
    }
  }
}
</script>

<style>
#app {
  height: 100vh;
}
</style>
