import json
import os, sys
try:
    from modules.crc32 import *
except:
    from crc32 import *

file_name_list = ['runtime', 'bsp', 'user', 'upgrade'] # 子文件名字列表
HEAD = 'PUDUMCUFILE'
file_info_json_len = 2*1024     # 文件描述信息json字符串长度  这里的长度是在文件中的最大长度，不是字符串实际有效长度
file_attach_str = ''
file_attach_json_len = 3*1024   # 附加数据json字符串长度 
json_str_end = '‖'              # json字符串结束符

def check_file(path:str) -> bool:
    '''检查文件路径是否合法'''
    return os.path.isfile(path)

def get_file_size(path:str) -> int:
    '''获取文件大小'''
    if check_file(path):
        return os.path.getsize(path)
    return 0

def get_file_list_crc(file_list:list) -> int:
    '''获取列表文件crc'''
    data = bytes()
    for fi in file_list:
        with open(fi, 'rb') as f:
            data += f.read()

    return crc32_bytes(data)

def generate_describe_json(cfg) -> str:
    '''生成文件描述信息'''

    info_dict = dict()
    info_dict['fver'] = cfg['data']['protocolVersion']
    info_dict['name'] = cfg['data']['fileName']
    info_dict['ver'] = cfg['data']['version']
    size = 0
    sub_file_list = []
    for fl in file_name_list:
        size += get_file_size(cfg['data'][fl])
        sub_file_list.append(cfg['data'][fl])
    
    # 判断加密方式
    if cfg['data']['encryption'] == '无':
        info_dict['csize'] = size                                   # 加密后大小, 暂无加密
        info_dict['osize'] = size                                   # 原始大小
        info_dict['ccrc'] =  get_file_list_crc(sub_file_list)       # 加密后crc 暂无加密
        info_dict['ocrc'] = info_dict['ccrc']                       # 原始crc

    file_log_len = len(cfg['data']['log'])
    info_dict['content_pos'] = len(HEAD) + 4 + 4 + file_info_json_len + file_log_len + file_attach_json_len
    if file_log_len != 0 : # 判断日志区是否存在
        info_dict['log'] = dict()
        info_dict['log']['pos'] = len(HEAD) + 4 + 4 + file_info_json_len
        info_dict['log']['size'] = file_log_len
        info_dict['log']['encrypted'] = True if cfg['data']['encryption'] != '无' else False
        info_dict['log']['crc'] = crc32_bytes(bytes(cfg['data']['log'], encoding = 'utf-8'))

    info_dict['attach'] = dict()
    info_dict['attach']['pos'] = len(HEAD) + 4 + 4 + file_info_json_len + file_log_len
    info_dict['attach']['size'] = len(file_attach_str.split(json_str_end)[0])
    info_dict['attach']['encrypted'] = True if cfg['data']['encryption'] != '无' else False
    info_dict['attach']['crc'] = crc32_bytes(bytes(file_attach_str.split(json_str_end)[0], encoding = 'utf-8'))

    json_str = json.dumps(info_dict, ensure_ascii=False)
    use_size = len(json_str.encode('utf-8'))
    if len(json_str.encode('utf-8')) > file_info_json_len + len(json_str_end.encode('utf-8')) + 1:
        print(f'file info json len to long: {use_size}')
        return 'err' + json_str_end + ' ' * (file_info_json_len - len('err'.encode('utf-8')) - len(json_str_end.encode('utf-8')) - 1) + '\n'

    # 字符串不满长度，填充空格
    
    json_str += json_str_end
    json_str += ' ' * (file_info_json_len - use_size - len(json_str_end.encode('utf-8')) - 1)
    json_str += '\n'

    return json_str
 
