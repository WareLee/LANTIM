# 用于显示层view的消息解析与组装的工具模块
# 自报家门数据格式： self:{username}:{any info}
# 请求广播格式：broadcast:{username}:{info wanted to send}, 注：广播消息根据实际到达client的时间排序
# 单播数据报格式： {time of client msg creating}:{friendusername}:{info wanted to send},注：单播消息的数据顺序由接收客户端负责

# 上下文:
#       剩余工作
#           完成该工具模块
#           完成view层的各种事件