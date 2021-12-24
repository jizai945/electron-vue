/* eslint-disable no-undef-init */
/* eslint-disable indent */
// 本文件作用
// 1. 封装了命令行调用功能
var spawn = require('child_process').spawn
var iconv = require('iconv-lite')
var cmdfd = undefined

const ccmd = {
    /**
     * 运行命令行
     * @param args:Array<string> 执行参数
     */
    stop_shell: function () {
        if (cmdfd !== undefined) {
            cmdfd.kill()
        }
        cmdfd = undefined
    },

  /**
     * 运行命令行
     * @param args:Array<string> 执行参数
     * @param stdoutCb 标准输出回调
     * @param stderrCb 标准错误回调
     * @param exitCb 退出回调
     */
    run_shell: function (args, stdoutCb = null, stderrCb = null, exitCb = null) {
        if (stdoutCb === null && stderrCb === null && exitCb === null) {
            cmdfd = spawn(args[0], args.slice(1), {
                detached: true,
                stdio: 'ignore',
                stderr: 'ignore'
            })
            cmdfd.unref()
            return
        }
        cmdfd = spawn(args[0], args.slice(1))

        // 捕获标准输出并将其打印到控制台
        cmdfd.stdout.on('data', function (data) {
            console.log('standard output:\n' + iconv.decode(data, 'GBK'))
            if (stdoutCb !== null) {
                stdoutCb(iconv.decode(data, 'GBK'))
            }
        })

        // 捕获标准错误输出并将其打印到控制台
        cmdfd.stderr.on('data', function (data) {
            console.log('standard error output:\n' + iconv.decode(data, 'GBK'))
            if (stderrCb !== null) {
                stderrCb(iconv.decode(data, 'GBK'))
            }
        })

        // 注册子进程关闭事件
        cmdfd.on('exit', function (code, signal) {
            console.log('child process eixt ,exit:' + code)
            if (exitCb !== null) {
                exitCb(code)
            }
        })
    }
}

module.exports = ccmd
