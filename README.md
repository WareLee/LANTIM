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

**文件名**: 存储用户数据信息的文件的命名规则  {id}.pickle . (如：lee:abcd5d.pickle, 表示用户名username=='lee'且id==‘abcd5d’ 的信息所在文件)

## 用户界面设计

### 登陆界面：



### 主界面：



## 程序结构设计：

> 一般可以先做一个程序架构设计，然后以此为基础再细化结构设计。但本应用较简单且逻辑清晰，就直接省略了。

