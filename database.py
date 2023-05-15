import xlwings as xw
import pandas as pd
import re
import os
import csv
import json
from datetime import datetime
import shutil

import time
# B+树索引
# 二分法，根据边界点不同分为两种
def erfen1(a, x, l=0, r=None):
    if r is None: r = len(a)
    while l< r:
        mid = (l + r) // 2
        if x < a[mid]: r = mid
        else: l = mid + 1
    return l

def erfen2(a, x, l=0, h=None):
    if h is None: h = len(a)
    while l < h:
        mid = (l + h) // 2
        if a[mid] < x: l = mid + 1
        else: h = mid
    return l

# 定义键值对，以及键值对相关的操作
class key_value(object):
    __slots__ = ('key', 'value')
    def __init__(self, key, value):
        self.key = key
        self.value = value
    def __str__(self):
        return str((self.key, self.value))
    def __lt__(self, other):  # 小
        if isinstance(other, key_value):
            if self.key < other.key: return True
            else: return False
        else:
            if self.key < other: return True
            else: return False
    def __gt__(self, other):  # 大
        if isinstance(other, key_value):
            if self.key > other.key: return True
            else: return False
        else:
            if self.key > other: return True
            else: return False
    def __eq__(self, other):  # 相等
        if isinstance(other, key_value): # 判断变量类型 确定与索引键值对是同一类型
            if self.key == other.key: return True
            else: return False
        else:
            if self.key == other: return True
            else: return False
    def __ne__(self, other): # 不等
        if isinstance(other, key_value):
            if self.key != other.key: return True
            else: return False
        else:
            if self.key != other: return True
            else: return False

# 树内部结点
class tree_node(object):
    def __init__(self, M):
        self._M = M
        self.childlist = []  # 是index节点，保存tree_node节点信息 是leaf节点， 保存 tree_leaf的信息
        self.idexlist = []  # 保存 索引节点
        self.par = None
    def isleaf(self):  return False
    def isfull(self): return len(self.idexlist) >= self.M - 1
    def isempty(self): return len(self.idexlist) <= (self.M + 1) // 2 - 1
    @property
    def M(self): return self._M

# 树叶节点
class tree_leaf(object):
    def __init__(self, L):
        self._L = L
        self.leaflist = []  # 叶节点列表
        self.bro = None
        self.dad = None
    def isleaf(self): return True
    def isfull(self): return len(self.leaflist) > self.L   # 个数超过了阶数，上溢
    def islack(self): return len(self.leaflist) <= (self.L + 1) // 2  # 不到个数最小值，下溢
    @property
    def L(self): return self._L

# 构建B+树
class Bplus_tree(object):
    def __init__(self, M, L):  # M为度。L为填充因子
        self._M = M
        self._L = L
        self._root = tree_leaf(L)
        self._leaf = self._root
    @property
    def M(self): return self._M
    @property
    def L(self): return self._L
    def leaf(self): return self._leaf
    def insert(self, key_value):  # 插入索引
        def split_node(n1):  # 内部节点分裂
            mid = self.M // 2
            new_node = tree_node(self.M)
            new_node.idexlist = n1.idexlist[mid:]
            new_node.childlist = n1.childlist[mid:]
            new_node.par = n1.dad
            for c in new_node.childlist:
                c.dad = new_node
            if n1.dad is None: # n1为根节点
                new_root = tree_node(self.M)
                new_root.idexlist = [n1.idexlist[mid - 1]]
                new_root.childlist = [n1, new_node]
                n1.dad = new_node.par = new_root
                self._root = new_root
            else:
                i = n1.dad.childlist.index(n1)
                n1.dad.idexlist.insert(i, n1.idexlist[mid - 1])
                n1.dad.childlist.insert(i + 1, new_node)
            n1.idexlist = n1.idexlist[:mid - 1]
            n1.childlist = n1.childlist[:mid]
            return n1.dad

        def split_leaf(n2):  # 叶节点分裂（插入后上溢）
            m = (self.L + 1) // 2
            new_leaf = tree_leaf(self.L)
            new_leaf.leaflist = n2.leaflist[m:] # 新leaf结点，存原leaf的右边
            if n2.dad == None:  # n2为根节点
                new_root = tree_node(self.M)  # 新node结点，存mid和max
                new_root.idexlist = [n2.leaflist[m].key]
                new_root.childlist = [n2, new_leaf]
                n2.dad = new_leaf.dad = new_root  # 新旧leaf结点的父节点指向新node
                self._root = new_root
            else:  # n2有父结点
                i = n2.dad.childlist.index(n2)
                n2.dad.idexlist.insert(i, n2.leaflist[m].key) # 向上更新父节点键
                n2.dad.childlist.insert(i + 1, new_leaf)
                new_leaf.dad = n2.dad
            n2.leaflist = n2.leaflist[:m]  # 原leaf的左边
            n2.bro = new_leaf # leaf结点之间的指针
        def insert_node(n):
            if not n.isleaf():  # 当前为内部节点
                if n.isfull():  # 结点中键个数超过阶数，需要将该结点进行分裂
                    insert_node(split_node(n))
                else:  # 没满
                    p = erfen1(n.idexlist, key_value)
                    insert_node(n.childlist[p])
            else:  # 从叶子节点开始插入
                p = erfen1(n.leaflist, key_value) # 正常插入，先用二分法查找插入位置，然后直接插入
                n.leaflist.insert(p, key_value)
                if n.isfull():  # 如果插入后满了，就需要分裂
                    split_leaf(n)
                else:
                    return
        insert_node(self._root)

    def search(self, key=None): # 根节点开始，向下逐层使用二分查找，最终找到匹配的叶子节点
        re = []
        node = self._root
        def search_key(node, key):
            if node.isleaf():
                pos = erfen2(node.leaflist, key)
                return (pos, node)
            else:
                pos = erfen1(node.idexlist, key)
                return search_key(node.childlist[pos], key) # 逐层递归
        posi, knode = search_key(node, key)
        if knode.leaflist[posi] == key:
            re.append(knode.leaflist[posi])
            return re
        else:
            return re
    def delete(self, key_value): # 删除索引
        def tran_l2r(n, i): # 将左边的转移过来
            # 将i的最后一个节点追加到i+1的第一个节点
            if not n.childlist[i].isleaf():
                n.childlist[i + 1].childlist.insert(0, n.childlist[i].childlist[-1])
                n.childlist[i].childlist[-1].dad = n.childlist[i + 1]
                n.childlist[i + 1].idexlist.insert(0, n.idexlist[i])
                n.idexlist[i] = n.childlist[i].idexlist[-1]
                n.childlist[i].childlist.pop()
                n.childlist[i].idexlist.pop()
            else:
                n.childlist[i + 1].leaflist.insert(0, n.childlist[i].leaflist[-1])
                n.childlist[i].leaflist.pop()
                n.idexlist[i] = n.childlist[i + 1].leaflist[0].key
        def tran_r2l(n, i): # 将右边的转移过来
            # 将i+1的第一个节点追加到i的最后一个节点
            if not n.childlist[i].isleaf():
                n.childlist[i].childlist.append(n.childlist[i + 1].childlist[0])
                n.childlist[i + 1].childlist[0].dad = n.childlist[i]
                n.childlist[i].idexlist.append(n.idexlist[i])
                n.idexlist[i] = n.childlist[i + 1].idexlist[0]
                n.childlist[i + 1].childlist.remove(n.childlist[i + 1].childlist[0])
                n.childlist[i + 1].idexlist.remove(n.childlist[i + 1].idexlist[0])
            else:
                n.childlist[i].leaflist.append(n.childlist[i + 1].leaflist[0])
                n.childlist[i + 1].leaflist.remove(n.childlist[i + 1].leaflist[0])
                n.idexlist[i] = n.childlist[i + 1].leaflist[0].key
        def merge(n, i): # 结点合并
            if n.childlist[i].isleaf():
                n.childlist[i].leaflist = n.childlist[i].leaflist + n.childlist[i + 1].leaflist
                n.childlist[i].bro = n.childlist[i + 1].bro
            else:
                n.childlist[i].idexlist = n.childlist[i].idexlist + [n.idexlist[i]] + n.childlist[i + 1].idexlist
                n.childlist[i].childlist = n.childlist[i].childlist + n.childlist[i + 1].childlist
            n.childlist.remove(n.childlist[i + 1])
            n.idexlist.remove(n.idexlist[i])
            if n.idexlist == []:
                n.childlist[0].dad = None
                self._root = n.childlist[0]
                del n
                return self._root
            else:
                return n
        def del_node(n, kv): # 删除可能会触发下溢出，即节点键个数<(mid+1)/2
            if not n.isleaf(): # 内部节点
                p = erfen1(n.idexlist, kv)
                if p == len(n.idexlist): # 是最大值，就需要从子结点重新找最大值
                    if not n.childlist[p].islack(): # 不产生下溢，直接删除
                        return del_node(n.childlist[p], kv)
                    elif not n.childlist[p - 1].islack(): # 产生下溢，删除后要修复，若兄弟节点富余，可以向对应富余的兄弟借键
                        tran_l2r(n, p - 1) # 将左边的转移过来
                        return del_node(n.childlist[p], kv)
                    else: # 兄弟节点也不富余，则将兄弟节点与该节点合并，然后更新父节点
                        return del_node(merge(n, p - 1), kv)
                else:
                    if not n.childlist[p].islack():
                        return del_node(n.childlist[p], kv)
                    elif not n.childlist[p + 1].islack():
                        tran_r2l(n, p) # 将右边的转移过来，默认是转移右边的
                        return del_node(n.childlist[p], kv)
                    else:
                        return del_node(merge(n, p), kv)
            else:  # 叶结点直接删除即可
                p = erfen2(n.leaflist, kv)
                pp = n.leaflist[p]
                if pp != kv:
                    return -1
                else:
                    n.leaflist.remove(kv)
                    return 0
        del_node(self._root, key_value) # 自顶向下

