# DailyVocab

## 下载方法
git clone https://github.com/xyl-27/DailyVocab.git
或直接下载压缩包

## 使用方法
1.在当前路径打开cmd 输入
nssm.exe install DailyVocab
![fig1](https://github.com/xyl-27/public-source/blob/main/DailyVocab/image/image.png)

这一步是为了将DailyVocab.exe添加到windows服务 (Windows服务是一种在后台运行、无需用户交互、以系统级别权限执行的特殊应用程序)

2.将DailyVocab.exe的路径输入到path中点击Install service  
![fig2](https://github.com/xyl-27/public-source/blob/main/DailyVocab/image/image-2.png)

3.在cmd中输入以下命令启动服务,(注意要以管理员身份打开cmd)
nssm.exe start DailyVocab
或者
WIN+R输入services.msc打开服务管理，找到DailyVocab，右键启动

4.打开wallpaper engine
打开壁纸
从URL导入  
![fig3](https://github.com/xyl-27/public-source/blob/main/DailyVocab/image/image-3.png)

URL为http://127.0.0.1:5000/
输入完URL和名称确认就可以使用了

## 停止使用
在cmd中输入以下命令停止服务,(注意要以管理员身份打开cmd)
nssm.exe stop DailyVocab
或者
WIN+R输入services.msc打开服务管理，找到DailyVocab，右键停止

如果要彻底删除服务
nssm.exe remove DailyVocab

## 更换词表
将新词表命名为words.txt替换data/words.txt

## 重置归档词表
直接删除/data/archive.json
