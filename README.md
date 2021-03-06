# LANTIM

## 简述:

Instant messaging software under LAN in Python(use UDP protocol). 

使用Python UDP 实现的局域网下的即时通讯应用。

## DB设计:

> 本应用中对***用户数据信息***的存储，没有使用真正的数据库，而是使用pickle持久化到本地文件中。每个用户的数据信息存储到一个文件中，通过**文件名**区分所属用户。

**用户信息：**指账户信息和好友信息

| id          | username | password   | friends        | groups                 |
| ----------- | -------- | ---------- | -------------- | ---------------------- |
| str：abcd5d | str：Lee | str: 55558 | list:[abcd5d,] | dict:{gname:[abcd5d,]} |

**文件名**: 存储用户数据信息的文件的命名规则  {id}.pickle . (如：lee:abcd5d.pickle, 表示用户名username=='lee'且id==‘abcd5d’ 的信息所在文件)，称之为``用户名相关``文件。

## 功能设计：

O. 用户认证登陆，查看好友列表：这些数据均采用本地持久化方式实现（见上述：DB设计）。

A. 用户一对一聊天：采用UDP单播

B. 多用户（所有在线用户）聊天：采用UDP广播

C. 多个指定用户群聊（就像QQ群）：是功能B的细化和拓展，可采用UDP广播或多播。... ... **暂不实现** 

## 用户界面设计

### 登陆界面：



### 主界面：
![主界面](https://github.com/WareLee/LANTIM/blob/master/159706943.jpg)



## 程序结构设计：

> 一般可以先做一个程序架构设计，然后以此为基础再细化结构设计。但本应用较简单且逻辑清晰，就直接省略了。

* __用户登陆逻辑__：根据用户输入的```username```,```password```，查看DB中是否有相应```用户名相关```的文件，读取文件并验证password。 成功验证后展示用户好友列表，该信息也存储在```用户名相关```的文件中（如上述文件lee:abcd5d.pickle）。

* __所有用户公共聊天__： 采用UDP广播，广播消息。

* __一对一单播逻辑__: 该逻辑的实现需要客户端和服务器端的配合。其服务器的设计采用TFTP的设计思想。

  ![并发UDP服务器](https://github.com/WareLee/LANTIM/blob/master/%E5%B9%B6%E5%8F%91udp%E6%9C%8D%E5%8A%A1%E5%99%A8.png)

  > 注：图1截取自《unix网络编程 第二版》一书。

* __整体client-server架构设计:__

  ![client-server架构设计](https://github.com/WareLee/LANTIM/blob/master/client_server%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1.png)

  ## 版本更新计划：

  v.0.1 当前版本。仅支持局域网下简单文本聊天。

  v.0.2 进程间通信数据结构优化....

  v.1.0 数据顺序性，可靠性保证....

  v.2.0 大文件传输支持...

  

  
