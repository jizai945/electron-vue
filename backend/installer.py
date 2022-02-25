import os
import shutil

new_dir_name = './dist'
# files = ['runtime_example.c', 'user_example.c'] # 资源文件
files = []

for f in files:
    print(f'copy file: {f}')
    if os.path.isdir('./'+f):
        shutil.copytree(f"./{f}", \
                        f"{new_dir_name}/{f}")  # 前面拷贝到后面
    elif os.path.isfile('./'+f):
        shutil.copyfile(f"./{f}", \
                        f"{new_dir_name}/{f}")  # 前面拷贝到后面
    else:
        print(f'{f} is not exist')