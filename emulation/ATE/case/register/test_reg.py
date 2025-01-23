from common.common_command.reg_common import *
from common.script.file_control import *
from common.script.excel_control import getExcellAllSheetName
from common.script.Serial_Port import SerialPort
from common.script.Reset import ReSet
from common.utils.log import log
import time
import pytest_repeat
from common.pycallInstrument.LA_KingstVis import CallLA_KingstVis
import csv
import pytest_assume

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
#print(f"当前文件的绝对路径: {current_file_path}")

# 假设根目录在当前文件的上五级目录
root_dir = os.path.abspath(os.path.join(current_file_path, '../../../common/data'))
#print(f"当前文件的绝对路径: {root_dir}")
full_path = os.path.join(root_dir,"reg.yaml")
ADC_data = read_yaml(full_path)  # for run.py
#ADC_data = read_yaml('../../common/data/reg.yaml')  # for single pytest
# ADC_data = read_yaml('./common/data/reg.yaml')  # for run.py
ADC_info = ADC_data[0].get('ADC_INFO')
file_path = log.handlers[0].baseFilename

def sendCmd_andGetReponse(input_cmd):
    start_time = time.time()
    global ateif
    check_data = ateif.execcmd(input_cmd)
    # print(check_data)
    return check_data

def get_ch_width(ch, csv_list):
    # 用于获取csv文件中通道ch首次采样脉宽
    row = 1
    while csv_list[row][ch+1] != " 1":
        row +=1
    on_time = int(float(csv_list[row][0])*1000000000 + 0.5)
    while csv_list[row][ch+1] != " 0":
        row += 1
    off_time = int(float(csv_list[row][0])*1000000000 + 0.5)
    width = off_time - on_time
    print(width)
    return width

def get_ch_on_time(ch, csv_list):
    # 用于获取csv文件中通道ch首次采样时间点
    row = 1
    while csv_list[row][ch+1] != " 1":
        row +=1
    on_time = int(float(csv_list[row][0])*1000000000)
    print(on_time)
    return on_time

def open_log():
    with open(file_path) as f:
        content = f.read()
    return content

def clear_log():
    os.truncate(file_path, 0)

@pytest.fixture(scope="function", autouse=True)
def setup():
    clear_log()


def test_case1_Reset():
    sendCmd_andGetReponse(['if','write',0x40020004, 0x8])
    sendCmd_andGetReponse(['if','read',0x40020004])
    ret = open_log()
    assert ADC_info["RESET_INFO"][0] in ret, "test reset write fail"
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','read',0x40020004])
    ret = open_log()
    assert ADC_info["RESET_INFO"][1] in ret, "test reset fail"

def test_case2_DefaultValue():
    sendCmd_andGetReponse(['if','reset'])
    for i in range(0, 62):
        sendCmd_andGetReponse(['if', 'read', i*4 + 0x40020000])
    ret = open_log()
    default_value_flag = True
    err = []
    for item in ADC_info["DEFAULT_VALUE"]:
        if item not in ret:
            err.append(item)
            default_value_flag = False
    assert default_value_flag, f"test defaultValue fail : can't found {err}"

def test_case3_WriteReg():
    sendCmd_andGetReponse(['if','write',0x40020004, 0x8])
    sendCmd_andGetReponse(['if','read',0x40020004])
    ret = open_log()
    assert ADC_info["WRITE_REG"] in ret, "test write Reg fail"

def test_case4_RegularSingle():
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',1])
    sendCmd_andGetReponse(['if','init',2,0,0,0,0,0,0,0,0])
    sendCmd_andGetReponse(['if','regular',0,10,0])
    for i in range(0, 5):
        sendCmd_andGetReponse(['if','start',0,1])
        time.sleep(0.01)
        sendCmd_andGetReponse(['if','data'])
    ret = open_log()
    for item in ADC_info["REGULAR_SINGLE"]:
        assert item in ret, f"test regularSingle fail : can't found {item}"

def test_case5_RegularContinuous():
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',1])
    sendCmd_andGetReponse(['if','init',2,0,1,0,0,0,0,0,0])
    sendCmd_andGetReponse(['if','regular',0,10,0])
    sendCmd_andGetReponse(['if','start',0,1])
    for i in range(0, 5):
        time.sleep(0.01)
        sendCmd_andGetReponse(['if','data'])

    # ADSTOP
    sendCmd_andGetReponse(['if','start',0,0])
    sendCmd_andGetReponse(['if','data'])
    sendCmd_andGetReponse(['if','data'])
    ret = open_log()
    str_list = re.findall(r"reg = 0x40020070, data = (.*)\n", ret)
    value_list = list(map(lambda x: int(x, 16), str_list))
    for i in range(len(value_list)-1):
        if i != len(value_list)-2:
            # ADSTART：data要求递增
            assert value_list[i] < value_list[i+1], f"test regular continuous fail:{str_list}"
        else:
            # ADSTOP：data不变
            assert value_list[i] == value_list[i+1], f"test regular continuous fail:{str_list}"

