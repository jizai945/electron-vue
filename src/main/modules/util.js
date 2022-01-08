
/**
 * 获取url上的参数
 */
export function getQueryVariable (variable) {
  var query = document.URL
  var vars = query.split(/[?&]/) // 同时用 ? 和 & 分割
  //   console.log(vars)
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split('=')
    if (pair[0] === variable) { return pair[1] }
  }
  return (false)
}

/**
 * 获取url上的参数
 */
export function getQueryVariableFromStr (str, variable) {
  var query = str
  var vars = query.split(/[?&]/) // 同时用 ? 和 & 分割
  //   console.log(vars)
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split('=')
    if (pair[0] === variable) { return pair[1] }
  }
  return (false)
}
