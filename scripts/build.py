#! python3
# build.py
# 1. 更新 sty、cls 和手册的版本并编译手册
# 2. 将文件传输到 CTAN 目录并压缩
# 3. 将文件传输到 release 目录并压缩

import os
import shutil
import subprocess
import sys
from pathlib import Path
import datetime
import re
import zipfile

import pyperclip
import send2trash
import pyinputplus as pyip

# 几个目录常量
originPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh")
docPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/doc")
ctanZipPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/CTAN")
ctanPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/CTAN/exam-zh")
ctanDocPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/CTAN/exam-zh/doc")
ctanTeXPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/CTAN/exam-zh/tex")
ctanExamplesPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/CTAN/exam-zh/examples")
releasePath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/release")

# 版本
try:
    version = str(sys.argv[1])
    # 让用户确认版本的输入
    while True:
        print('New version will be: v' + version + '. Are you sure?')
        answer = pyip.inputYesNo()
        if answer == 'no':
            version = input('Please type the new version: ')
            continue
        else:
            break
except IndexError:
    version = input('Please type the new version: ')
    # 让用户确认版本的输入
    while True:
        print('New version will be: v' + version + '. Are you sure?')
        answer = pyip.inputYesNo()
        if answer == 'no':
            print('Please type the new version: ')
            version = input()
            continue
        else:
            break

# 时间
dateNow = datetime.datetime.now()
# 将月份和日期都变成两位数，否则编译会报错
month = dateNow.month
month = f"{month:02d}"
day = dateNow.day
day = f"{day:02d}"
date = str(dateNow.year) + '-' + str(month) + '-' + str(day)

# 压缩包名称
ctanZipName = 'exam-zh.zip'
releaseZipName = 'exam-zh-v' + version + '.zip'

# 1. 更新 sty 和 cls 的版本

# 正则表达式
styDateRegex = re.compile(r'\\ProvidesExplPackage\s\{.*\}\s\{(\d{4}-\d{1,2}-\d{1,2})\}\s\{v(\d+\.\d+\.?\d*)\}')
clsDateRegex = re.compile(r'\\ProvidesExplClass\s\{.*\}\s\{(\d{4}-\d{1,2}-\d{1,2})\}\s\{v(\d+\.\d+\.?\d*)\}')
docDateRegex = re.compile(r'\\newcommand\{\\DocDate\}\{(\d{4}-\d{1,2}-\d{2})\}')
docVersionRegex = re.compile(r'\\newcommand\{\\DocVersion\}\{v(\d+\.\d+\.?\d*)\}')

# 将 originPath 目录下的所有 sty 后缀文件名加入 styfiles 中
styfiles = []
for styfile in originPath.glob('*.sty'):
    styfiles.append(str(styfile))
# 因为上面的遍历，styfile 已经是绝对路径了，但为了下面的替换，要改为文件名
for i in range(len(styfiles)):
    temp = styfiles[i].split('/')
    styfiles[i] = temp[-1]
clsFile = 'exam-zh.cls'
docFiles = ['exam-zh-doc.tex', 'exam-zh-doc.pdf', 'exam-zh-doc-setup.tex', 'xdyydoc.cls']
exampleFiles = ['example-single.tex', 'example-multiple.tex', 'example-single.pdf', 'example-multiple.pdf']
helpFiles = ['CHANGELOG.md', 'README.md', 'LICENSE']

# 替换 sty 中的时间和版本
for styfile in styfiles:
    with open(originPath / styfile, 'r') as file:
        content = file.read()
        pre, mid, after = styfile.partition('.')
        content = styDateRegex.sub(r'\\ProvidesExplPackage {%s} {%s} {v%s}' % (pre, date, version), content)
        with open(originPath / styfile, 'w') as newFile:
            newFile.write(content)

# 替换 cls 中的时间和版本
with open(originPath / clsFile, 'r') as file:
    content = file.read()
    content = clsDateRegex.sub(r'\\ProvidesExplClass {exam-zh} {%s} {v%s}' % (date, version), content)
    with open(originPath / clsFile, 'w') as newFile:
        newFile.write(content)

