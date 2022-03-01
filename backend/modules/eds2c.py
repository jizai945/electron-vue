from asyncore import write
from doctest import Example
import os
import configparser
import re
import toml
try:
    from modules.runtime_example import runtime_txt
    from modules.user_example import user_txt
except:
    from runtime_example import runtime_txt
    from user_example import user_txt

'''
    ini解析参考:  https://www.cnblogs.com/dingzy1972/p/14806151.html
'''

eds_data_type = {1: {'len':1, 'name': 'boolean'},
                2: {'len':1, 'name': 'INTEGER8'},
                3: {'len':2, 'name': 'INTEGER16'},
                4: {'len':4, 'name': 'INTEGER32'},
                5: {'len':1, 'name': 'UNS8'},
                6: {'len':2, 'name': 'UNS16'},
                7: {'len':4, 'name': 'UNS32'},
                8: {'len':4, 'name': 'REAL32'},
                9: {'len':32, 'name': 'visible_string'},
                10: {'len':32, 'name': 'octet_string'},
                11: {'len':32, 'name': 'unicode_string'}}

# 重写optionxform函数 解决解析时不区分大小写的问题
class myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    # 这里重写了optionxform方法，直接返回选项名
    def optionxform(self, optionstr):
        return optionstr

class EdsException(Exception):
    pass

