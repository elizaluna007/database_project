# database_project

CQU 数据库项目之数据库 SQL 引擎设计与模拟实现

#### lry:

##### 登录注册(使用用户 id 和密码)(可跳过直接使用)

##### Database()需要使用账号 ID 和密码登录

##### Database(True)登录账号 account=12345,password=11111111a 直接使用指令

##### 数据库创建（完成）

##### use database_name

##### create database database_name

##### 数据表创建（完成）

##### create table table_name({name type [not null] [unique]}{foreign key(name)references table_name2(name2) }[primary key(name)])

##### 符号[...]表示方括号内包含的为可选项；符号{...}表示花括号内包含的为可重复 0 次或多次的项；

##### 添加用例（完成）

##### insert into table_name({name})values({data})

###### 数据类型设计参考https://github.com/haowang-cqu/SQLittle.git

```
database_project
├─ database.py---------------------------------------------数据库（代码所在位置，搜索u should add，你就知道你该在哪里继续添加了）
├─ dbs-----------------------------------------------------数据库存储地址
│  ├─ db0001234525337633_db_2------------------------------具体的数据库，文件名由【数据库ID_数据库名称】组成
│  └─ db0001234540907795_db
│     ├─ tb000123454090779539588310_my_table---------------具体的数据表，文件名有【数据表ID_数据表名称】组成
│     │  ├─ data.csv---------------------------------------数据表数据
│     │  └─ type.csv---------------------------------------数据表结构
│     └─ tb000123454090779584011892_my_table_2
│        ├─ data.csv
│        └─ type.csv
├─ main.py
├─ Metadata------------------------------------------------元数据
│  ├─ Metadata_Database_Table.xlsx-------------------------sheet1-3分别存储用户信息、数据库信息、数据表信息
│  └─ type-------------------------------------------------数据类型
│     ├─ num.json
│     ├─ str.json
│     ├─ time.json
│     └─ types.json
├─ pics----------------------------------------------------相关设计
│  └─ 用例图.png
└─ README.md

```
