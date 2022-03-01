import os
import shutil

copy_to_path = './dist'
copy_src_files = ['example']# 资源文件

for f in copy_src_files:
    print(f'copy file: {f}')
    if os.path.isdir('./'+f):
        # 尝试删除原本的文件
        try:
            # 删除
            shutil.rmtree(f"{copy_to_path}/{f}")
        except Exception as e:
            print(e)
        shutil.copytree(f"./{f}", \
                        f"{copy_to_path}/{f}")  # 前面拷贝到后面
        print(f'copy file:[{f"{copy_to_path}/{f}"}] sucess')
    elif os.path.isfile('./'+f):
        shutil.copyfile(f"./{f}", \
                        f"{copy_to_path}/{f}")  # 前面拷贝到后面
        print(f'copy file:[{f"{copy_to_path}/{f}"}] sucess')
    else:
        print(f'{f} is not exist')