class EdsToC():
    def __init__(self, eds_path: str, c_path: str, user_path: str) -> None:
        self.eds =  eds_path
        self.c = c_path
        self.user_c = user_path
        self.cfg = myconf()
        self.err = None
        self.toml_cfg = None
        self._idx_list = []
        try:
            ret = self.cfg.read(self.eds)
            if ret == []:
                self.err = EdsException('[ERR]:eds文件有问题')
        except Exception as e:
            self.err = e

    def __get_idx_list(self) -> list:
        '''获取索引的列表'''
        if len(self._idx_list):
            return self._idx_list

        sections = ['MandatoryObjects', 'ManufacturerObjects', 'OptionalObjects']
        for section in sections:
            for key in self.cfg.options(section):
                if key == 'SupportedObjects':
                    continue
                # print(f'{key} --- {self.cfg.get(section, key).replace("0x", "")}')
                self._idx_list.append(self.cfg.get(section, key).replace('0x', ''))
        
        self._idx_list.sort()
        # print(self._idx_list)
        return self._idx_list

    def __get_idx_sublen(self, idx:str) -> int:
        '''
        获得索引下子索引的个数  
        sub0,sub1...subn -> return n+1
        '''
        if self.err != None:
            raise self.err
        i = 0
        while True:
            if f'{idx}sub{i}' not in self.cfg.sections():
                return i
            i += 1
        
    def __get_idx_subdatalen(self, section:str, sub_len:int = -1) -> int:
        '''获取子索引数据的长度'''
        if sub_len == -1:
            sub_len = self.__get_idx_sublen(section)

        data_len =  int(self.cfg.get(f'{section}sub0', "DefaultValue"), 16) # 获得子索引数据长度  如果为0则需要实际判断
        if data_len == 0:
            return sub_len-1
            # for i in range(1, sub_len):
            #     data_len += eds_data_type[int(self.cfg.get(f'{section}sub{i}', "DataType"), 16)]['len']

        return data_len
        

    def __convert_param_init(self, src:str, type:str = 'runtime') -> str:
        '''OD_PARAM_INIT'''

        write = '' 
        src_idx = self.__get_idx_list()
        filter_idx = [idx for idx in src_idx if self.__judge_idx(idx, type)]
        for idx, section in enumerate(filter_idx):
            # print(section)    
            obj_type = int(self.cfg.get(section, 'ObjectType'))
            notes = f'\t/* index 0x{section} :\t {self.cfg.get(section, "ParameterName")}. */'
            last_ch = '' if idx == len(filter_idx)-1 else ','
            last_n = '' if idx == len(filter_idx)-1 else '\n\t'

            if obj_type == 7:
                default_val = self.cfg.get(section, "DefaultValue")
                default_val = default_val.replace('$NODEID+', '')
                if '0x' not in default_val:
                    default_val = hex(int(default_val))
                write += f'{default_val}{last_ch}{notes}\\\{last_n}'
            elif obj_type == 8 or obj_type == 9: # 8 --- array  / 9 --- record
                # 获得sub的个数
                sub_len = self.__get_idx_sublen(section)
                if sub_len <= 0:
                    raise EdsException(f'[ERR]: {section}子索引个数有问题')
                data_len =  self.__get_idx_subdatalen(section, sub_len)
                write += f'{hex(data_len).upper()}, '
                write += '{' if obj_type == 9 else ''
                for i in range(1, sub_len):
                    sub_section = f'{section}sub{i}'
                    data_type = int(self.cfg.get(sub_section, "DataType"), 16)
                    default_val = self.cfg.get(sub_section, "DefaultValue").replace('$NODEID+', '')
                    if data_type == 9:
                        write += '\"'+ default_val + '\"'
                    elif data_type == 0x0A:
                        write += f'{default_val}'
                    else:
                        if not self.cfg.has_option(sub_section, 'size'):
                            write += default_val
                        else:
                            write += '{'+ default_val + '}'
                    
                    if i == sub_len-1:
                        write += '}' if obj_type == 9 else ''
                    write += ', ' if (i != sub_len-1 or idx != len(filter_idx)-1) else ''
                write += f'{notes}\\\{last_n}'

            else:
                raise EdsException('[ERR]: 暂时无法处理的对象类型')

        return re.sub("/(.*)OD_PARAM_INIT(.*)/", write, src)

    def __convert_typedef_struct(self, src:str, type:str = 'runtime')->str:
        '''typedef struct'''
        write = ''
        src_idx = self.__get_idx_list()
        filter_idx = [idx for idx in src_idx if self.__judge_idx(idx, type)]
        last_num = len(filter_idx)-1
        for idx, section in enumerate(filter_idx):
            notes = f'/* index 0x{section} :\t{self.cfg.get(section, "ParameterName")} */\n\t'
            if self.cfg.has_option(section, 'DataType'):
                data_type = eds_data_type[int(self.cfg.get(section, "DataType"), 16)]['name']
                write += f'{notes}{data_type} slaveApp_obj{section};'
                write += '\n\t'
            else:
                parent_type = 'UNS8'
                parent_name = f'SlaveApp_highestSubIndex_obj{section}'
                parent_notes = f' /* number of subindex - {self.__get_idx_subdatalen(section)} */'
                sub_str = ''
                sub_len = self.__get_idx_sublen(section)
                for i in range(1, sub_len):
                    sub_section = f'{section}sub{i}'
                    sub_type = int(self.cfg.get(sub_section, 'DataType'), 16)
                    sub_name = self.cfg.get(sub_section, 'ParameterName')
                    sub_name = re.sub(r'\W+', '_', sub_name)
                    if sub_type == 9 or sub_type == 0x0a:
                        if self.cfg.has_option(sub_section, 'size'):
                            sub_buf_size = self.cfg.get(sub_section, 'size')
                        else:
                            sub_buf_size = eds_data_type[sub_type]["len"] // 1 # char
                        sub_str += f'UNS8 SlaveApp_obj{section}_{sub_name}[{sub_buf_size}];\n\t'
                    else:
                        if not self.cfg.has_option(sub_section, 'size'):
                            sub_str += f'{eds_data_type[sub_type]["name"]} SlaveApp_obj{section}_{sub_name};\n\t'
                        else: # 数组
                            sub_buf_size = int(self.cfg.get(sub_section, 'size')) // eds_data_type[sub_type]['len']
                            sub_str += f'{eds_data_type[sub_type]["name"]} SlaveApp_obj{section}_{sub_name}[{sub_buf_size}];\n\t'

                write += f'{notes}{parent_type} {parent_name};{parent_notes}\n\t{sub_str}'

        write = write[:-2] # 去掉末尾的\n\t
        return re.sub("/(.*)typedef struct(.*)/", write, src)

    def __convert_object_dictionary(self, src:str, type:str = 'runtime') -> str:
        '''object dictionary'''
        write = ''
        line_tab = '\t'*5
        src_idx = self.__get_idx_list()
        filter_idx = [idx for idx in src_idx if self.__judge_idx(idx, type)]
        for idx, section in enumerate(filter_idx):
            sub_len = self.__get_idx_sublen(section)
            null_str = f'{line_tab}\tNULL,\n' * (1 if sub_len == 0 else sub_len)
            null_str = null_str[:-1]
            if sub_len == 0:
                data_type = eds_data_type[int(self.cfg.get(section, "DataType"), 16)]["name"]
                sub_index_arr = '{ ' + f'{self.cfg.get(section, "AccessType")}, {data_type}, sizeof({data_type}), (void*)&od.SlaveApp_obj{section}'+' }'
            else:
                data_type = eds_data_type[int(self.cfg.get(f'{section}sub0', "DataType"), 16)]["name"]
                sub_index_arr = '{ ' + f'{self.cfg.get(f"{section}sub0", "AccessType")}, {data_type}, sizeof({data_type}), (void*)&od.SlaveApp_highestSubIndex_obj{section}'+' },'
            if sub_len != 0:
                for i in range(1, sub_len):
                    sub_section = f'{section}sub{i}'
                    sub_acc = self.cfg.get(sub_section, 'AccessType')
                    sub_data_type_num = int(self.cfg.get(sub_section, 'DataType'), 16)
                    sub_data_type = eds_data_type[sub_data_type_num]['name']
                    sub_name = self.cfg.get(sub_section, 'ParameterName')
                    sub_name = re.sub(r'\W+', '_', sub_name)
                    
                    if sub_data_type_num == 9 or sub_data_type_num == 0x0a:
                        if self.cfg.has_option(sub_section, 'size'):
                            sub_data_size = self.cfg.get(sub_section, 'size')
                        else:
                            sub_data_size = eds_data_type[sub_data_type_num]['len']
                        sub_index_arr += f'\n{line_tab}\t' + '{ ' + f'{sub_acc}, {sub_data_type}, {sub_data_size}, (void*)&od.SlaveApp_obj{section}_{sub_name}' + ' },'
                    else:
                        sub_index_arr += f'\n{line_tab}\t' +'{ ' + f'{sub_acc}, {sub_data_type}, sizeof({sub_data_type}), (void*)&od.SlaveApp_obj{section}_{sub_name}' + ' },'
                    

            write += f'/* index 0x{section} : \t {self.cfg.get(section, "ParameterName")} */'
            write += \
