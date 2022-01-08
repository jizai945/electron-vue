'''mcu打包命令行工具'''

from canopen.sdo.constants import END_BLOCK_TRANSFER
import click
import sys
import os
import json
import struct
try:
    from modules.crc32 import *
except:
    from crc32 import *

VERSION = '0.1.0'               # 协议格式版本
HEAD = 'PUDUMCUFILE'
sub_file_list = []
sub_partion_names = []
encrypted = False               # 加密开关标志位
file_info_json_len = 1*1024     # 文件描述信息json字符串长度  这里的长度是在文件中的最大长度，不是字符串实际有效长度
file_log_len = 0                # 文件日志字段长度
attach_json_len = 2*1024        # 附加数据字符串长度            这里的长度是在文件中的最大长度，不是字符串实际有效长度
mcuModel = 'stm32f103c8t6'      # mcu型号
attach_json_str = ''            # 附加数据json字符串
hver = []                       # 依赖信息
json_str_end = '‖'              # json字符串结束符

def check_file(file:str) -> bool:
    '''检查文件路径是否合法'''
    return os.path.isfile(file)

def get_file_size(file:str) -> int:
    '''获取文件大小'''
    if check_file(file):
        return os.path.getsize(file)
    return 0

def get_file_list_crc(file_list:list) -> int:
    '''获取列表文件crc'''
    data = bytes()
    for fi in file_list:
        with open(fi, 'rb') as f:
            data += f.read()

    return crc32_bytes(data)

def get_file_crc(file:str) -> int:
    '''获取文件crc'''
    data = bytes()
    with open (file, 'rb') as f:
        data = f.read()

    return crc32_bytes(data)

def input_subfile_name():
    click.echo('请输入文件名: ', nl=False)
    file = input()
    if check_file(file):
        sub_file_list.append(file)
    else:
        click.secho('file path err', fg='red', err=True)
        sys.exit(1)

def generate_attach_json(hver_=[], prj='HOLA_PJ0003', btype='motorboard', func='MOTOR_DRIVER') -> str:
    '''生成附加数据json字符串'''

    global mcuModel
    global hver
    global attach_json_str
    # 11字节头文件标记 + 4字节文件描述信息长度 + 4字节文件描述信息crc32 + 文件描述信息json字符串长度 + 文件日志 + 附加数据长度
    offset = len(HEAD) + 4 + 4 + file_info_json_len + file_log_len + attach_json_len

    attach = dict()
    attach['imgCnt'] = len(sub_file_list)
    attach['imgList'] = list()
    for i in range(attach['imgCnt']):
        sub_dict = dict()
        sub_dict['partion_name'] = sub_partion_names[i]
        sub_dict['version'] = VERSION
        if not encrypted:
            sub_dict['csize'] = get_file_size(sub_file_list[i])         # 加密后大小
            sub_dict['ccrc'] = get_file_crc(sub_file_list[i])           # 加密后crc
            sub_dict['osize'] = sub_dict['csize']                       # 原大小
            sub_dict['ocrc'] = sub_dict['ccrc']                         # 原crc
            sub_dict['fpos'] = dict()
            sub_dict['fpos']['pos'] = offset                            # 偏移
            sub_dict['fpos']['size'] = sub_dict['csize']                # 大小
            offset += sub_dict['csize']
        sub_dict['deps'] = dict()
        sub_dict['deps']['mcuModel'] = mcuModel
        sub_dict['deps']['hver'] = hver
        sub_dict['deps']['prj'] = prj
        sub_dict['deps']['btype'] = btype
        sub_dict['deps']['func'] = func

        attach['imgList'].append(sub_dict)

    attach_json_str = json.dumps(attach, ensure_ascii=False)
    if len(attach_json_str) > attach_json_len + len(json_str_end) + 1:
        click.secho(f'attach json len > {attach_json_len + len(json_str_end) + 1}', err=True, fg='red')
        sys.exit(1)

    # 字符串不满长度，填充空格
    attach_json_str += json_str_end
    attach_json_str += ' ' * (attach_json_len - len(attach_json_str) - len(json_str_end) - 1)
    attach_json_str += '\n'

    # click.echo(json_str)
    return attach_json_str


