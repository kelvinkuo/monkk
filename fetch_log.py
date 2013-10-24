#module:fetchlog
#date  :Thu Oct 17 16:44:38 2013
#author:kk

# 脚本从所有服务器取回前一天日志，按天归档，目录结构如下

# dir:20131016
#     dir:98.12.105.34
#         file:flashServer.6225.20131016_000001-0.mg.log
#         file:flashServer.6225.20131016_100020-1.mg.log
#     dir:98.12.105.35
#         file:flashServer.7772.20131016_000001-0.mcu.log
#         file:flashServer.7772.20131016_100020-1.mcu.log
#     dir:98.12.105.36
#         file:flashServer.3356.20131016_000001-0.mg.log
#         file:flashServer.3356.20131016_100020-1.mg.log
#     dir:98.12.105.37
#         file:flashServer.8876.20131016_000001-0.mg.log
#         file:flashServer.8876.20131016_100020-1.mg.log

# 日志传输的方案
# 1 在服务器上搭建ftp，日志服务器定时去获取
# 2 视频服务器主动向日志服务器上传日志

# 第二个方案只需要日志服务器搭建ftp服务器，视频服务器需要做一个定时任务脚本