tree1 = Bplus_tree(4, 4)  # address
tree2 = Bplus_tree(4, 4)  # student

def split_string_with_delimiters(string):
    result = []
    current_str = ""

    for char in string:
        if char == "," or char == ";" or char == "(" or char == ")" or char == " ":
            if (current_str != ""):
                result.append(current_str)
            if (char == "("):
                result.append("(")
            elif (char == ")"):
                result.append(")")
            current_str = ""
        else:
            current_str = current_str+char
    if (current_str != ""):
        result.append(current_str)
    return result


def is_binary_string(s):
    try:
        # 尝试将字符串解码为二进制数据
        s.encode('latin1')
        # 如果解码成功，且字符串只包含0和1，则判断为二进制字符串
        return all(c in '01' for c in s)
    except UnicodeEncodeError:
        # 解码失败，不是二进制字符串
        return False


def is_date(date_string, date_range=["1000-01-01", "9999-12-31"]):
    try:
        # 检查日期范围是否满足要求
        start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
        end_date = datetime.strptime(date_range[1], "%Y-%m-%d")
        target_date = datetime.strptime(date_string, "%Y-%m-%d")

        if start_date <= target_date <= end_date:
            return True
        else:
            return False
    except ValueError:
        # 解析日期出错，不满足要求的字符串
        return False


def is_time(time_string, time_range=["-838:59:59", "838:59:59"]):
    try:
        # 解析时间范围
        start_time = time_range[0]
        end_time = time_range[1]

        # 解析目标时间
        target_time = time_string

        # 检查时间格式是否满足要求
        if not all(x.isdigit() for x in target_time.split(":")):
            return False

        # 分割时间字符串为小时、分钟和秒钟
        target_hour, target_minute, target_second = map(
            int, target_time.split(":"))

        # 检查分钟和秒钟是否在有效范围内
        if not (0 <= target_minute <= 59 and 0 <= target_second <= 59):
            return False

        # 处理负数时间的情况
        if start_time.startswith("-") or end_time.startswith("-"):
            # 将时间转换为秒数进行比较
            start_seconds = sum(int(x) * 60**i for i,
                                x in enumerate(reversed(start_time.split(":"))))
            end_seconds = sum(int(x) * 60**i for i,
                              x in enumerate(reversed(end_time.split(":"))))
            target_seconds = target_hour * 3600 + target_minute * 60 + target_second

            if start_seconds <= target_seconds <= end_seconds:
                return True
            else:
                return False
        else:
            # 解析时间范围为小时、分钟和秒钟
            start_hour, start_minute, start_second = map(
                int, start_time.split(":"))
            end_hour, end_minute, end_second = map(int, end_time.split(":"))

            # 检查时间是否在范围内
            if (
                start_hour <= target_hour <= end_hour
                and start_minute <= target_minute <= end_minute
                and start_second <= target_second <= end_second
            ):
                return True
            else:
                return False
    except ValueError:
        # 解析时间出错，不满足要求的字符串
        return False


def is_year(year_string):
    if (year_string >= "1901" and year_string <= "2155"):
        return True
    else:
        return False


def is_datetime(datetime_string):
    datetime = datetime_string.split(" ")
    if (len(datetime) != 2):
        return False
    else:
        date_part = datetime[0]
        time_part = datetime[1]
        date_range = ["1000-01-01", "9999-12-31"]
        time_range = ["0:0:0", "23:59:59"]
        if (is_date(date_part, date_range) and is_time(time_part, time_range)):
            return True
        else:
            return False