f'''
{line_tab}static ODCallback_t SlaveApp_Index{section}_callbacks[] =
{line_tab}{"{"}
{null_str}
{line_tab}{"}"};
{line_tab}const subindex SlaveApp_Index{section}[] = 
{line_tab}{"{"}
{line_tab}\t{sub_index_arr}
{line_tab}{"}"};
'''
        write = write[:-1]
        return re.sub("/(.*)OBJECT DICTIONARY(.*)/", write, src)

    def __convert_indextable(self, src:str, type:str = 'runtime') -> str:
        '''index table'''
        write = ''
        src_idx = self.__get_idx_list()
        filter_idx = [idx for idx in src_idx if self.__judge_idx(idx, type)]
        for idx, section in enumerate(filter_idx):
            write += '{ ' + f'(subindex*)SlaveApp_Index{section}, sizeof(SlaveApp_Index{section})/sizeof(SlaveApp_Index{section}[0]), 0x{section}' + ' },\n\t'

        write = write[:-1]
        return re.sub("/(.*)indextable(.*)/", write, src)

    def __convert_scanindexod(self, src:str, type:str = 'runtime') -> str:
        '''scan index od'''
        write = ''
        self.quick_dict = dict() # 建立字典方便后面处理
        keys = ['1200-127f', '1280-13ff', '1400-15ff', '1600-17ff', '1800-19ff', '1A00-1BFF', '1FA0-1FCF', '1FD0-1FFF']
        for k in keys:
            self.quick_dict[k] = list()

        src_idx = self.__get_idx_list()
        filter_idx = [idx for idx in src_idx if self.__judge_idx(idx, type)]
        for idx, section in enumerate(filter_idx):
            write += f'\t\t\tcase 0x{section}: i = {idx}; *callbacks = SlaveApp_Index{section}_callbacks; break;\n'
            section_num = int(section, 16)
            if section_num >= 0x1200 and section_num <= 0x127f:
                self.quick_dict['1200-127f'].append(idx)
            elif section_num <= 0x13ff:
                self.quick_dict['1280-13ff'].append(idx)
            elif section_num <= 0x15ff:
                self.quick_dict['1400-15ff'].append(idx)
            elif section_num <= 0x17ff:
                self.quick_dict['1600-17ff'].append(idx)
            elif section_num <= 0x19ff:
                self.quick_dict['1800-19ff'].append(idx)
            elif section_num <= 0x1BFF:
                self.quick_dict['1A00-1BFF'].append(idx)
            elif section_num <= 0x1FCF:
                self.quick_dict['1FA0-1FCF'].append(idx)  
            elif section_num <= 0x1FFF:
                self.quick_dict['1FD0-1FFF'].append(idx)  

        write = write[:-1]
        return re.sub("/(.*)scan index od(.*)/", write, src)

    def __convert_quick_first(self, src:str) -> str:
        '''quick_index SlaveApp_firstIndex'''
        write = ''
        keys = ['1200-127f', '1280-13ff', '1400-15ff', '1600-17ff', '1800-19ff', '1A00-1BFF', '1FA0-1FCF', '1FD0-1FFF']
        notes = ['SDO_SVR', 'SDO_CLT', 'PDO_RCV', 'PDO_RCV_MAP', 'PDO_TRS', 'PDO_TRS_MAP', 'PDO_TRS_MAP', 'PDO_TRS_MAP']
        for i, k in enumerate(keys):
            self.quick_dict[k].sort()
            write += ('0' if len(self.quick_dict[k]) == 0 else str(self.quick_dict[k][0]) )
            write += f', /* {notes[i]} */\n\t'

        write = write[:-2]
        return re.sub("/(.*)quick first(.*)/", write, src)

    def __convert_quick_last(self, src:str) -> str:
        '''quick_index SlaveApp_lastIndex'''
        write = ''
        keys = ['1200-127f', '1280-13ff', '1400-15ff', '1600-17ff', '1800-19ff', '1A00-1BFF', '1FA0-1FCF', '1FD0-1FFF']
        notes = ['SDO_SVR', 'SDO_CLT', 'PDO_RCV', 'PDO_RCV_MAP', 'PDO_TRS', 'PDO_TRS_MAP', 'PDO_TRS_MAP', 'PDO_TRS_MAP']
        for i, k in enumerate(keys):
            self.quick_dict[k].sort()
            write += ('0' if len(self.quick_dict[k]) == 0 else str(self.quick_dict[k][-1]) )
            write += f', /* {notes[i]} */\n\t'

        write = write[:-2]
        return re.sub("/(.*)quick last(.*)/", write, src)

    def __get_runtime_index(self) -> list:
        '''获取runtime中需要的index'''
        if self.toml_cfg == None:
            try:
                read = toml.load('./example/canopen.toml')
            except:
                read = toml.load('./backend/dist/example/canopen.toml') # 生成环境
            self.toml_cfg = read
            # print(read)

        return self.toml_cfg['runtime']['index']

    def __judge_idx(self, idx:str, type:str) -> bool:
        '''判断idx和类型判断是否是需要生成的'''
        if type == 'runtime': 
            if int(idx, 16) in self.__get_runtime_index():
                return True
            return False
        else:
            if int(idx, 16) not in self.__get_runtime_index():
                return True
            return False

    def start_convert(self) -> bool:
        '''开始转换'''
        try:
            if self.err != None:
                raise self.err

            # ------------------ 根据c源文件 实测收到加密的影响 ----------------------
            # examples = ['../example/runtime_example.c', '../example/user_example.c']
            # c_out = [self.c, self.user_c]

            # for i in range(len(examples)):
            #     with open(examples[i], 'r', encoding='utf-8') as f:
            #         read = f.read()
            #         read = self.__convert_param_init(read) 
            #         read = self.__convert_typedef_struct(read) 
            #         read = self.__convert_object_dictionary(read)
            #         read = self.__convert_indextable(read)
            #         read = self.__convert_scanindexod(read)
            #         read = self.__convert_quick_first(read)
            #         read = self.__convert_quick_last(read)
            #         with open(c_out[i], 'w', encoding='utf-8') as f2:
            #             f2.write(read)

            #  -------------------------- 根据py字符串 --------------------------------
            examples = [runtime_txt, user_txt]
            types = ['runtime', 'user']
            c_out = [self.c, self.user_c]
            for i in range(len(examples)):
                read = examples[i]
                read = self.__convert_param_init(read, types[i]) 
                read = self.__convert_typedef_struct(read, types[i]) 
                read = self.__convert_object_dictionary(read, types[i])
                read = self.__convert_indextable(read, types[i])
                read = self.__convert_scanindexod(read, types[i])
                read = self.__convert_quick_first(read)
                read = self.__convert_quick_last(read)
                with open(c_out[i], 'w', encoding='utf-8') as f2:
                    f2.write(read) 

        except Exception as e:
            print(f'\033[0;31;40m{e}\033[0m')
            self.err = e
            return False

        print('\033[0;32;40mconvert sucess\033[0m')
        return True

    def dfs_file(self):
        '''遍历打印key value'''
        try:
            if self.err != None:
                raise self.err
            for section in self.cfg.sections():
                print(f'section --- {section}')
                for key in self.cfg.options(section):
                    print(f'\t {key} --- {self.cfg.get(section, key)}')
        except Exception as e:
            print(e)

    def get_err(self) -> str:
        return '' if self.err == None else str(self.err)

    def toml_test(self):
        try:
            read = toml.load('./example/canopen.toml') # 开发环境
        except:
            read = toml.load('./backend/dist/example/canopen.toml') # 生成环境
        print(read)

if __name__ == '__main__':
    e = EdsToC('C:\\Users\\Wang\\Desktop\\demo2.eds', './runtime_test.c', './user_test.c')
    # e.dfs_file()
    e.start_convert()
    # e.toml_test()