def generate_attach_json(cfg:dict) -> str:
    '''生成附件数据'''
    global file_attach_json_len

    offset = len(HEAD) + 4 + 4 + file_info_json_len + len(cfg['data']['log']) + file_attach_json_len

    attach = dict()
    attach['img_cnt'] = len(file_name_list)
    attach['partion_table'] = dict()

    for idx, fi in enumerate(file_name_list):
        attach['partion_table'][fi] = dict()
        attach['partion_table'][fi]['label'] = fi
        attach['partion_table'][fi]['is_bootable'] = True
        attach['partion_table'][fi]['start_addr'] = int(cfg['data'][f'{fi}Start'], 16)
        next_addr = 0x08080000 if idx == (len(file_name_list)-1) else int(cfg['data'][f'{file_name_list[idx+1]}Start'], 16)
        attach['partion_table'][fi]['size'] = next_addr - int(cfg['data'][f'{fi}Start'], 16)

    if cfg['data']['depFlag'] == True:
        attach['deps'] = dict()
        attach['deps']['mcu_model'] = cfg['data']['deps']['mcu_model']
        attach['deps']['hver'] = list()
        for hv in cfg['data']['deps']['hver']:
            attach['deps']['hver'].append(hv['value'])
        attach['deps']['prj'] = cfg['data']['deps']['prj']
        attach['deps']['btype'] = cfg['data']['deps']['btype']
        attach['deps']['func'] = cfg['data']['deps']['func']

    for fi in file_name_list:
        attach['img_list'] = list()
        attach['img_list'].append({})
        attach['img_list'][-1]['partion_label'] = fi
        attach['img_list'][-1]['version'] = cfg['data'][f'{fi}Version']
        file_size = get_file_size(cfg['data'][fi])
        attach['img_list'][-1]['osize'] = file_size
        attach['img_list'][-1]['ocrc'] = get_file_list_crc([cfg['data'][fi]])
        if cfg['data']['encryption'] == '无': # 判断加密方式
           attach['img_list'][-1]['csize'] = attach['img_list'][-1]['osize']
           attach['img_list'][-1]['ccrc'] = attach['img_list'][-1]['ocrc']

        # 现在默认都是非块传输
        attach['img_list'][-1]['fpos'] = {'pos':offset, 'size':file_size}
        offset += file_size

    json_str = json.dumps(attach, ensure_ascii=False)
    use_size = len(json_str.encode('utf-8'))
    if use_size > file_attach_json_len + len(json_str_end.encode('utf-8')) + 1:
        print(f'file attach json len to long: {use_size}')
        return 'err' + json_str_end + ' ' * (file_attach_json_len - len('err'.encode('utf-8')) - len(json_str_end.encode('utf-8')) - 1) + '\n'

    # 字符串不满长度，填充空格
    json_str += json_str_end
    json_str += ' ' * (file_info_json_len - use_size - len(json_str_end.encode('utf-8')) - 1)
    json_str += '\n'

    return json_str

def start_pack(cfg:dict) -> bool:
    '''开始打包'''
    global file_attach_str

    file_log_str = cfg['data']['log']
    file_attach_str = generate_attach_json(cfg)
    sub_file_bytes = bytes()
    file_describe_str = generate_describe_json(cfg) # 描述信息需要依据日志和附加信息生成
    file_describe_len =  len(file_describe_str.split(json_str_end)[0]).to_bytes(4, byteorder='little', signed=False)
    file_describe_crc = crc32_bytes(bytes(file_describe_str.split(json_str_end)[0], encoding='utf-8')).to_bytes(4, byteorder='little', signed=False)

    for fl in file_name_list:   
        with open(cfg['data'][fl], 'rb') as f:
            sub_file_bytes += f.read()

    file_bytes = HEAD.encode('utf-8') + \
                 file_describe_len + \
                 file_describe_crc + \
                 file_describe_str.encode('utf-8') + \
                 file_log_str.encode('utf-8') + \
                 file_attach_str.encode('utf-8') + \
                 sub_file_bytes   

    with open(cfg['target'], 'wb+') as f:
        f.write(file_bytes)

    return True