# 2. 更新手册版本并编译
1
with open(docPath / docFiles[0], 'r') as file:
    content = file.read()
    content = docDateRegex.sub(r'\\newcommand{\\DocDate}{%s}' % (date), content)
    content = docVersionRegex.sub(r'\\newcommand{\\DocVersion}{v%s}' % (version), content)
    with open(docPath / docFiles[0], 'w') as newFile:
        newFile.write(content)

# 编译

# 先将 working directory 改到 doc 再编译，这样可以使得一些相对路径不依赖 py 的位置
# （其实就是相对路径要相对 tex 文件，所以要到那个目录下）
os.chdir(originPath)
for i in range(2):
    subprocess.run(['latexmk', '-xelatex', exampleFiles[i]])  # 编译示例文件
os.chdir(docPath)
LaTeXcompile = subprocess.run(['latexmk', '-xelatex', docFiles[0]], capture_output=True)

out = LaTeXcompile.stdout

# 复制文件到 release 和 CTAN / exam-zh 并压缩

if out != '':  # 表示编译已经结束
    # 辅助文件
    for helpFile in helpFiles:
        shutil.copy(originPath / helpFile, ctanPath)
        shutil.copy(originPath / helpFile, releasePath)
    # sty 和 cls 文件
    for styfile in styfiles:
        shutil.copy(originPath / styfile, ctanTeXPath)
        shutil.copy(originPath / styfile, releasePath)
    shutil.copy(originPath / clsFile, ctanTeXPath)
    shutil.copy(originPath / clsFile, releasePath)
    # doc 文件
    for docFile in docFiles:
        shutil.copy(docPath / docFile, ctanDocPath)
    shutil.copy(docPath / docFiles[1], releasePath)

    shutil.copytree(docPath / 'back', ctanDocPath / 'back', dirs_exist_ok=True)
    shutil.copytree(docPath / 'body', ctanDocPath / 'body', dirs_exist_ok=True)
    shutil.copytree(docPath / 'figures', ctanDocPath / 'figures', dirs_exist_ok=True)

    for exampleFile in exampleFiles:
        shutil.copy(originPath / exampleFile, ctanExamplesPath)
        shutil.copy(originPath / exampleFile, releasePath)

    # 删除之前的压缩包
    # 删除 release 目录的压缩包
    if list(releasePath.glob('*.zip')):
        send2trash.send2trash(list(releasePath.glob('*.zip'))[0])
    # 删除 CTAN 目录的压缩包
    if list(ctanZipPath.glob('*.zip')):
        send2trash.send2trash(list(ctanZipPath.glob('*.zip'))[0])

    # 压缩

    # 压缩 release
    os.chdir(releasePath)
    with zipfile.ZipFile(releasePath / releaseZipName, 'w') as releaseZip:
        for file in os.listdir(releasePath):
            # 不把 zip 去掉的话会循环压缩
            if not file.endswith('zip') and not file.endswith('DS_Store') and not file.startswith('__MACOSX/'):
                releaseZip.write(file)
        for file in releaseZip.namelist():
            if file.endswith('DS_Store'):
                print('Something went wrong! Check it!')

    # 压缩 CTAN / exam-zh
    os.chdir(ctanZipPath)
    with zipfile.ZipFile(ctanZipName, 'w') as ctanZip:
        for path, dirnames, filenames in os.walk(ctanPath):
            relativePath = path.replace(str(ctanZipPath), '')  # 把父目录路径去掉，剩下相对路径
            # print(path)
            # print(relativePath)
            # print()
            for filename in filenames:
                if not filename.endswith('DS_Store') and not filename.startswith('__MACOSX/'):
                    #1 表示原位置， #2 表示目标位置
                    ctanZip.write(os.path.join(path, filename), os.path.join(relativePath, filename))
        for file in ctanZip.namelist():
            if file.endswith('DS_Store'):
                print('Something went wrong! Check it!')

# 复制版本和时间信息到剪切板

pyperclip.copy('v' + version + ' - ' + date)
