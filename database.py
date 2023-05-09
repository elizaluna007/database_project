import xlwings as xw
import pandas as pd
import re
import os
import csv
import json


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
            writer._save()
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
            self.create_database()
        # 创建数据表
        elif (small_strings[0] == "create" and small_strings[1] == "table"):
            self.create_table(small_strings)

        # 插入数据
        elif (small_strings[0] == "insert" and small_strings[1] == "into"):
            self.insert_data(small_strings)

        # --------------u should add the other instruction here--------------------------------

        else:
            print("该指令非法")

    def insert_data(self, small_strings):
        table_name = small_strings[2]
        if (self.is_sure_table_by_database_ID(table_name)):
            self.insert_dt(table_name, small_strings)
        else:
            print("该数据表名称非法,插入数据失败")

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

        print(data_type)
        print(data)

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
        print(data_insert_name)
        print(data_insert_data)
        result = ["" for i in range(len(data[0]))]
        key = 1
        for i in range(len(data_insert_data)):
            b, n = self.insert_dt_select(
                data_type, data, data_insert_name[i], data_insert_data[i])
            key = key and b
            result[n] = data_insert_data[i]
        if (b):
            print("插入")
        else:
            print("数据有误")

    def insert_dt_select(self, type, data, name_now, data_now):
        key = 1
        # i是该数据的位置
        for i in range(len(type)):
            if (type[i][0] == name_now):
                break
        print("index is ", i)
        # check
        if (type[i][2] != ""):
            print(type[i][2])

        # primary key
        if (type[i][4] == True):
            for j in data:
                if (j[i-1] == data_now):
                    key = 0
        # unique
        if (type[i][5] == True):
            for j in data:
                if (j[i-1] == data_now):
                    key = 0
        # foreign key
        if (type[i][7] != ""):
            print(type[i][7])
        return key, i-1

    def create_table(self, small_strings):
        table_name = small_strings[2]
        if (self.is_sure_table_by_database_ID(table_name)):
            print("该数据表名称非法,创建数据表失败")
        else:
            self.create_tb(table_name, small_strings)

    def create_tb(self, table_name, small_strings):
        id_left = self.database_ID[2:]
        id_right = str(hash(table_name)).zfill(9)[1:9]
        id = "tb"+id_left+id_right
        if (self.is_sure_table(id)):
            print("该数据表名称非法,创建数据表失败")
        else:
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
            #     writer._save()
            #     writer.close()
            # 创建一个数据表就是创建一个dbs/db_ID_db_name_/tb_ID_tb_name的文件夹，其中包含类型文件以及存储数据文件
            folder_name = "dbs/{}_{}/{}_{}".format(
                self.database_ID, self.database_name, id, table_name)
            if not os.path.exists(folder_name):  # 如果文件夹不存在则创建
                os.mkdir(folder_name)

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
                    for ii in range(len(result)):
                        if (result[ii][0] == name):
                            result[ii][7] = small_strings[i+6] + \
                                "("+small_strings[i+8]+")"
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
                    # id INT NOT NULL
                    if (i+3 < len(small_strings) and small_strings[i+2] == "not" and small_strings[i+3] == "null"):
                        # name VARCHAR NOT NULL UNIQUE
                        if (i+4 < len(small_strings) and small_strings[i+4] == "unique"):
                            r = [name, type, "", "", False, True, True, ""]
                            result.append(r)
                            i = i+5
                        else:
                            r = [name, type, "", "", False, False, True, ""]
                            result.append(r)
                            i = i+4
                     # id INT UNIQUE
                    elif (i+1 < len(small_strings) and small_strings[i+1] == "unique"):
                        # name VARCHAR UNIQUE NOT NULL
                        if (i+4 < len(small_strings) and small_strings[i+3] == "not" and small_strings[i+4] == "null"):
                            r = [name, type, "", "", False, True, True, ""]
                            result.append(r)
                            i = i+2
                        else:
                            r = [name, type, "", "", False, True, False, ""]
                            result.append(r)
                            i = i+2

                    else:
                        print(small_strings[i])
                        r = [name, type, "", "", False, False, False, ""]
                        result.append(r)
                        i = i+2
                else:
                    if (small_strings[i] == "(" or small_strings[i] == ")"):
                        i = i+1
                    else:
                        print("您输入的指令错误")
                        break
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
            print(result_data)
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
            writer._save()
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
            #     writer._save()
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
            writer._save()
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


# db = Database()
# 账号不存在->重新登录/退出系统
# 密码错误->重新登录/注册新账号/退出系统
# 注册新账号->账号已存在->重新登录/重新注册/退出系统
# 不需要密码直接开始
# account=12345
# password="11111111a"
db = Database(True)
