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
docBasicPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/doc-basic")
examplesBasicPath = Path("/Users/xiakangwei/Nutstore/Github/repository/exam-zh/examples-basic")

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
docBasicFiles = ['exam-zh-doc-basic.tex', 'exam-zh-doc-basic.pdf']
examplesBasicFiles = ['00-minimal.tex', '01-first-exam.tex', '02-math-basic.tex']

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
with open(docPath / docFiles[0], 'r') as file:
    content = file.read()
    content = docDateRegex.sub(r'\\newcommand{\\DocDate}{%s}' % (date), content)
    content = docVersionRegex.sub(r'\\newcommand{\\DocVersion}{v%s}' % (version), content)
    with open(docPath / docFiles[0], 'w') as newFile:
        newFile.write(content)

# 更新 doc-basic 手册版本
with open(docBasicPath / docBasicFiles[0], 'r') as file:
    content = file.read()
    content = docDateRegex.sub(r'\\newcommand{\\DocDate}{%s}' % (date), content)
    content = docVersionRegex.sub(r'\\newcommand{\\DocVersion}{v%s}' % (version), content)
    with open(docBasicPath / docBasicFiles[0], 'w') as newFile:
        newFile.write(content)

# 编译

# 先将 working directory 改到 doc 再编译，这样可以使得一些相对路径不依赖 py 的位置
# （其实就是相对路径要相对 tex 文件，所以要到那个目录下）
os.chdir(originPath)
print('\n' + '='*60)
print('开始编译示例文件...')
print('='*60)
for i in range(2):
    print(f'\n[{i+1}/2] 正在编译: {exampleFiles[i]}')
    result = subprocess.run(['latexmk', '-xelatex', exampleFiles[i]])
    if result.returncode != 0:
        print(f'✗ 错误: {exampleFiles[i]} 编译失败 (返回码: {result.returncode})')
        sys.exit(1)
    print(f'✓ {exampleFiles[i]} 编译成功')

# 编译 examples-basic 示例文件
os.chdir(examplesBasicPath)
print('\n' + '='*60)
print('开始编译 basic 示例文件...')
print('='*60)
for i, example_file in enumerate(examplesBasicFiles):
    print(f'\n[{i+1}/{len(examplesBasicFiles)}] 正在编译: {example_file}')
    result = subprocess.run(['latexmk', '-xelatex', example_file])
    if result.returncode != 0:
        print(f'✗ 错误: {example_file} 编译失败 (返回码: {result.returncode})')
        sys.exit(1)
    print(f'✓ {example_file} 编译成功')

os.chdir(docPath)
print('\n' + '='*60)
print('开始编译文档...')
print('='*60)
print(f'\n正在编译: {docFiles[0]}')
LaTeXcompile = subprocess.run(['latexmk', '-xelatex', docFiles[0]])

# 检查编译返回码（0 表示成功，包括文件已是最新的情况）
if LaTeXcompile.returncode != 0:
    print(f'✗ 错误: 文档编译失败 (返回码: {LaTeXcompile.returncode})')
    sys.exit(1)

print(f'✓ 文档编译成功')

# 编译 doc-basic 文档
os.chdir(docBasicPath)
print('\n' + '='*60)
print('开始编译 basic 文档...')
print('='*60)
print(f'\n正在编译: {docBasicFiles[0]}')
LaTeXcompileBasic = subprocess.run(['latexmk', '-xelatex', docBasicFiles[0]])

# 检查编译返回码（0 表示成功，包括文件已是最新的情况）
if LaTeXcompileBasic.returncode != 0:
    print(f'✗ 错误: basic 文档编译失败 (返回码: {LaTeXcompileBasic.returncode})')
    sys.exit(1)

print(f'✓ basic 文档编译成功')

# 复制文件到 release 和 CTAN / exam-zh 并压缩

print('\n' + '='*60)
print('开始复制文件和打包...')
print('='*60)

