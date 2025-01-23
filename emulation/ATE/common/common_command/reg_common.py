import re
import time

from common.script.excel_control import *
from common.script.Reset import ReSet
from common.utils.log import log
from common.global_var.globalvar import *

# def sendCmd_andGetReponse(input_cmd):
#     start_time = time.time()
#     global ateif
#     check_data = ateif.execcmd(input_cmd)
#     return check_data

# def resetddic():
#     cmd_list = ['if','rst','0']
#     sendCmd_andGetReponse(cmd_list)
#     cmd_list = ['if','rst','1']
#     sendCmd_andGetReponse(cmd_list)

# def writeRam_byAddress(  input_header: str,sheet_name_list):
#     for sheet_name in sheet_name_list:
#         address_rowNum = find_headerNum('Name', sheet_name)
#         # 通过input_header获取row_num,再通过两个rowName获取sheet数据字典
#         input_header_rowNum = find_headerNum(input_header, sheet_name)

#         dict1 = readSheetByName_outputDic_effectRow(address_rowNum, input_header_rowNum, sheet_name)
#         log.info(dict1)
#         # # 定义保存数据的list
#         # output_list = [input_header]
#         resetddic()
#         # 遍历字典通过key(address)获取返回的十六进制数再对比excel读取的数据
#         for value_list, value  in dict1.items():
#             # print(value_list, value)
#             cmd_list = ['if', 'write','','']
#             cmd_list[2] = str(value_list)
#             cmd_list[3] = str(value)

#             response = sendCmd_andGetReponse(cmd_list)

#     return True


# def getSdata_compareWithEdata(input_header: str, sheet_name_list: list):
#     # 遍历输入的sheet_name列表
#     for sheet_name in sheet_name_list:
#         address_rowNum = find_headerNum('Name', sheet_name)
#         log.info(f"address rownum = {address_rowNum} ")
#         # 通过input_header获取row_num,再通过两个rowName获取sheet数据字典
#         input_header_rowNum = find_headerNum(input_header, sheet_name)
#         log.info(f"input_header_rowNum = {input_header_rowNum} ")

#         dict1 = readSheetByName_outputDic_effectRow(address_rowNum, input_header_rowNum, sheet_name)
#         log.info(dict1)
#         # # 定义保存数据的list
#         # output_list = [input_header]
#         result = True
#         # 遍历字典通过key(address)获取返回的十六进制数再对比excel读取的数据
#         for value_list, value  in dict1.items():
#             # print(value_list, value)
#             cmd_list = ['if', 'read','']
#             cmd_list[2] = str(value_list)
#             # print(cmd_list)

#             response = sendCmd_andGetReponse(cmd_list)
#             # print(f'resp = {response} value = {value}')
#             #返回信息为真，对返回信息处理，提取read data后的十六进制数

#             if value == 'IGNORE':
#                 continue

#             if response == int(value, 16):
#                 log.info(f"pass   {sheet_name} {value_list}读取值为{hex(response)}，与{value}值相等\n")
#             else:
#                 result = False
#                 log.error(f"fail {sheet_name} {value_list}读取值与{value}不等，读取值：{hex(response)}，")

#     assert result

#     return True

# def testexcelrow(sheet_name:str):
#     maxrow = getmaxval(sheet_name)
#     cmd_length = 13
#     cmd_list = [''] * cmd_length

#     cmd_list[0] = 'if'

#     resetddic()
#     print('')

#     for i in range(2, maxrow, 2):
#         banksel = 0
#         cmd_list[1] = 'rw'
#         resultstr = True
#         rowdata = getrowvalue(sheet_name, i)
#         # print(rowdata)

#         if rowdata[1] == 1: # bank0 select
#             banksel = banksel | (0x1 << 0)
#         if rowdata[2] == 1:
#             banksel = banksel | (0x1 << 1)
#         if rowdata[3] == 1:
#             banksel = banksel | (0x1 << 2)


#         cmd_list[2] = hex(banksel)
#         for c in range(3, cmd_length):
#             cmd_list[c] = rowdata[c+1]


#         print(cmd_list)

#         response = sendCmd_andGetReponse(cmd_list)
#         # 回读

#         cmd_list[1] = 'rr'
#         rowdata = getrowvalue(sheet_name, i + 1)
#         # print(cmd_list[:4])
#         response = sendCmd_andGetReponse(cmd_list[:4])
#         # print(response)

#         for d in range(0, len(response)):
#             if (hex(response[d]) != rowdata[5+d]):
#                 print(f'Compare Fail {hex(response[d])} != {rowdata[4+d]}')
#                 resultstr = False

#         if resultstr == True:
#             print(f'Row {i} {i+1} Test OK.')
#         else:
#             print(f'Row {i} {i+1} Test Fail.')

#     assert resultstr

# def rramallbanktest():

#     resetddic()

#     cmd_list = ['if','rt','default','0xff']
#     res = sendCmd_andGetReponse(cmd_list)
#     assert res
#     cmd_list = ['if','rt','random','10']
#     res = sendCmd_andGetReponse(cmd_list)
#     assert res
#     cmd_list = ['if','rt','cycling','1']
#     res = sendCmd_andGetReponse(cmd_list)
#     assert res