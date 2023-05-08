import xlwings as xw
import pandas as pd
import re


class Database:
    # 数据库初始化
    def __init__(self, choose=None):
        print("欢迎登录数据库系统")
        self.path = None  # 数据库路径，即工作簿的路径
        # self.app = None  # 创建Excel应用程序的实例
        self.wb = None  # 一个 Excel 工作簿
        self.config = None  # Excel 工作簿中的一个工作表
        self.database_ID = None  # 当前正在使用的数据库ID
        self.field_col = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        self.length_col = '0'
        self.account = None  # 账户ID
        self.password = None  # 账户密码
        self.database_name = None  # 要登录的数据库
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
            line = input("请输入您的指令(exit退出系统):")
            while (line != "exit"):
                self.instruction(line)
                line = input("请输入您的指令(exit退出系统):")

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
                print(f'账号 {self.account} 成功登录')
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
                else:
                    print("系统已退出")
        else:
            print(f"当前账号 {self.account} 不存在，请选择重新登录(T)或注册(F)或退出系统(OTHER)")
            choice = input()
            if (choice == 'T'):
                self.login()  # 登录
            elif (choice == 'F'):
                self.register()  # 注册
            else:
                print("系统已退出")

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
                print("系统已退出")

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
            writer._save()
            writer.close()

    def instruction(self, input_string):
       # 定义分隔符的正则表达式模式
        pattern = r"\s+|\(|\)|,|;"

        # 使用正则表达式的 split() 方法按照模式进行分割
        small_strings = re.split(pattern, input_string)

        # 去除空字符串
        small_strings = [
            string for string in small_strings if string.strip() != ""]

        # 如果还未选择数据库，需要先选择数据库
        if (self.database_name == None and small_strings[0] != "use" and small_strings[0] != "create"):
            print("请先选择数据库")
            return

        # 选择数据库
        elif (small_strings[0] == "use"):
            self.database_name = small_strings[1]
            self.use_database()

        # 创建数据库
        elif (small_strings[0] == "create" and small_strings[1] == "database"):
            self.database_name = small_strings[2]
            self.create_database()
        else:
            # u should do here
            return

    def create_db(self):
        id_left = str(self.account).zfill(8)
        id_right = str(hash(self.database_name)).zfill(9)[1:9]
        id = 'db'+id_left+id_right
        if (self.is_sure(id)):
            print("该数据库名称非法,创建数据库失败")
        else:
            self.database_ID = id
            try:
                self.path = f'dbs/{self.database_ID}.xlsx'
                self.wb = xw.Book(self.path)
                self.config = self.wb.sheets["Sheet1"]
            except FileNotFoundError:
                self.wb = xw.Book()
                self.wb.save(self.path)
                print(
                    f"已创建数据库: {self.database_name}: dbs/{self.database_ID}.xlsx")
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
                writer._save()
                writer.close()

    def create_database(self):
        print("begin create database")
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
                    print(f"该数据库 {self.database_name} 已建立过，无需重复创建")
                    return
            # 该用户没有建立过该名称的数据库
            # 创建数据库
            self.create_db()
        else:
            # 创建数据库
            self.create_db()

    def is_sure(self, id):
        print("开始检查", id)
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
                    print(f"成功选择数据库 {self.database_name} ")
                    break
            if (key == 0):
                print(f"您选择的数据库 {self.database_name} 不存在")

    # def create_table(self, table_name: str, pr_key: str, field: list[str]):
    #     table_length = len(field)

    #     if len(field) > 12:
    #         print("create table: 字段数量超过十个了！")
    #         return
    #     try:
    #         _ = self.wb.sheets[table_name]
    #         print("create table: 已经存在同名表了！")
    #     except:
    #         rows = self.config.used_range.last_cell.row
    #         self.config.range('A' + str(rows + 1)).value = table_name
    #         self.config.range('B' + str(rows + 1)).value = pr_key
    #         for i in range(len(field)):
    #             self.config.range(
    #                 self.field_col[i] + str(rows + 1)).value = field[i]
    #         self.config.range(self.length_col + str(rows + 1)
    #                           ).value = table_length
    #         self.wb.sheets.add(table_name)
    #         self.wb.save()
    #         print("create table: 创建成功！！")

    # def insert(self, table_name: str, pr_key, field: list[str]):
    #     try:
    #         table = self.wb.sheets[table_name]
    #     except:
    #         print("insert: 没有该表!")
    #         return
    #     if not self.check_field(table_name, field):
    #         return

    #     row = 1
    #     while True:
    #         x = table.range('B' + str(row)).value
    #         if x is None:
    #             table.range('B' + str(row)).value = pr_key
    #             for i in range(len(field)):
    #                 table.range(self.field_col[i] + str(row)).value = field[i]
    #             self.wb.save()
    #             print(f"insert: 插入成功！pr_key={pr_key}")
    #             return
    #         if x == pr_key:
    #             print(f"insert: 已经存在相同主键{pr_key}")
    #             return
    #         elif pr_key < x:
    #             row = row  2
    #         else:
    #             row = row  2 + 1


db = Database()
# 账号不存在->重新登录/退出系统
# 密码错误->重新登录/注册新账号/退出系统
# 注册新账号->账号已存在->重新登录/重新注册/退出系统