def is_timestamp(timestamp_string):
    datetime = timestamp_string.split(" ")
    if (len(datetime) != 2):
        return False
    else:
        date_part = datetime[0]
        time_part = datetime[1]
        date_range = ["1970-01-01", "2038-1-19"]
        time_range = ["0:0:0", "23:59:59"]
        if (is_date(date_part, date_range) and is_time(time_part, time_range)):
            return True
        else:
            return False


class Database:
    # 数据库初始化
    def __init__(self, choose=None, account=12345, password="11111111a"):
        print("---欢迎登录数据库系统---")
        self.path = None  # 数据库路径，即工作簿的路径
        # self.app = None  # 创建Excel应用程序的实例
        self.wb = None  # 一个 Excel 工作簿
        self.config = None  # Excel 工作簿中的一个工作表
        self.database_ID = None  # 当前正在使用的数据库ID
        self.account = None  # 账户ID
        self.password = None  # 账户密码
        self.database_name = None  # 要登录的数据库
        self.table_ID = None  # 当前正在使用的表格ID
        # 读取xlsx文件
        self.dataframe_1 = pd.read_excel(
            './Metadata/Metadata_Database_Table.xlsx', sheet_name='Sheet1')  # 用户信息：账户、名称、密码
        self.dataframe_2 = pd.read_excel(
            './Metadata/Metadata_Database_Table.xlsx', sheet_name='Sheet2')  # 数据库信息：数据库ID、数据库名称、数据库所属账户ID
        self.dataframe_3 = pd.read_excel(
            './Metadata/Metadata_Database_Table.xlsx', sheet_name='Sheet3')  # 表格信息：表格ID、表格名称、表格所属数据库ID
        # 如果什么都没有，则先登录
        if (choose == None):
            self.login()
        # 否则一开始就指令
        else:
            self.account = account
            self.password = password
            self.inst()

    def inst(self):
        print(f'*账号 {self.account} 成功登录*')
        line = input("请输入您的指令(exit退出系统):")
        while (line != "exit"):
            self.instruction(line)
            line = input("请输入您的指令(exit退出系统):")
        print("*您已退出数据库系统")

    # 登录
    def login(self):
        self.account = int(input("请输入您的账号(纯数字):"))
        self.password = str(input("请输入您的密码："))
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 0  # 第0列的索引（从0开始）
        # 使用布尔索引检查第0列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_1.iloc[:, column_index] == self.account
        if column_exists.any():
            # 获取满足条件的行索引
            row_indices = column_exists[column_exists].index.tolist()
            # 验证该行的第2个数是否是password
            value_column_index = 2  # 第2列的索引（从0开始）
            rows_with_value = self.dataframe_1.iloc[row_indices,
                                                    value_column_index] == self.password
            # 输出满足条件的行索引和第2个数是否为password
            if (rows_with_value.tolist())[0]:
                print(f'*账号 {self.account} 成功登录*')
                line = input("请输入您的指令(exit退出系统):")
                while (line != "exit"):
                    self.instruction(line)
                    line = input("请输入您的指令:")
            else:
                print(
                    f"当前账号 {self.account} 的密码错误，请选择重新登录(T)或者注册新账号(F)或者退出系统(OTHERS)")
                choice = input()
                if (choice == 'T'):
                    self.login()
                elif (choice == 'F'):
                    self.register()  # 注册
                    self.inst()
                else:
                    print("系统已退出")
        else:
            print(f"当前账号 {self.account} 不存在，请选择重新登录(T)或注册(F)或退出系统(OTHER)")
            choice = input()
            if (choice == 'T'):
                self.login()  # 登录
            elif (choice == 'F'):
                self.register()  # 注册
                self.inst()
            else:
                print("*系统已退出")

    # 注册
    def register(self):
        self.account = int(input("请输入您的账号ID:"))
        name = input("请输入您的账号名称:")
        self.password = input("请输入您的密码：")
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 0  # 第0列的索引（从0开始）
        # 使用布尔索引检查第0列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_1.iloc[:, column_index] == self.account
        if column_exists.any():
            print(f"当前账号 {self.account} 已存在，请选择是否重新登录(T)或者注册(F)或者退出系统(OTHER)")
            choice = input()
            if (choice == 'T'):
                self.login()  # 登录
            elif (choice == 'F'):
                self.register()  # 注册
            else:
                print("*系统已退出")

        else:
            # 将新数据添加到数据框的最后一行
            self.dataframe_1.loc[len(self.dataframe_1)] = [
                self.account, name, self.password]
            # 创建 ExcelWriter 对象
            writer = pd.ExcelWriter('./Metadata/Metadata_Database_Table.xlsx')
            # 将数据写入各个工作表
            self.dataframe_1.to_excel(writer, sheet_name='Sheet1', index=False)
            self.dataframe_2.to_excel(writer, sheet_name='Sheet2', index=False)
            self.dataframe_3.to_excel(writer, sheet_name='Sheet3', index=False)
            # 保存 Excel 文件
            writer.save()
            writer.close()

    def instruction(self, input_string):
        #    # 定义分隔符的正则表达式模式
        #     pattern = r"\s+|,|;"

        #     # 使用正则表达式的 split() 方法按照模式进行分割
        #     small_strings = re.split(pattern, input_string)

        #     # 去除空字符串
        #     small_strings = [
        #         string for string in small_strings if string.strip() != ""]
        small_strings = split_string_with_delimiters(input_string)
        # 如果还未选择数据库，需要先选择数据库
        if (self.database_name == None and small_strings[0] != "use" and small_strings[0] != "create"):
            print("请先选择数据库")
            return
        elif (self.database_name == None and small_strings[0] == "create" and small_strings[1] == "table"):
            print("请先选择数据库")
            return
        # 选择数据库
        elif (small_strings[0] == "use"):
            self.database_name = small_strings[1]
            self.use_database()

        # 创建数据库
        elif (small_strings[0] == "create" and small_strings[1] == "database"):
            self.database_name = small_strings[2]
            if (self.is_sure_key(small_strings[2])):
                print("该数据库名称与关键词重合，创建数据库失败")
            else:
                self.create_database()
        # 创建数据表
        elif (small_strings[0] == "create" and small_strings[1] == "table"):
            if (self.is_sure_key(small_strings[2])):
                print("该数据表名称与关键词重合，创建数据表失败")
            else:
                self.create_table(small_strings)

        # 插入数据
        elif (small_strings[0] == "insert" and small_strings[1] == "into"):
            self.insert_data(small_strings)

        # --------------u should add the other instruction here--------------------------------
        # 查看当前在使用的数据库
        elif (small_strings[0] == "select" and small_strings[1] == "database"):
            print("current database: ID ",self.database_ID,"  name ",self.database_name);
        # 查看数据表结构
        elif (small_strings[0] == "select" and small_strings[1] == "type"):
            self.selecttable_data(small_strings)
        # 查询数据表 select * from 数据表名 where id = 001
        elif (small_strings[0] == "select" and small_strings[1] == "*" and small_strings[4] == "where"):
            self.select2_data(small_strings)
        # 查看数据表全部数据
        elif (small_strings[0] == "select" and small_strings[1] == "*"):
            self.selectall_data(small_strings)
        # eg: select name from student where id = 001 ;
        elif (small_strings[0] == "select" and small_strings[2] == "from" and len(small_strings)>5):
            self.select1_data(small_strings)
        # eg: select name from student ;
        elif (small_strings[0] == "select" and small_strings[2] == "from"):
            self.select3_data(small_strings)
        # 删除数据 delete from 数据表名 where id = 001
        elif (small_strings[0] == "delete" and small_strings[1] == "from"):
            self.delete_data(small_strings)
        # 删除数据表 drop table 数据表名
        elif (small_strings[0] == "drop" and small_strings[1] == "table"):
            self.drop_table(small_strings)
        # 删除数据库 drop database 数据库名
        elif (small_strings[0] == "drop" and small_strings[1] == "database"):
            self.drop_database(small_strings)
        # 修改数据 update 数据表名 set name = '小明' where id = 001
        elif (small_strings[0] == "update" and small_strings[2] == "set"):
            self.update_data(small_strings)        
        else:
            print("该指令非法")

    def select1_data(self, small_strings):
        attri_name = small_strings[1]
        table_name = small_strings[3]
        select_key = small_strings[5]
        select_value = small_strings[7]
        if (self.is_sure_table_by_database_ID(table_name)):
            t = time.perf_counter()
            self.select1_dt(attri_name,table_name,select_key,select_value,small_strings)
            print(f'time cost:{time.perf_counter() - t:.18f}s')
        else:
            print("该数据表不存在,查看数据表失败")

    def select1_dt(self,attri_name,table_name,select_key,select_value, small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 打开CSV文件并读取数据 # select name from student where id = 001 ;
        data = []
        with open(file_name_type, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        t=0
        t1=0
        for i in range(len(data[0])):
            if data[0][i]==select_key:
                t=i
            if data[0][i]==attri_name:
                t1=i
        # 无索引的查询
        for i in range(1,len(data)):
            if(data[i][t]==select_value):
                print(data[i][t1])
        # #有索引的查询
        # if (table_name == "address"):
        #     for kv in tree1.search(int(select_value)):
        #         value = kv.value
        #         print(data[value][t1])
        # elif (table_name == "student"):
        #     for kv in tree2.search(int(select_value)):
        #         value = kv.value
        #         print(data[value][t1])

    def select2_data(self, small_strings):
        table_name = small_strings[3]
        select_key = small_strings[5]
        select_value = small_strings[7]
        # print(select_key," ",select_value)
        if (self.is_sure_table_by_database_ID(table_name)):
            t = time.perf_counter()
            self.select2_dt(table_name,select_key,select_value,small_strings)
            print(f'time cost:{time.perf_counter() - t:.18f}s')
        else:
            print("该数据表不存在,查看数据表失败")

    def select2_dt(self, table_name,select_key,select_value, small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 打开CSV文件并读取数据
        data = []
        with open(file_name_type, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        t=0
        for i in range(len(data[0])):
            if data[0][i]==select_key:
                t=i
                break
        # 无索引的查询
        for i in range(1,len(data)):
            if(data[i][t]==select_value):
                print(data[i])
        # # 有索引的查询
        # if(table_name=="address"):
        #     for kv in tree1.search(int(select_value)):
        #         value=kv.value
        #         print(data[value])
        # elif(table_name=="student"):
        #     for kv in tree2.search(int(select_value)):
        #         value=kv.value
        #         print(data[value])
    def select3_data(self, small_strings):
        attri_name = small_strings[1]
        table_name = small_strings[3]
        if (self.is_sure_table_by_database_ID(table_name)):
            t = time.perf_counter()
            self.select3_dt(attri_name,table_name,small_strings)
            print(f'time cost:{time.perf_counter() - t:.18f}s')
        else:
            print("该数据表不存在,查看数据表失败")

    def select3_dt(self,attri_name,table_name,small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 打开CSV文件并读取数据 # select name from student ;
        data = []
        with open(file_name_type, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        t1=0
        for i in range(len(data[0])):
            if data[0][i]==attri_name:
                t1=i
        for i in range(1,len(data)):
                print(data[i][t1])
    def selecttable_data(self, small_strings):
        table_name = small_strings[3]
        if (self.is_sure_table_by_database_ID(table_name)):
            self.selecttable_dt(table_name, small_strings)
        else:
            print("该数据表不存在,查看数据表失败")

    def selecttable_dt(self, table_name, small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/type.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 打开CSV文件并读取数据
        with open(file_name_type, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

    def selectall_data(self, small_strings):
        table_name = small_strings[3]
        if (self.is_sure_table_by_database_ID(table_name)):
            self.selectall_dt(table_name, small_strings)
        else:
            print("该数据表不存在,查看数据表失败")

    def selectall_dt(self, table_name, small_strings):
        file_name_data = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 打开CSV文件并读取数据
        with open(file_name_data, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

    def is_sure_key(self, str):
        metadata = ['_admin_ID_', '_admin_name_', '_password_', '_database_ID_',
                    '_database_name_', '_database_admin_ID_', '_table_ID_', '_table_name_', '_database_ID_']
        type = ["_name_", "_type_", "_check_", "_default_",
                "_primary key_", "_unique_", "_not null_", "_foreign key_"]
        num_type = ['tinyint', 'smallint', 'mediumint',
                    'int', 'bigint', 'float', 'double']
        str_type = ['char', 'varchar', 'tinyblob', 'tinytext',
                    'blob', 'text', 'mediumblob', 'mediumtext', 'longblob', 'longtext']
        time_type = ['date', 'time', 'year', 'datetime', 'timestamp']
        if str in metadata or str in type or str in num_type or str in str_type or str in time_type:
            if str in num_type or str in str_type or str in time_type:
                return 2
            return 1
        else:
            return 0

    def insert_data(self, small_strings):
        table_name = small_strings[2]
        if (self.is_sure_table_by_database_ID(table_name)):
            self.insert_dt(table_name, small_strings)
        else:
            print("该数据表不存在,插入数据失败")

    def insert_dt(self, table_name, small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/type.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        file_name_data = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 打开CSV文件并读取数据
        data_type = []
        with open(file_name_type, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data_type.append(row)
        data = []
        with open(file_name_data, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)

        data_insert_name = []
        data_insert_data = []
        i = 4
        key = 0
        while (i < len(small_strings)):
            if (small_strings[i] != ")" and small_strings[i] != "(" and small_strings[i] != "values"):
                if (key == 0):
                    data_insert_name.append(small_strings[i])
                else:
                    data_insert_data.append(small_strings[i])
                i = i+1
            elif (small_strings[i] == "values"):
                i = i+1
                key = 1
            else:
                i = i+1

        # 建立索引，key：id  value：行号
        hang = len(data)
        if (data_insert_name[0] == "id"):
            if(table_name=="address"):
                print("成功建立一条关于address表的索引：key ",int(data_insert_data[0]),"  value ",hang)
                tree1.insert(key_value(int(data_insert_data[0]), hang))
            elif(table_name == "student"):
                print("成功建立一条关于student表的索引：key ",int(data_insert_data[0]),"  value ",hang)
                tree2.insert(key_value(int(data_insert_data[0]), hang))

        result = ["" for i in range(len(data[0]))]
        key = 1
        for i in range(len(data_insert_data)):
            b, n = self.insert_dt_select(
                data_type, data, data_insert_name[i], data_insert_data[i])
            key = key and b
            result[n] = data_insert_data[i]

        # 判断not null
        key = key and self.check_not_null(result, data_type)
        # 判断primary key
        key = key and self.check_primary_key(result, data_type)
        # 默认值赋值
        result = self.check_default(result, data_type)
        result = [result]
        if (key):
            with open(file_name_data, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(result)
            result = result[0]
            print("成功插入数据", result)

    def check_default(self, result, data_type):
        for i in range(len(data_type[1:])):
            if (data_type[i+1][3] != ""):
                if (result[i] == ""):
                    result[i] = data_type[i+1][3]
        return result

    def check_not_null(self, result, data_type):
        for i in range(len(data_type[1:])):
            if (data_type[i+1][6] == "True"):
                if (result[i] == ""):
                    print("not null数据 {} 为空,插入数据失败".format(data_type[i+1][0]))
                    return False
        return True

    def check_primary_key(self, result, data_type):
        for i in range(len(data_type[1:])):
            if (data_type[i+1][4] == "True"):
                if (result[i] == ""):
                    print("primary key数据 {} 为空,插入数据失败".format(
                        data_type[i+1][0]))
                    return False
        return True

    # 检查类型与数值是否匹配
    def check(self, type, data):
        # num类型的值的范围在type文件夹下的num.json中，对其进行检查
        if (type == "tinyint"):
            if (int(data) >= -128 and int(data) <= 127):
                return True
            else:
                return False
        elif (type == "smallint"):
            if (int(data) >= -32768 and int(data) <= 32767):
                return True
            else:
                return False
        elif (type == "mediumint"):
            if (int(data) >= -8388608 and int(data) <= 8388607):
                return True
            else:
                return False
        elif (type == "int"):
            if (int(data) >= -2147483648 and int(data) <= 2147483647):
                return True
            else:
                return False
        elif (type == "bigint"):
            if (int(data) >= -9223372036854775808 and int(data) <= 9223372036854775807):
                return True
            else:
                return False
        elif (type == "float"):
            if (float(data) >= -3.402823466E+38 and float(data) <= 3.402823466E+38):
                return True
            else:
                return False
        elif (type == "double"):
            if (float(data) >= -1.7976931348623157E+308 and float(data) <= 1.7976931348623157E+308):
                return True
            else:
                return False
        # str类型的值的范围在type文件夹下的str.json中，对其进行检查
        elif (type == "char"):
            if (len(data) <= 255):
                return True
            else:
                return False
        elif (type == "varchar"):
            if (len(data) <= 65535):
                return True
            else:
                return False
        elif (type == "tinyblob"):
            if (len(data) <= 255 and is_binary_string(data)):
                return True
            else:
                return False
        elif (type == "tinytext"):
            if (len(data) <= 255):
                return True
            else:
                return False
        elif (type == "blob"):
            if (len(data) <= 65535 and is_binary_string(data)):
                return True
            else:
                return False
        elif (type == "text"):
            if (len(data) <= 65535):
                return True
            else:
                return False
        elif (type == "mediumblob"):
            if (len(data) <= 16777215 and is_binary_string(data)):
                return True
            else:
                return False
        elif (type == "mediumtext"):
            if (len(data) <= 16777215):
                return True
            else:
                return False
        elif (type == "longblob"):
            if (len(data) <= 4294967295 and is_binary_string(data)):
                return True
            else:
                return False
        elif (type == "longtext"):
            if (len(data) <= 4294967295):
                return True
        # time类型的值的范围在type文件夹下的time.json中，对其进行检查
        elif (type == "date"):
            if (is_date(data)):
                return True
            else:
                return False
        elif (type == "time"):
            if (is_time(data)):
                return True
            else:
                return False
        elif (type == "year"):
            if (is_year(data)):
                return True
            else:
                return False
        elif (type == "datetime"):
            if (is_datetime(data)):
                return True
            else:
                return False
        elif (type == "timestamp"):
            if (is_timestamp(data)):
                return True
            else:
                return False
        else:
            # id char(num)
            if (type[:4] == "char"):
                num = type[5:]
                return True
            else:
                return False

    def insert_dt_select(self, type, data, name_now, data_now):
        key = 1
        # i是该数据的位置
        key_key = 0
        for i in range(len(type)):
            if (type[i][0] == name_now):
                key_key = 1
                break
        if (key_key == 0):
            key = 0
            print("属性名 {name_now} 不存在,插入数据失败".format(name_now=name_now))
            return key, i-1

        # type
        if (self.check(type[i][1], data_now) == False):
            key = 0
            print("数据类型不匹配,插入数据失败")
            return key, i-1

        if (type[:4] == "char"):
            num = int(type[5:])
            if (len(data_now) != num):
                key = 0
                print("数据类型不匹配,插入数据失败")
                return key, i-1

        # check
        # if (type[i][2] != ""):
            # todo

        # primary key
        if (type[i][4] == "True"):
            for j in data:
                if (j[i-1] == data_now):
                    key = 0
                    print("{data_now}已存在,插入数据失败".format(data_now=data_now))
                    return key, i-1
        # unique
        if (type[i][5] == "True"):
            for j in data:
                if (j[i-1] == data_now):
                    key = 0
                    print("{data_now}已存在,插入数据失败".format(data_now=data_now))
                    return key, i-1
        # foreign key
        if (type[i][7] != ""):
            # 使用正则表达式提取主要名称和附加名称
            pattern = r'^(.*?)\((.*?)\)$'
            match = re.match(pattern, type[i][7])
            main_name = match.group(1)
            additional_name = match.group(2)
            if (self.is_sure_table_by_database_ID(main_name)):  # 存在该数据表
                if (self.is_sure_name_by_table_ID(main_name, additional_name)):  # 存在该外键
                    file_name = "dbs/{}_{}/{}_{}/data.csv".format(
                        self.database_ID, self.database_name, self.table_ID, main_name)
                    data = []
                    with open(file_name, 'r') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            data.append(row)
                    for q in range(len(data[0])):
                        if (data[0][q] == additional_name):
                            break
                    key_key = 0
                    for j in data:
                        if (j[q] == data_now):
                            key_key = 1
                            break
                    if (key_key == 0):
                        print(
                            "数据表 {main_name} 不存在外键 {additional_name} 的值 {data_now} ,插入数据失败".format(main_name=main_name, additional_name=additional_name, data_now=data_now))
                        key = 0
                        return key, i-1

                else:
                    print("数据表 {main_name} 不存在外键 {additional_name} ,插入数据失败".format(
                        main_name=main_name, additional_name=additional_name))
                    key = 0
                    return key, i-1
            else:
                print("数据表 {main_name} 不存在,插入数据失败".format(main_name=main_name))
                key = 0
                return key, i-1
        return key, i-1

    def is_sure_name_by_table_ID(self, main_name, additional_name):
        file_name = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, main_name)
        if os.path.isfile(file_name):
            data = []
            with open(file_name, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    data.append(row)
            for i in range(len(data[0])):
                if (data[0][i] == additional_name):
                    return True
        return False

    def create_table(self, small_strings):
        table_name = small_strings[2]
        if (table_name == "("):
            print("指令非法,创建数据表失败")
        elif (self.is_sure_table_by_database_ID(table_name)):
            print("该数据表名称已存在,创建数据表失败")
        else:
            self.create_tb(table_name, small_strings)

    def create_tb(self, table_name, small_strings):
        id_left = self.database_ID[2:]
        id_right = str(hash(table_name)).zfill(9)[1:9]
        id = "tb"+id_left+id_right
        if (self.is_sure_table(id)):
            print("该数据表名称非法,创建数据表失败")
        else:
            # type类型
            result = [["_name_", "_type_", "_check_", "_default_",
                       "_primary key_", "_unique_", "_not null_", "_foreign key_"]]
            i = 4
            name = ""
            while (i < len(small_strings)):
                # PRIMARY KEY (id)
                if (small_strings[i] == "primary" and small_strings[i+1] == "key"):
                    name = small_strings[i+3]
                    for ii in range(len(result)):
                        if (result[ii][0] == name):
                            result[ii][4] = True
                    i = i+4
                # foreign key (CharID) references ChineseCharInfo(ID)
                elif (small_strings[i] == "foreign" and small_strings[i+1] == "key"):
                    name = small_strings[i+3]
                    tb_name = small_strings[i+6]
                    tb_data_name = small_strings[i+8]
                    if (self.is_sure_table_by_database_ID(tb_name)):
                        if (self.is_sure_name_by_table_ID(tb_name, tb_data_name)):
                            key_key = 0
                            for ii in range(len(result)):
                                if (result[ii][0] == name):
                                    result[ii][7] = small_strings[i+6] + \
                                        "("+small_strings[i+8]+")"
                                    key_key = 1
                                    break
                            if (not key_key):
                                print("{name}数据不存在".format(name=name))
                                return
                        else:
                            print("数据表 {main_name} 不存在外键 {additional_name} ,创建数据表{table_name}失败".format(
                                main_name=tb_name, additional_name=tb_data_name, table_name=table_name))
                            return
                    else:
                        print("数据表 {main_name} 不存在,创建数据表{table_name}失败".format(
                            main_name=tb_name, table_name=table_name))
                        return

                    i = i+10
                elif (small_strings[i] == "not" and small_strings[i+1] == "null"):
                    for ii in range(len(result)):
                        if (result[ii][0] == name):
                            result[ii][6] = True
                    i = i+2
                elif (small_strings[i] == "unique"):
                    for ii in range(len(result)):
                        if (result[ii][0] == name):
                            result[ii][5] = True
                    i = i+1
                elif (small_strings[i] == "default"):
                    data = small_strings[i+1]
                    for ii in range(len(result)):
                        if (result[ii][0] == name):
                            result[ii][3] = data
                    i = i+2
                # age INT CHECK (age >= 0 AND age <= 150)
                elif (small_strings[i] == "check"):
                    q = i+2
                    ss = ""
                    while (small_strings[q] != ")"):
                        ss = ss+small_strings[q]
                        q = q+1
                    for ii in range(len(result)):
                        if (result[ii][0] == name):
                            result[ii][2] = ss
                    i = q+1
                elif (small_strings[i] != ')' and small_strings[i] != '('):
                    name = small_strings[i]
                    type = small_strings[i+1]
                    if (self.is_sure_key(type) != 2):
                        print("数据类型错误")
                        return
                    # id char(num)
                    if (type == "char"):
                        num = small_strings[i+3]
                        type = type+"_"+num
                        r = [name, type, "", "", False, False, False, ""]
                        result.append(r)
                        i = i+5
                    else:
                        r = [name, type, "", "", False, False, False, ""]
                        result.append(r)
                        i = i+2
                else:
                    if (small_strings[i] == "(" or small_strings[i] == ")"):
                        i = i+1
                    else:
                        print("您输入的指令错误")
                        break

            # 创建一个数据表就是创建一个dbs/db_ID_db_name_/tb_ID_tb_name的文件夹，其中包含类型文件以及存储数据文件
            folder_name = "dbs/{}_{}/{}_{}".format(
                self.database_ID, self.database_name, id, table_name)
            if not os.path.exists(folder_name):  # 如果文件夹不存在则创建
                os.mkdir(folder_name)

            # 创建一个数据表就是创建一个dbs/db_ID_db_name_/tb_ID_tb_name/type.csv的文件夹，其中包含类型
            # 打开CSV文件并以追加模式写入数据
            file_name = "dbs/{}_{}/{}_{}/type.csv".format(
                self.database_ID, self.database_name, id, table_name)
            with open(file_name, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(result)
            # 创建一个数据表就是创建一个dbs/db_ID_db_name_/tb_ID_tb_name/type.csv的文件夹，其中包含类型
            # 打开CSV文件并以追加模式写入数据
            result_data = []
            for i in result[1:]:
                result_data.append(i[0])
            result_data = [result_data]
            file_name = "dbs/{}_{}/{}_{}/data.csv".format(
                self.database_ID, self.database_name, id, table_name)
            with open(file_name, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(result_data)

            print(
                f"已创建数据表: {table_name}: dbs/{self.database_ID}_{self.database_name}/{id}_{table_name}")
            # 将新数据添加到数据框的最后一行
            self.dataframe_3.loc[len(self.dataframe_3)] = [
                id, table_name, self.database_ID]
            # 创建 ExcelWriter 对象
            writer = pd.ExcelWriter(
                './Metadata/Metadata_Database_Table.xlsx', engine='openpyxl')
            # 将数据写入各个工作表
            self.dataframe_1.to_excel(
                writer, sheet_name='Sheet1', index=False)
            self.dataframe_2.to_excel(
                writer, sheet_name='Sheet2', index=False)
            self.dataframe_3.to_excel(
                writer, sheet_name='Sheet3', index=False)
            # 保存 Excel 文件
            writer.save()
            writer.close()

    def is_sure_table(self, id):
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 0  # 第0列的索引（从0开始）
        # 检查第0列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_3.iloc[:,
                                              column_index] == id
        column_exists_bool = column_exists.tolist()
        for i in column_exists_bool:
            if (i == True):
                return True
        return False

    def is_sure_table_by_database_ID(self, table_name):
        # 判断当前数据库ID下的数据库内是否已经存在当前数据表
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 2  # 第2列的索引（从0开始）
        # 检查第2列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_3.iloc[:,
                                              column_index] == self.database_ID
        if column_exists.any():
            row_indices = column_exists[column_exists].index.tolist(
            )
            # 验证该行的第1个数是否是database_name
            value_column_index = 1  # 第1列的索引（从0开始）
            rows_with_value = self.dataframe_3.iloc[row_indices,
                                                    value_column_index] == table_name
            for i in range(len(rows_with_value.tolist())):
                if (rows_with_value.tolist()[i] == True):
                    self.table_ID = self.dataframe_3.iloc[row_indices[i], 0]
                    return True
        return False

    def create_db(self):
        id_left = str(self.account).zfill(8)
        id_right = str(hash(self.database_name)).zfill(9)[1:9]
        id = 'db'+id_left+id_right
        if (self.is_sure_database(id)):
            print("该数据库名称非法,创建数据库失败")
        else:
            self.database_ID = id
            # try:
            #     self.path = f'dbs/{self.database_ID}.xlsx'
            #     self.wb = xw.Book(self.path)
            #     self.config = self.wb.sheets["Sheet1"]
            # except FileNotFoundError:
            #     self.wb = xw.Book()
            #     self.wb.save(self.path)
            #     print(
            #         f"已创建数据库: {self.database_name}: dbs/{self.database_ID}.xlsx")
            #     # 将新数据添加到数据框的最后一行
            #     self.dataframe_2.loc[len(self.dataframe_2)] = [
            #         self.database_ID, self.database_name, self.account]
            #     # 创建 ExcelWriter 对象
            #     writer = pd.ExcelWriter(
            #         './Metadata/Metadata_Database_Table.xlsx', engine='openpyxl')
            #     # 将数据写入各个工作表
            #     self.dataframe_1.to_excel(
            #         writer, sheet_name='Sheet1', index=False)
            #     self.dataframe_2.to_excel(
            #         writer, sheet_name='Sheet2', index=False)
            #     self.dataframe_3.to_excel(
            #         writer, sheet_name='Sheet3', index=False)
            #     # 保存 Excel 文件
            #     writer.save()
            #     writer.close()

            # 创建一个数据库就是创建一个dbs/db_ID_db_name的文件夹
            folder_name = "dbs/{}_{}".format(self.database_ID,
                                             self.database_name)
            if not os.path.exists(folder_name):  # 如果文件夹不存在则创建
                os.mkdir(folder_name)
            print(
                f"已创建数据库: {self.database_name}: dbs/{self.database_ID}_{self.database_name}")
            # 将新数据添加到数据框的最后一行
            self.dataframe_2.loc[len(self.dataframe_2)] = [
                self.database_ID, self.database_name, self.account]
            # 创建 ExcelWriter 对象
            writer = pd.ExcelWriter(
                './Metadata/Metadata_Database_Table.xlsx', engine='openpyxl')
            # 将数据写入各个工作表
            self.dataframe_1.to_excel(
                writer, sheet_name='Sheet1', index=False)
            self.dataframe_2.to_excel(
                writer, sheet_name='Sheet2', index=False)
            self.dataframe_3.to_excel(
                writer, sheet_name='Sheet3', index=False)
            # 保存 Excel 文件
            writer.save()
            writer.close()

    def is_sure_database_name_by_account(self):
        # 当前用户是否已经创建过该数据库
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 2  # 第2列的索引（从0开始）
        # 检查第2列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_2.iloc[:,
                                              column_index] == self.account
        if column_exists.any():
            row_indices = column_exists[column_exists].index.tolist(
            )
            # 验证该行的第1个数是否是database_name
            value_column_index = 1  # 第1列的索引（从0开始）
            rows_with_value = self.dataframe_2.iloc[row_indices,
                                                    value_column_index] == self.database_name

            for i in range(len(rows_with_value.tolist())):
                if (rows_with_value.tolist()[i] == True):
                    return True
        return False

    def create_database(self):
        if (self.is_sure_database_name_by_account()):
            print(f"该数据库 {self.database_name} 已建立过，无需重复创建")
        else:
            self.create_db()

    def is_sure_database(self, id):
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 0  # 第0列的索引（从0开始）
        # 检查第0列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_2.iloc[:,
                                              column_index] == id
        column_exists_bool = column_exists.tolist()
        for i in column_exists_bool:
            if (i == True):
                return True
        return False

    def use_database(self):
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 2  # 第2列的索引（从0开始）
        # 检查第2列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_2.iloc[:,
                                              column_index] == self.account
        if column_exists.any():
            row_indices = column_exists[column_exists].index.tolist()
            # 验证该行的第1个数是否是database_name
            value_column_index = 1  # 第1列的索引（从0开始）
            rows_with_value = self.dataframe_2.iloc[row_indices,
                                                    value_column_index] == self.database_name
            key = 0
            for i in range(len(rows_with_value.tolist())):
                if (rows_with_value.tolist()[i] == True):
                    database_ID = self.dataframe_2.iloc[row_indices[i], 0]
                    self.database_ID = database_ID
                    key = 1
                    print(f"*成功选择数据库 {self.database_name} ")
                    return
            if (key == 0):
                print(f"您选择的数据库 {self.database_name} 不存在")
        else:
            print(f"您选择的数据库 {self.database_name} 不存在")


    def delete_data(self, small_strings):
        # delete from student where id = 001 ;
        table_name = small_strings[2]
        select_key = small_strings[4]
        select_value = small_strings[6]
        if (self.is_sure_table_by_database_ID(table_name)):
            self.delete_dt(table_name,select_key,select_value,small_strings)
        else:
            print("该数据表不存在,查看数据表失败")

    def delete_dt(self,table_name,select_key,select_value, small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        data = []
        with open(file_name_type, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        t=0
        delete_index = 0
        for i in range(len(data[0])):
            if data[0][i]==select_key:
                t=i
        # # 无索引删除
        # for i in range(1,len(data)):
        #     if(data[i][t]==select_value):
        #         delete_index=i
        # 通过索引查找后删除
        if (table_name == "address"):
            for kv in tree1.search(int(select_value)):
                delete_index = kv.value
        elif (table_name == "student"):
            for kv in tree2.search(int(select_value)):
                delete_index = kv.value
        # 删除对应行的索引
        if(table_name=="address"):
            for kv in tree1.search(int(select_value)):
                key=kv.key
                value=kv.value
                print("删除一条关于address表的索引：key ",key, "  value ",value)
                tree1.delete(key_value(key, value))
        elif(table_name=="student"):
            for kv in tree2.search(int(select_value)):
                key=kv.key
                value=kv.value
                print("删除一条关于student表的索引：key ", key, "  value ", value)
                tree2.delete(key_value(key, value))
        # 删除对应的行
        data.pop(delete_index)
        # 保存修改后的文件
        with open(file_name_type, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print("删除成功")


    # 删除数据表：drop_table
    def drop_table(self, small_strings):
        # drop table student ;
        table_name = small_strings[2]
        if (self.is_sure_table_by_database_ID(table_name)):
            self.drop_tb(table_name, small_strings)
        else:
            print("该数据表不存在,删除数据表失败")

    def drop_tb(self, table_name, small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 使用os库来删除文件
        import os
        try:
            shutil.rmtree(file_name_type)
            # 删除./Metadata/Metadata_Database_Table.xlsx'中的数据
            # 读取表格
            # 找到要删除的行的索引
            index = self.dataframe_3[self.dataframe_3['table_name'] == table_name].index
            # 删除对应的行
            self.dataframe_3.drop(index=index, inplace=True)
            # 创建 ExcelWriter 对象
            writer = pd.ExcelWriter(
                './Metadata/Metadata_Database_Table.xlsx', engine='openpyxl')
            # 将数据写入各个工作表
            self.dataframe_1.to_excel(
                writer, sheet_name='Sheet1', index=False)
            self.dataframe_2.to_excel(
                writer, sheet_name='Sheet2', index=False)
            self.dataframe_3.to_excel(
                writer, sheet_name='Sheet3', index=False)
            # 保存 Excel 文件
            writer.save()
            writer.close()
            print("删除数据表成功")
        except FileNotFoundError:
            print("该数据表不存在")


    def is_sure_database_by_account_ID(self, database_name):
        # 检查第0列是否存在和整数类型的account相等的值
        column_index = 2
        # 检查第2列是否存在和整数类型的account相等的值
        column_exists = self.dataframe_2.iloc[:,
                                                column_index] == self.account
        if column_exists.any():
            row_indices = column_exists[column_exists].index.tolist()
            # 验证该行的第1个数是否是database_name
            value_column_index = 1
            rows_with_value = self.dataframe_2.iloc[row_indices,
                                                    value_column_index] == database_name
            for i in range(len(rows_with_value.tolist())):
                if (rows_with_value.tolist()[i] == True):
                    return True
        return False
    
    # 删除数据库：drop_database
    def drop_database(self, small_strings):
        # drop database school ;
        database_name = small_strings[2]
        if (self.is_sure_database_by_account_ID(database_name)):
            self.drop_db(database_name, small_strings)
        else:
            print("该数据库不存在，删除数据库失败")

    def drop_db(self, database_name, small_strings):
        file_name_type = "dbs/{}_{}/".format(
            self.database_ID, database_name)
        # 使用shutil库来删除文件夹
        import shutil
        try:
            shutil.rmtree(file_name_type)
            # 删除./Metadata/Metadata_Database_Table.xlsx'中的数据
            # 读取表格
            # 找到要删除的行的索引
            index = self.dataframe_2[self.dataframe_2['database_name'] == database_name].index
            # 删除对应的行
            self.dataframe_2.drop(index=index, inplace=True)
            # 创建 ExcelWriter 对象
            writer = pd.ExcelWriter(
                './Metadata/Metadata_Database_Table.xlsx', engine='openpyxl')
            # 将数据写入各个工作表
            self.dataframe_1.to_excel(
                writer, sheet_name='Sheet1', index=False)
            self.dataframe_2.to_excel(
                writer, sheet_name='Sheet2', index=False)
            self.dataframe_3.to_excel(
                writer, sheet_name='Sheet3', index=False)
            # 保存 Excel 文件
            writer.save()
            writer.close()
            print("删除数据库成功")
        except FileNotFoundError:
            print("该数据库不存在")

   # 修改数据：update_data
    def update_data(self, small_strings):
        # update student set name = 'Tom' where id = '001' ;
        table_name = small_strings[1]
        update_key = small_strings[3]
        update_value = small_strings[5]
        where_key = small_strings[7]
        where_value = small_strings[9]
        if (self.is_sure_table_by_database_ID(table_name)):
            t = time.perf_counter()
            self.update_dt(table_name, update_key,
                        update_value, where_key, where_value, small_strings)
            print(f'time cost:{time.perf_counter() - t:.18f}s')
        else:
            print("该数据表不存在，修改数据失败")

    def update_dt(self, table_name, update_key,
                update_value, where_key, where_value, small_strings):
        file_name_type = "dbs/{}_{}/{}_{}/data.csv".format(
            self.database_ID, self.database_name, self.table_ID, table_name)
        # 打开CSV文件并读取数据 # select name from student where id = 001 ;
        data = []
        with open(file_name_type, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        t=0
        t1=0
        for i in range(len(data[0])):
            if data[0][i]==where_key:
                t=i
            if data[0][i]==update_key:
                t1=i
        # 无索引修改
        # for i in range(1,len(data)):
        #     if(data[i][t]==where_value):
        #         data[i][t1]=update_value
        # 通过索引查找后修改
        if (table_name == "address"):
            for kv in tree1.search(int(where_value)):
                value = kv.value
                data[value][t1]=update_value
        elif (table_name == "student"):
            for kv in tree2.search(int(where_value)):
                value = kv.value
                data[value][t1]=update_value
        # save
        try:
            with open(file_name_type, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
            print("修改成功")
        except FileNotFoundError:
            print("该数据表不存在")



# db = Database()
# 账号不存在->重新登录/退出系统
# 密码错误->重新登录/注册新账号/退出系统
# 注册新账号->账号已存在->重新登录/重新注册/退出系统
# 不需要密码直接开始
# account=12345
# password="11111111a"
db = Database(True)