if True:  # 编译成功后总是执行复制和打包
    # 辅助文件
    print('\n[1/8] 复制辅助文件 (README, CHANGELOG, LICENSE)...')
    for helpFile in helpFiles:
        shutil.copy(originPath / helpFile, ctanPath)
        shutil.copy(originPath / helpFile, releasePath)
    print(f'  ✓ 已复制 {len(helpFiles)} 个辅助文件')

    # sty 和 cls 文件
    print('\n[2/8] 复制 sty 和 cls 文件...')
    for styfile in styfiles:
        shutil.copy(originPath / styfile, ctanTeXPath)
        shutil.copy(originPath / styfile, releasePath)
    shutil.copy(originPath / clsFile, ctanTeXPath)
    shutil.copy(originPath / clsFile, releasePath)
    print(f'  ✓ 已复制 {len(styfiles)} 个 sty 文件和 1 个 cls 文件')

    # doc 文件
    print('\n[3/8] 复制文档文件...')
    for docFile in docFiles:
        shutil.copy(docPath / docFile, ctanDocPath)
    shutil.copy(docPath / docFiles[1], releasePath)
    shutil.copytree(docPath / 'back', ctanDocPath / 'back', dirs_exist_ok=True)
    shutil.copytree(docPath / 'body', ctanDocPath / 'body', dirs_exist_ok=True)
    shutil.copytree(docPath / 'figures', ctanDocPath / 'figures', dirs_exist_ok=True)
    print(f'  ✓ 已复制文档文件和目录 (back, body, figures)')

    # doc-basic 文件
    print('\n[4/8] 复制 basic 文档文件...')
    shutil.copy(docBasicPath / docBasicFiles[1], releasePath)
    print(f'  ✓ 已复制 basic 文档 PDF')

    # 示例文件
    print('\n[5/8] 复制示例文件...')
    for exampleFile in exampleFiles:
        shutil.copy(originPath / exampleFile, ctanExamplesPath)
        shutil.copy(originPath / exampleFile, releasePath)
    print(f'  ✓ 已复制 {len(exampleFiles)} 个示例文件')

    # basic 示例文件
    print('\n[6/8] 复制 basic 示例文件...')
    for example_file in examplesBasicFiles:
        # 复制 .tex 源文件
        shutil.copy(examplesBasicPath / example_file, releasePath)
        # 复制生成的 PDF 文件
        pdf_file = example_file.replace('.tex', '.pdf')
        shutil.copy(examplesBasicPath / pdf_file, releasePath)
    print(f'  ✓ 已复制 {len(examplesBasicFiles)} 个 basic 示例文件（含 .tex 和 .pdf）')

    # 删除之前的压缩包
    print('\n[7/8] 清理旧的压缩包...')
    # 删除 release 目录的压缩包
    if list(releasePath.glob('*.zip')):
        old_zip = list(releasePath.glob('*.zip'))[0]
        send2trash.send2trash(old_zip)
        print(f'  ✓ 已删除旧的 release 压缩包')
    # 删除 CTAN 目录的压缩包
    if list(ctanZipPath.glob('*.zip')):
        old_zip = list(ctanZipPath.glob('*.zip'))[0]
        send2trash.send2trash(old_zip)
        print(f'  ✓ 已删除旧的 CTAN 压缩包')

    # 压缩
    print('\n[8/8] 创建压缩包...')

    # 压缩 release
    print(f'  正在创建 {releaseZipName}...')
    os.chdir(releasePath)
    with zipfile.ZipFile(releasePath / releaseZipName, 'w') as releaseZip:
        for file in os.listdir(releasePath):
            # 不把 zip 去掉的话会循环压缩
            if not file.endswith('zip') and not file.endswith('DS_Store') and not file.startswith('__MACOSX/'):
                releaseZip.write(file)
        for file in releaseZip.namelist():
            if file.endswith('DS_Store'):
                print('  ✗ 警告: 发现 .DS_Store 文件，请检查！')
    print(f'  ✓ {releaseZipName} 创建成功')

    # 压缩 CTAN / exam-zh
    print(f'  正在创建 {ctanZipName}...')
    os.chdir(ctanZipPath)
    with zipfile.ZipFile(ctanZipName, 'w') as ctanZip:
        file_count = 0
        for path, dirnames, filenames in os.walk(ctanPath):
            relativePath = path.replace(str(ctanZipPath), '')  # 把父目录路径去掉，剩下相对路径
            for filename in filenames:
                if not filename.endswith('DS_Store') and not filename.startswith('__MACOSX/'):
                    #1 表示原位置， #2 表示目标位置
                    ctanZip.write(os.path.join(path, filename), os.path.join(relativePath, filename))
                    file_count += 1
        for file in ctanZip.namelist():
            if file.endswith('DS_Store'):
                print('  ✗ 警告: 发现 .DS_Store 文件，请检查！')
    print(f'  ✓ {ctanZipName} 创建成功 (包含 {file_count} 个文件)')

# 复制版本和时间信息到剪切板

pyperclip.copy('v' + version + ' - ' + date)

print('\n' + '='*60)
print('✓ 构建完成！')
print('='*60)
print(f'\n版本信息: v{version} - {date}')
print(f'已复制到剪贴板: v{version} - {date}')
print(f'\nRelease 包: {releasePath / releaseZipName}')
print(f'CTAN 包: {ctanZipPath / ctanZipName}')
print('\n构建成功！ 🎉\n')