def generate_file_info_json(file:str, sub_file_list:list, version:str) -> str:
    '''
    生成 文件描述信息json字符串 暂无加密，json假定最大2K大小
    '''
    global attach_json_str
    global VERSION
    global encrypted
    size = 0

    info_dict = dict()
    info_dict['fver'] = VERSION                                 # 文件格式版本
    info_dict['file'] = file                                    # 文件名
    info_dict['ver'] = version                                  # 文件版本
    for su in sub_file_list:
        size += get_file_size(su)
    if not encrypted: 
        info_dict['csize'] = size                                   # 加密后大小, 暂无加密
        info_dict['osize'] = size                                   # 原始大小
        info_dict['ccrc'] =  get_file_list_crc(sub_file_list)       # 加密后crc 暂无加密
        info_dict['ocrc'] = info_dict['ccrc']                       # 原始crc

    info_dict['content_pos'] = len(HEAD) + 4 + 4 + file_info_json_len + file_log_len + attach_json_len # 打包烧录文件的偏移位置
    # info_dict['log'] 空
    info_dict['attach'] = dict()
    info_dict['attach']['pos'] = len(HEAD) + 4 + 4 + file_info_json_len + file_log_len  # 附加数据起始位置
    info_dict['attach']['size'] = len(attach_json_str.split(json_str_end)[0])
    info_dict['attach']['encrypted'] = encrypted
    info_dict['attach']['crc'] = crc32_bytes(bytes(attach_json_str.split(json_str_end)[0], encoding = 'utf-8'))

    json_str = json.dumps(info_dict, ensure_ascii=False)
    if len(json_str) > file_info_json_len + len(json_str_end) + 1:
        click.secho(f'file info json len > {file_info_json_len + len(json_str_end) + 1}', err=True, fg='red')
        sys.exit(1)

    # 字符串不满长度，填充空格
    json_str += json_str_end
    json_str += ' ' * (file_info_json_len - len(json_str) - len(json_str_end) - 1)
    json_str += '\n'

    # click.echo(json_str)
    return json_str


@click.group()
def cli():
    pass

@click.command()
def version():
    """output version"""
    click.echo(f'version: {VERSION}')

@click.command()
@click.option('--hash-type', prompt=True, type=click.Choice(['md5', 'sha1']))
def digest(hash_type):
    '''for test'''
    click.echo(hash_type)

def pack_process(file_name:str, pack_version:str) -> bool:
    global sub_partion_names
    global sub_file_list

    attach_str = generate_attach_json()  # 生成附加数据
    log_str = ''  # 日志
    file_info_str = generate_file_info_json(file_name, sub_file_list, pack_version)  # 描述信息
    file_info_crc = crc32_bytes(bytes(file_info_str.split(json_str_end)[0], encoding='utf-8')) # 结束符前的crc
    sub_file_bytes = bytes()
    for fi in sub_file_list:
        with open(fi, 'rb') as f:
            sub_file_bytes += f.read()

    file_bytes = HEAD.encode('utf-8') + \
                 len(file_info_str.split(json_str_end)[0]).to_bytes(4, byteorder='little', signed=False) + \
                 file_info_crc.to_bytes(4, byteorder='little', signed=False) + \
                 file_info_str.encode('utf-8') + log_str.encode('utf-8') + attach_str.encode('utf-8') + sub_file_bytes

    with open(file_name, 'wb+') as f:
        f.write(file_bytes)

    # 打印信息
    click.secho('-' * 100, fg='green')
    click.echo('文件名: ', nl=False)
    click.secho(file_name, fg='yellow')
    click.echo(f'版本: {pack_version}')
    click.echo(f'打包文件大小: {len(file_bytes)}')

    click.echo('子文件路径: ')
    for fi, pa in zip(sub_file_list, sub_partion_names):
        click.secho(
            f'*\t{fi} - partion_name:({pa}) - size:({get_file_size(fi)}) - crc:({"0x{:08x}".format(get_file_crc(fi))})',
            fg='yellow')

    click.secho('-' * 100, fg='green')
    click.secho('打包成功', fg='green')

    return True