def test_case6_Resolution():
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',1])
    sendCmd_andGetReponse(['if','init',2,1,0,0,0,0,0,0,0]) #14 bit
    sendCmd_andGetReponse(['if','regular',0,10,0])
    sendCmd_andGetReponse(['if','start',0,1])
    time.sleep(0.1)
    sendCmd_andGetReponse(['if','data'])

def test_case7_ClockDivider():
    file_dir_path="D:\\ATC\\divider"
    if os.path.exists(file_dir_path):
        os.system(f"rmdir /s /q {file_dir_path}")
    Kingst1 = CallLA_KingstVis(1)
    Kingst1.Configure(1.65, 200000000, 200000, 0.001)
    Kingst1.SetTrigger(0, 2, [0])
    for i in range(0, 12):
        Kingst1.Start(0)
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',i,0,0,0,0,0,0,0,0])
        sendCmd_andGetReponse(['if','regular',0,0,0])
        sendCmd_andGetReponse(['if','start',0,1])
        Kingst1.RecvStartACK()
        Kingst1.SaveData(f"D:\\ATC\\divider\\divider_{i}.kvdat",[])
        Kingst1.SaveData(f"D:\\ATC\\divider\\csv\\divider_{i}.csv",[])
    Kingst1.closeTCP()
    for i in range(0, 12):
        filename=f"D:\\ATC\\divider\\csv\\divider_{i}.csv"
        with open(filename, "r") as csvfile:
            csv_list = list(csv.reader(csvfile))
            # 取第4行第1列数据，这里需要str>float>int（四舍五入）
            cell_value = int(float(csv_list[3][0])*1000000000 + 0.5)
            print(cell_value)
            expect_value = int(ADC_info["CLOCK_DIVIDER"][i])
            with pytest.assume:assert expect_value - 5 <= cell_value <= expect_value + 5, f"test divider{i}fail: value={cell_value}"

def test_case8_SampleTime():
    file_dir_path="D:\\ATC\\sample"
    if os.path.exists(file_dir_path):
        os.system(f"rmdir /s /q {file_dir_path}")
    Kingst1 = CallLA_KingstVis(1)
    Kingst1.Configure(1.65, 200000000, 200000, 0.001)
    Kingst1.SetTrigger(0, 2, [0])
    sampleList = [0, 1, 2, 3, 10, 1022, 1023]
    for i in sampleList:
        Kingst1.Start(0)
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',2,0,0,0,0,0,0,0,0])
        sendCmd_andGetReponse(['if','regular',0,i,0])
        sendCmd_andGetReponse(['if','start',0,1])
        Kingst1.RecvStartACK()
        Kingst1.SaveData(f"D:\\ATC\\sample\\sample_time_{i}.kvdat",[])
        Kingst1.SaveData(f"D:\\ATC\\sample\\csv\\sample_time_{i}.csv",[])
    Kingst1.closeTCP()
    for i in sampleList:
        filename=f"D:\\ATC\\sample\\csv\\sample_time_{i}.csv"
        with open(filename, "r") as csvfile:
            csv_list = list(csv.reader(csvfile))
            # 取第4行第1列数据，这里需要str>float>int（四舍五入）
            cell_value = int(float(csv_list[3][0])*1000000000 + 0.5)
            print(cell_value)
            print(i)
            expect_value = (i + 1)*80
            with pytest.assume:assert expect_value - 5 <= cell_value <= expect_value + 5, f"test sampletime{i}fail: value={cell_value}"

def test_case9_Discontinuous_001():
    # 常规转换时，不同DISCUM的情况
    # Kingst1 = CallLA_KingstVis(1)
    # Kingst1.Configure(1.65, 200000000, 200000, 0.01)
    # Kingst1.SetTrigger(0, 2, [0, 2])
    for i in range(1, 9): #0:disable disc  1:disc=0 8:disc=7
        clear_log()
        print(f'DISCUM={i}: @@@@@@@@@@@@@@@@@@@@@@')
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',2,0,0,15,i,0,0,0,0])
        sendCmd_andGetReponse(['if','regular',0,10,0])
        # Kingst1.Start(0)
        for j in range(0, 5):
            print(f'Start Times:{j}')
            sendCmd_andGetReponse(['if','start',0,1])
            time.sleep(0.1)
            sendCmd_andGetReponse(['if','data'])
        time.sleep(0.01)
        ret = open_log()
        for item in ADC_info["DISCONTINUS_INFO"][i-1]:
            with pytest.assume:assert item in ret, f"test discont fail：can't found {item},discum={i}"
    #     Kingst1.RecvStartACK()
    #     Kingst1.SaveData(f"D:\\ATC\\discont\\discont_{i}.kvdat",[])
    #     Kingst1.SaveData(f"D:\\ATC\\discont\\csv\\discont_{i}.csv",[])
    # Kingst1.closeTCP()