def pack_func(file_name, sub_file, part_name, pack_version, mcu, hver_):
    '''pack file'''

    global sub_partion_names
    global sub_file_list
    global mcuModel
    global hver

    if file_name == None:
        click.secho('文件名为空', err=True, fg='red')
        sys.exit(1)

    if len(sub_file) == 0:
        click.secho('子文件为空', err=True, fg='red')
        sys.exit(1)

    if len(part_name) == 0:
        click.secho('分区名为空', err=True, fg='red')
        sys.exit(1)

    if len(sub_file) != len(part_name):
        click.secho('子文件和分区名条数不对应', err=True, fg='red')
        sys.exit(1)

    for fi in sub_file:
        if not check_file(fi):
            click.secho('文件路径不合法', err=True, fg='red')
            sys.exit(1)

    if pack_version == None:
        click.secho('版本为空', err=True, fg='red')
        sys.exit(1)

    if mcu == None:
        click.secho('芯片型号为空', err=True, fg='red')
        sys.exit(1)

    sub_file_list = [sf for sf in sub_file]
    sub_partion_names = [pn for pn in part_name]
    mcuModel = mcu
    hver = [h for h in hver_]

    pack_process(file_name, pack_version)

@click.command()
@click.option('--file-name', '-f', help='input your file name', type=str)
@click.option('--sub-file', '-s', help='input sub files', multiple=True)
@click.option('--part-name', '-p', help='input part name', multiple=True)
@click.option('--pack-version', '-v', help='input pack version', type=str)
@click.option('--mcu', '-m', help='input mcu', type=str)
@click.option('--hver_', '-h', help='input hver', multiple=True)
def pack(file_name, sub_file, part_name, pack_version, mcu, hver_):
    '''mcu file pack 对外cil接口'''

    pack_func(file_name, sub_file, part_name, pack_version, mcu, hver_)

cli.add_command(version)
cli.add_command(digest)
cli.add_command(pack)

def run_pack_func():
    global sub_file_list
    global sub_partion_names
    global mcuModel
    global hver
    nums = 0

    click.secho('>>> now start pack process', fg='green')
    click.secho('请输入打包后的版本: ', nl=False)
    version = input()
    if not len(version):
        click.secho('版本有误! ', err=False, fg='red')
        sys.exit(1)

    click.secho('请输入打包后的文件名: ', nl=False)
    file = input()
    if not len(file):
        click.secho('文件名有误! ', err=False, fg='red')
        sys.exit(1)

    click.secho('请输入芯片型号(example stm32f103c8t6): ', nl=False)
    tmp = input()
    if not len(tmp):
        click.secho('输入有误! ', err=False, fg='red')
        sys.exit(1)
    mcuModel = tmp

    while True:
        click.secho('请继续输入依赖信息, 没有则直接回车: ', nl=False)
        tmp = input()
        if not len(tmp):
            break
        hver.append(tmp)

    while not nums:
        click.secho('请输入要打包的文件数量: ', nl=False)
        nums = input()
        nums = int(nums)
        if not nums:
            click.secho('文件数量不能为0，请重新输入! ', err=False, fg='red')
            continue

        sub_file_list = list()
        for _ in range(nums):
            while True:
                click.secho(f'文件路径{_} : ', nl=False)
                sub_file = input()
                if not check_file(sub_file):
                    click.secho('文件路径不合法，请重新输入! ', err=False, fg='red')
                    continue
                else:
                    sub_file_list.append(sub_file)

                click.secho(f'分区名{_} : ', nl=False)
                partion_name = input()
                if not len(partion_name):
                    click.secho('分区名不能为空，请重新输入! ', err=False, fg='red')
                    continue
                else:
                    sub_partion_names.append(partion_name)
                    break

        pack_process(file, version)

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            run_pack_func()
        else:
            cli()

    except Exception as e:
        click.echo(e, err=True, fg='red')
        sys.exit(1)

    # pack_func('test', ['ulog.py'], ['user'], 'v0.0.1', 'stm32f4', ['xxx', 'yyy'])
    sys.exit(0)