def test_case9_Discontinuous_002():
    # 常规被注入打断时，不同DISCUM的情况
    for i in range(1, 8, 3): # DISCUM = 1,4,7
        print(f'DISCUM={i}: @@@@@@@@@@@@@@@@@@@@@@')
        for t in [3, 4, 5, 6]:
            print(f"===========================================trigger={t}")
            sendCmd_andGetReponse(['if','reset'])
            sendCmd_andGetReponse(['if','sel',1])
            sendCmd_andGetReponse(['if','init',2,0,0,15,i,0,0,0,0])
            sendCmd_andGetReponse(['if','regular',0,10,0])
            # sendCmd_andGetReponse(['if','inject',0,10,0,0,0,0,0,0])
            for j in range(0, 3):
                clear_log()
                print(f'Start Times:{j}')
                print("inject:")
                sendCmd_andGetReponse(['if','start',t,0]) # inject interupt regular
                time.sleep(0.1)
                sendCmd_andGetReponse(['if','data'])
                ret = open_log()
                if t == 4:
                    for item in ADC_info["DISCONTINUS_INFO_2"][3][j]:
                        with pytest.assume:assert item in ret, f"test Discontinuous_002 fail, discum={i},item={item}"
                else:
                    for item in ADC_info["DISCONTINUS_INFO_2"][i//3][j]:
                        with pytest.assume:assert item in ret, f"test Discontinuous_002 fail, discum={i},item={item}"

def test_case10_DMA():
    num = 1
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',num])
    sendCmd_andGetReponse(['if','init',2,0,1,0,0,0,0,0,0]) # continuous
    sendCmd_andGetReponse(['if','regular',0,10,0])
    sendCmd_andGetReponse(['if','dma', num])
    # for i in range(0, 5):
    #     sendCmd_andGetReponse(['if','data'])
    ret = open_log()
    for item in ADC_info["DMA_INFO"]:
        with pytest.assume:assert item in ret, f"test DMA fail: can't found {item}"

def test_case11_Cali():
    Offsetfactor = [
        [0x8000, 0x8001, 0x8002, 0xD554, 0xD555, 0xD556, 0x0000, 0x7FFF, 0x7FFE, 0x0001],
        [0x2000, 0x2001, 0x2002, 0x2554, 0x2555, 0x2556, 0x0000, 0x1FFF, 0x1FFE, 0x0001],
        [0x800,  0x801,  0x802,  0xD54,  0xD55,  0xD56,  0x000,  0x7FF,  0x7FE, 0x001],
        ]

    for res in range(0, 3):
        print(f'resolution:{res}')
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',2,res,0,0,0,0,0,0,0])
        sendCmd_andGetReponse(['if','regular',0,10,0])
        sublist = Offsetfactor[res]
        for i, factor in enumerate(sublist):
            clear_log()
            print(f"factor:{hex(factor)}")
            sendCmd_andGetReponse(['if','cali',1,factor,0])
            sendCmd_andGetReponse(['if','start',0,1])
            time.sleep(0.01)
            sendCmd_andGetReponse(['if','data'])
            ret = open_log()
            with pytest.assume:assert ADC_info["CALI_INFO"][res][i] in ret, f"test cali fail: res={res},factor={factor}"

def test_case12_IOTrigger():
    sendCmd_andGetReponse(['if','reset'])
    for i in range(1, 3):
        if i == 1:
            print(f'regular trigger: @@@@@@@@@@@@@@@@@@@@@@')
            sendCmd_andGetReponse(['if','sel',1])
            sendCmd_andGetReponse(['if','init',2,0,0,0,0,1,0,0,0]) # regular trigger
            sendCmd_andGetReponse(['if','regular',0,10,0])
            sendCmd_andGetReponse(['if','start',0,1]) # regular start

            for j in range(0, 3):
                sendCmd_andGetReponse(['if','hwtrg',1,1,0,0]) # regular enable
                time.sleep(0.01)
                sendCmd_andGetReponse(['if','data'])
        else:
            # 需要打印JDR1~4才能判断
            sendCmd_andGetReponse(['if','reset'])
            print(f'inject trigger: @@@@@@@@@@@@@@@@@@@@@@')
            sendCmd_andGetReponse(['if','sel',1])
            sendCmd_andGetReponse(['if','init',0,0,0,0,0,0,0,0,0])
            sendCmd_andGetReponse(['if','inject',0,10,0,3,1,0,0,0]) # inject trigger
            sendCmd_andGetReponse(['if','start',1,1]) # injected start
            for j in range(0, 3):
                sendCmd_andGetReponse(['if','hwtrg',0,0,1,1]) # inject enable
                time.sleep(0.02)
                sendCmd_andGetReponse(['if','data'])
    ret = open_log()
    for item in ADC_info["IO_TRIGGER"]:
        with pytest.assume:assert item in ret, "test iotrigger fail"

def test_case13_Inject():
    # 需要打印JDR1~4才能判断
    items = ["JADSTART", "JADSTOP", "JAUTO", "JDISCEN"]
    for i, item in enumerate(items):
        clear_log()
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',0,0,0,0,0,0,0,0,0])
        sendCmd_andGetReponse(['if','regular',0,10,0])
        if item == "JADSTART":
            print('JADSTART:@@@@@@@@@@@@@@@@@@@@@@')
            sendCmd_andGetReponse(['if','inject',0,10,0,3,0,0,0,0]) # inject continuous
            sendCmd_andGetReponse(['if','start',1,1]) # inject start
            time.sleep(0.03)
            sendCmd_andGetReponse(['if','data'])
        if item == "JADSTOP":
            print('JADSTOP:@@@@@@@@@@@@@@@@@@@@@@')
            sendCmd_andGetReponse(['if','start',1,0])
            sendCmd_andGetReponse(['if','data'])
        if item == "JAUTO":
            print('JAUTO:@@@@@@@@@@@@@@@@@@@@@@')
            sendCmd_andGetReponse(['if','inject',0,10,0,3,0,0,0,1])
            sendCmd_andGetReponse(['if','start',0,1])
            time.sleep(0.03)
            sendCmd_andGetReponse(['if','data'])
        if item == "JDISCEN":
            print('JDISCEN:@@@@@@@@@@@@@@@@@@@@@@')
            sendCmd_andGetReponse(['if','inject',0,10,0,3,0,0,1,0])
            for i in range(0, 4):
                sendCmd_andGetReponse(['if','start',1,1])
                time.sleep(0.01)
                sendCmd_andGetReponse(['if','data'])
        ret = open_log()
        for result in ADC_info["INJECT_INFO"][i]:
            with pytest.assume:assert result in ret, f"test inject_{item} fail"


def test_case14_TriggerManage_001():
    # 一开始转换就被打断
    # Kingst1 = CallLA_KingstVis(1)
    # Kingst1.Configure(1.65, 200000000, 50000000, 0.25)
    # Kingst1.SetTrigger(0, 2, [0, 2])
    for i in range(2, 7):
        # Kingst1.Start(0)
        clear_log()
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',11,0,0,0,0,0,0,0,0]) # slow sample rate for trigger delay effect
        sendCmd_andGetReponse(['if','regular',0,1000,0])
        sendCmd_andGetReponse(['if','inject',0,1000,0,3,0,0,0,0])
        sendCmd_andGetReponse(['if','start',i,0]) # trigger1-5 遍历
        time.sleep(0.05)
        print(f"trigger{i-1}:@@@@@@@@@@@@@@@@@@@@@@")
        sendCmd_andGetReponse(['if','data'])
        ret = open_log()
        # trigger2可能有两种情况,stm32使用triggerManage的bin，基本上是情况2
        if i == 3:
            flag1 = True
            flag2 = True
            for item1 in ADC_info["TRIGGER_MANAGE"][1][0]:
                if item1 not in ret:
                    flag1 = False
                    print("11111")
                    break
            for item2 in ADC_info["TRIGGER_MANAGE"][1][1]:
                if item2 not in ret:
                    flag2 = False
                    break
            with pytest.assume:assert flag1 or flag2, f"test TriggerManage fail: trigger2 fail"
        else:
            for item in ADC_info["TRIGGER_MANAGE"][i-2]:
                with pytest.assume:assert item in ret, f"test TriggerManage fail: trigger{i-1}fail, can't found {item}"
    #     Kingst1.RecvStartACK()
    #     Kingst1.SaveData(f"D:\\ATC\\TriggerManage\\trigger{i-1}.kvdat",[])
    # Kingst1.closeTCP()

def test_case14_TriggerManage_002():
    # 连续转换过程中打断
    for i in range(0, 4):
        clear_log()
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',11,0,0,0,0,0,0,0,0]) # slow sample rate for trigger delay effect
        sendCmd_andGetReponse(['if','regular',0,1000,0])
        sendCmd_andGetReponse(['if','inject',0,1000,0,3,0,0,0,0])
        if i == 0 or i == 1:
            print("【注入转换第一次：】")
            sendCmd_andGetReponse(['if','start',1, 1]) # trigger 1 #regular interput regualr
            time.sleep(0.05)
            sendCmd_andGetReponse(['if','data'])
            print("【注入转换第二次：】")
            sendCmd_andGetReponse(['if','start',1, 1]) # trigger 1 #regular interput regualr
            time.sleep(0.05)
            sendCmd_andGetReponse(['if','data'])
            #2次注入转换后 使用注入打断注入规则
            if i == 0:
                print("【2次注入转换后   注入打断注入：】")
                sendCmd_andGetReponse(['if','start',4,0]) # trigger 3  inject interput inject
                time.sleep(0.05)
                sendCmd_andGetReponse(['if','data'])
            #2次注入转换后 使用常规打断注入规则
            if i == 1:
                print("【2次注入转换后  常规打断注入：】")
                sendCmd_andGetReponse(['if','start',5,0]) # trigger 4 regular interput inject
                time.sleep(0.05)
                sendCmd_andGetReponse(['if','data'])
        if i == 2 or i == 3:
            print("【常规转换第一次：】")
            sendCmd_andGetReponse(['if','start',0, 1]) # trigger 1 #regular interput regualr
            time.sleep(0.05)
            sendCmd_andGetReponse(['if','data'])
            print("【常规转换第二次：】")
            sendCmd_andGetReponse(['if','start',0, 1]) # trigger 1 #regular interput regualr
            time.sleep(0.05)
            sendCmd_andGetReponse(['if','data'])
            #2次常规转换后 使用注入打断常规，常规被打断
            if i == 2:
                print("【2次常规转换后  注入打断常规：】")
                sendCmd_andGetReponse(['if','start',3,0]) # trigger 2  inject interput regular
                time.sleep(0.05)
                sendCmd_andGetReponse(['if','data'])
            #2次常规转换后 使用同一时刻转换规则，注入优先转换
            if i == 3:
                print("【2次常规转换后  常规和注入同一时刻转换：】")
                sendCmd_andGetReponse(['if','start',6,0]) # trigger 5
                time.sleep(0.05)
                sendCmd_andGetReponse(['if','data'])
        ret = open_log()
        for item in ADC_info["TRIGGER_MANAGE_2"][i]:
            with pytest.assume:assert item in ret, f"test TriggerManage_002 fail, 第{i+1}种情况出错，can't found {item}"


def test_case15_SRAM():
    sendCmd_andGetReponse(['if','reset'])
    for i in range(0, 32): # 32768
        sendCmd_andGetReponse(['if','write', i*4 + 0x30000000, i+1])
        sendCmd_andGetReponse(['if','read', i*4 + 0x30000000])
        ret = open_log()
        reg = hex(i*4 + 0x30000000)
        with pytest.assume:assert f"reg = {reg}, data = {hex(i+1)}" in ret, f"test SRAM fail：can't found {hex(i+1)}"

def test_case16_GPIO():
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',1])

    # GPIO output/input
    for dir in range(0, 2):
        for pin in range(4, 25):
        # pin = 22 # 4:P0V33  21:P17V33
            # dir = 0 # 0:output 1:input
            level = 1
            print(f"pin = {pin}, dir = {dir}")
            sendCmd_andGetReponse(['if','iodata',pin,level])
            sendCmd_andGetReponse(['if','iodir',pin,dir])
            # sendCmd_andGetReponse(['if','iodata','0'])
            ret = open_log()
            assert ADC_info["GPIO_INFO"][dir][pin-4] in ret, f"test GPIO fail：pin={pin}, dir={dir}"

def test_case17_AclkDiv4():
    file_dir_path="D:\\ATC\\ACLK_DIV4"
    if os.path.exists(file_dir_path):
        os.system(f"rmdir /s /q {file_dir_path}")
    Kingst1 = CallLA_KingstVis(1)
    Kingst1.Configure(1.65, 200000000, 200000, 0.001)
    Kingst1.SetTrigger(0, 2, [11]) # P19 adc1
    Kingst1.Start(0)
    # P19V33 P20V33
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',1])
    sendCmd_andGetReponse(['if','init',1,0,0,0,0,0,0,0,0])
    # sendCmd_andGetReponse(['if','regular',0,10,0])
    sendCmd_andGetReponse(['if','aclk',1,0])
    Kingst1.RecvStartACK()
    Kingst1.SaveData(f"D:\\ATC\\ACLK_DIV4\\ACLK_DIV4_divider_adc1.kvdat",[])
    Kingst1.SaveData(f"D:\\ATC\\ACLK_DIV4\\ACLK_DIV4_divider_adc1.csv",[])
    filename=f"D:\\ATC\\ACLK_DIV4\\ACLK_DIV4_divider_adc1.csv"
    with open(filename, "r") as csvfile:
        csv_list = list(csv.reader(csvfile))
        # 取第5行第1列数据，这里需要str>float>int（四舍五入）
        cell_value = int(float(csv_list[4][0])*1000000000 + 0.5)
        print(cell_value)
        expect_value = 80
        with pytest.assume:assert expect_value - 5 <= cell_value <= expect_value + 5, f"test aclk_div4 fail: value={cell_value}"

    Kingst1.SetTrigger(0, 2, [4]) # P20 adc2
    Kingst1.Start(0)
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',2])
    sendCmd_andGetReponse(['if','init',1,0,0,0,0,0,0,0,0])
    sendCmd_andGetReponse(['if','aclk',0,1])
    Kingst1.RecvStartACK()
    Kingst1.SaveData(f"D:\\ATC\\ACLK_DIV4\\ACLK_DIV4_divider_adc2.kvdat",[])
    Kingst1.SaveData(f"D:\\ATC\\ACLK_DIV4\\ACLK_DIV4_divider_adc2.csv",[])
    filename=f"D:\\ATC\\ACLK_DIV4\\ACLK_DIV4_divider_adc2.csv"
    with open(filename, "r") as csvfile:
        csv_list = list(csv.reader(csvfile))
        # 取第5行第1列数据，这里需要str>float>int（四舍五入）
        cell_value = int(float(csv_list[4][0])*1000000000 + 0.5)
        print(cell_value)
        expect_value = 80
        assert expect_value - 5 <= cell_value <= expect_value + 5, f"test aclk_div4 fail: value={cell_value}"

    Kingst1.closeTCP()

def test_case18_Parallel():
    file_dir_path="D:\\ATC\\parallel"
    if os.path.exists(file_dir_path):
        os.system(f"rmdir /s /q {file_dir_path}")
    Kingst1 = CallLA_KingstVis(1)
    Kingst1.Configure(1.65, 200000000, 10000000, 0.05)
    # CH0:adc_clk CH2:adc_eoc CH5:P1V33 CH6:P2V33 CH7:P3V33 CH8:P0V33
    Kingst1.SetTrigger(0, 2, [2, 5, 6, 7, 8, 0])

    print("test analog_parallel:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    Kingst1.Start(0)
    time.sleep(1)
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',1])
    # PV033:EOC P16V33:D15
    sendCmd_andGetReponse(['if','parallel',0,1,0,0])   #analog
    sendCmd_andGetReponse(['if','init',0,0,0,0,0,0,0,0,0])
    sendCmd_andGetReponse(['if','regular',0,10,0])
    for i in range(0, 1):
        sendCmd_andGetReponse(['if','start',0,1])
        time.sleep(0.01)
        sendCmd_andGetReponse(['if','data'])
    Kingst1.RecvStartACK()
    Kingst1.SaveData(f"D:\\ATC\\parallel\\analog_parallel_out.kvdat",[])
    Kingst1.SaveData(f"D:\\ATC\\parallel\\analog_parallel_out.csv",[])
    ret = open_log()
    for item in ADC_info["PARALLEL_INFO"]:
        with pytest.assume:assert item in ret, "test parallel fail:data error"
    filename=f"D:\\ATC\\parallel\\analog_parallel_out.csv"
    with open(filename, "r") as csvfile:
        csv_list = list(csv.reader(csvfile))
        clk = get_ch_width(0, csv_list)
        with pytest.assume:assert 215 <= clk <= 225, "test parallel fail:clk error"
        eoc = get_ch_width(2, csv_list)
        with pytest.assume:assert 260 <= eoc <= 270, "test parallel fail:eoc error"
        aeoc = get_ch_width(8, csv_list)
        expect_aeoc = 265
        with pytest.assume:assert expect_aeoc - 5 <= aeoc <= expect_aeoc + 5, f"test analog_parallel fail: aeoc={aeoc_width}"

    print("test digital_parallel:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    expect_aeoc = [200, 400, 600, 800]
    # width=0/1/2/3
    for w in range(0, 4):
        clear_log()
        Kingst1.Start(0)
        time.sleep(1)
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        # PV033:EOC P16V33:D15
        sendCmd_andGetReponse(['if','parallel',1,0,w,0])   #digital
        sendCmd_andGetReponse(['if','init',0,0,0,0,0,0,0,0,0])
        sendCmd_andGetReponse(['if','regular',0,10,0])
        for i in range(0, 1):
            sendCmd_andGetReponse(['if','start',0,1])
            time.sleep(0.01)
            sendCmd_andGetReponse(['if','data'])
        Kingst1.RecvStartACK()
        Kingst1.SaveData(f"D:\\ATC\\parallel\\digital_parallel_out_width{w}.kvdat",[])
        Kingst1.SaveData(f"D:\\ATC\\parallel\\digital_parallel_out_width{w}.csv",[])
        ret = open_log()
        for item in ADC_info["PARALLEL_INFO"]:
            with pytest.assume:assert item in ret, "test parallel fail:data error"
        filename=f"D:\\ATC\\parallel\\digital_parallel_out_width{w}.csv"
        with open(filename, "r") as csvfile:
            csv_list = list(csv.reader(csvfile))
            clk = get_ch_width(0, csv_list)
            with pytest.assume:assert 215 <= clk <= 225, "test parallel fail:clk error"
            eoc = get_ch_width(2, csv_list)
            with pytest.assume:assert 260 <= eoc <= 270, "test parallel fail:eoc error"
            aeoc = get_ch_width(8, csv_list)
            with pytest.assume:assert expect_aeoc[w] - 5 <= aeoc <= expect_aeoc[w] + 5, f"test analog_parallel fail: aeoc={aeoc_width},width={w}"
    Kingst1.closeTCP()

def test_case19_OverSample():
    ratioList = [0, 1, 2, 10]
    # ratioList = [10]
    for i in ratioList:
        sendCmd_andGetReponse(['if','reset'])
        sendCmd_andGetReponse(['if','sel',1])
        sendCmd_andGetReponse(['if','init',2,0,0,0,0,0,1,i,0]) # regular avg
        sendCmd_andGetReponse(['if','regular',0,0,0])
        sendCmd_andGetReponse(['if','start',0,1])

        # sendCmd_andGetReponse(['if','inject',0,0,0,0,0,0,0,0])
        # sendCmd_andGetReponse(['if','start',1,1]) # inject start

        time.sleep(0.5)
        sendCmd_andGetReponse(['if','data'])
    ret = open_log()
    for item in ADC_info["OVER_SAMPLE"]:
        with pytest.assume:assert item in ret, f"test oversample fail, can't found {item}"

def test_case20_AWD():
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','sel',1])
    sendCmd_andGetReponse(['if','write',0x50000008, 1 << 15])
    sendCmd_andGetReponse(['if','init',2,0,0,0,0,0,0,0,0])
    sendCmd_andGetReponse(['if','regular',0,0,0])
    sendCmd_andGetReponse(['if','awd',0,0,0x5558,0x5556])
    for i in range(0, 5):
        clear_log()
        sendCmd_andGetReponse(['if','start',0,1])
        sendCmd_andGetReponse(['if','data'])
        sendCmd_andGetReponse(['if','read',0x50000004])
        ret = open_log()
        if i==0 or i==4:
            with pytest.assume:assert ADC_info["AWD_ON"] in ret, "test AWD_ON fail"
        else:
            with pytest.assume:assert ADC_info["AWD_OFF"] in ret, "test AWD_OFF fail"

def test_case21_Sync():
    file_dir_path="D:\\ATC\\sync"
    if os.path.exists(file_dir_path):
        os.system(f"rmdir /s /q {file_dir_path}")
    Kingst1 = CallLA_KingstVis(1)
    Kingst1.Configure(1.65, 200000000, 20000000, 0.1)
    Kingst1.SetTrigger(0, 2, [0, 1])
    Kingst1.Start(0)
    sendCmd_andGetReponse(['if','reset'])
    for i in range(1, 3):
        sendCmd_andGetReponse(['if','sel',i])
        sendCmd_andGetReponse(['if','init',2,0,0,0,0,1,0,0,0]) # regular trigger
        sendCmd_andGetReponse(['if','regular',0,10,0])
        sendCmd_andGetReponse(['if','start',0,1]) # regular start

    sendCmd_andGetReponse(['if','sync',1,0,1])

    sendCmd_andGetReponse(['if','hwtrg',1,1,0,0]) # regular enable
    sendCmd_andGetReponse(['if','sel',1])
    sendCmd_andGetReponse(['if','data'])
    sendCmd_andGetReponse(['if','sel',2])
    sendCmd_andGetReponse(['if','data'])
    Kingst1.RecvStartACK()
    Kingst1.SaveData(f"D:\\ATC\\sync\\sync_clk.kvdat",[])
    Kingst1.SaveData(f"D:\\ATC\\sync\\sync_clk.csv",[])
    Kingst1.closeTCP()
    filename=f"D:\\ATC\\sync\\sync_clk.csv"
    with open(filename, "r") as csvfile:
        csv_list = list(csv.reader(csvfile))
        sync = abs(get_ch_on_time(1, csv_list) - get_ch_on_time(0,csv_list))
        assert sync == 0 or sync == 5, "test sync fail：sync error"
        # clk = int(float(csv_list[3][0])*1000000000 + 0.5)
        clk1 = get_ch_width(0, csv_list)
        clk2 = get_ch_width(1, csv_list)
        expect_value = 220
        with pytest.assume:assert expect_value - 5 <= clk1 <= expect_value + 5, f"test sync fail：ADC1 time error"
        with pytest.assume:assert expect_value - 5 <= clk2 <= expect_value + 5, f"test sync fail：ADC2 time error"

def test_case22_DualMode():
    file_dir_path="D:\\ATC\\dualmode"
    if os.path.exists(file_dir_path):
        os.system(f"rmdir /s /q {file_dir_path}")
    Kingst1 = CallLA_KingstVis(1)
    Kingst1.Configure(1.65, 200000000, 10000000, 0.25)
    Kingst1.SetTrigger(0, 2, [0, 1])

    print("test regular + delay @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    delay = [5, 10]
    for item in delay:
        Kingst1.Start(0)
        sendCmd_andGetReponse(['if','reset'])
        for i in range(1, 3):
            sendCmd_andGetReponse(['if','sel',i])
            sendCmd_andGetReponse(['if','init',0,0,0,0,0,1,0,0,0]) # regular trigger
            sendCmd_andGetReponse(['if','regular',0,10,0])
            sendCmd_andGetReponse(['if','start',0,1]) # regular start
        sendCmd_andGetReponse(['if','dual',item,0]) # delay trigger
        for i in range(0, 5):
            sendCmd_andGetReponse(['if','hwtrg',1,1,0,0]) # regular enable
            sendCmd_andGetReponse(['if','data'])
        Kingst1.RecvStartACK()
        Kingst1.SaveData(f"D:\\ATC\\dualmode\\regular_trigger_{item}.kvdat",[])
        Kingst1.SaveData(f"D:\\ATC\\dualmode\\csv\\regular_trigger_{item}.csv",[])
        filename=f"D:\\ATC\\dualmode\\csv\\regular_trigger_{item}.csv"
        with open(filename, "r") as csvfile:
            csv_list = list(csv.reader(csvfile))
            clk = abs(get_ch_on_time(1, csv_list) - get_ch_on_time(0,csv_list))
            with pytest.assume:assert item*20-5 <= clk <= item*20+5 , f"test regular + delay_{item} fail：time {clk}"

    # print("test inject + alter @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # Kingst1.SetTrigger(0, 2, [0, 1])
    # Kingst1.Start(0)
    # sendCmd_andGetReponse(['if','reset'])
    # for i in range(1, 3):
    #     sendCmd_andGetReponse(['if','sel',i])
    #     sendCmd_andGetReponse(['if','init',0,0,0,0,0,1,0,0,0])
    #     sendCmd_andGetReponse(['if','inject',0,10,0,3,1,0,0,0]) # inject trigger
    #     sendCmd_andGetReponse(['if','start',1,1]) # injected start
    # # sendCmd_andGetReponse(['if','dual',10,0]) # delay trigger
    #     sendCmd_andGetReponse(['if','dual',0,i]) # alter trigger
    # for i in range(0, 1):
    #     sendCmd_andGetReponse(['if','hwtrg',0,0,1,1]) # inject enable
    #     sendCmd_andGetReponse(['if','data'])
    # Kingst1.RecvStartACK()
    # Kingst1.SaveData(f"D:\\ATC\\dualmode\\inject_alter.kvdat",[])
    # Kingst1.SaveData(f"D:\\ATC\\dualmode\\csv\\inject_alter.csv",[0, 10])
    # filename=f"D:\\ATC\\dualmode\\csv\\inject_alter.csv"
    # # with open(filename, "r") as csvfile:
    # #     csv_list = list(csv.reader(csvfile))
    # #     clk = abs(get_ch_on_time(10, csv_list) - get_ch_on_time(0,csv_list))
    # #     assert clk == 0, "test inject+alter fail：sync error"

    print("test regular + alter @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    Kingst1.Configure(1.65, 200000000, 10000000, 0.5)
    Kingst1.SetTrigger(0, 2, [0, 1])
    Kingst1.Start(0)
    sendCmd_andGetReponse(['if','reset'])
    for i in range(1, 3):
        sendCmd_andGetReponse(['if','sel',i])
        sendCmd_andGetReponse(['if','init',0,0,0,0,0,1,0,0,0]) # regular trigger
        sendCmd_andGetReponse(['if','regular',0,10,0])
        sendCmd_andGetReponse(['if','start',0,1]) # regular start
        sendCmd_andGetReponse(['if','dual',0,i]) # alter trigger adc1:奇 adc2：偶
    for i in range(0, 5):
        sendCmd_andGetReponse(['if','hwtrg',1,1,0,0]) # regular enable
        sendCmd_andGetReponse(['if','data'])
    Kingst1.RecvStartACK()
    Kingst1.SaveData(f"D:\\ATC\\dualmode\\regular_alter.kvdat",[])
    Kingst1.SaveData(f"D:\\ATC\\dualmode\\csv\\regular_alter.csv",[0, 1])
    filename=f"D:\\ATC\\dualmode\\csv\\regular_alter.csv"
    with open(filename, "r", newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader) # 读取并忽略第一行
        c0_index = header.index(" 通道 0") # 找到列名所在的索引
        c1_index = header.index(" 通道 1")# 找到列名所在的索引
        list_0=[]
        list_1=[]
        for row in csv_reader:
            list_0.append(row[c0_index])
            list_1.append(row[c1_index])
        print(list_0, list_1)
        expect_0 = [' 0', ' 0', ' 0', ' 1', ' 0', ' 0', ' 0', ' 1', ' 0', ' 0', ' 0']
        expect_1 = [' 0', ' 1', ' 0', ' 0', ' 0', ' 1', ' 0', ' 0', ' 0', ' 1', ' 0']
        assert list_0 == expect_0 and list_1 == expect_1, "test regular + alter fail：sync error"

    Kingst1.closeTCP()

def test_case23_XCLK_Freq(probe_clk0_div=0x17, p19v33_ds=0x0):
    sendCmd_andGetReponse(['if','reset'])
    sendCmd_andGetReponse(['if','hsetest', probe_clk0_div, p19v33_ds])


def test_case00():
    print("just for debug")

# if __name__ == '__main__':
    # test_case14_TriggerManage()