import pytest
import time
import os
import shutil
from common.utils.log import log

def pytest_collection_modifyitems(session, items):
    # items.sort(key=lambda item: (item.parent.name, item.name))

    for item in items:
        print("收集到测试用例名称", item.nodeid)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    file_path = os.path.dirname(log.handlers[0].baseFilename)
    if report.when == "call" and report.failed:
        case_name = report.nodeid.split("::")[-1]
        print(case_name)
        log_time = file_path + "\\" + case_name + "_" + time.strftime("%Y%m%d-%H-%M-%S")
        if case_name == "test_case7_ClockDivider":
            path = "D:\\ATC\\divider"
        elif case_name == "test_case8_SampleTime":
            path = "D:\\ATC\\sample"
        elif case_name == "test_case17_AclkDiv4":
            path = "D:\\ATC\\ACLK_DIV4"
        elif case_name == "test_case18_Parallel":
            path = "D:\\ATC\\parallel"
        elif case_name == "test_case21_Sync":
            path = "D:\\ATC\\sync"
        elif case_name == "test_case22_DualMode":
            path = "D:\\ATC\\dualmode"
        else:
            path = ""
        if path != "":
            shutil.copytree(path, log_time)
            if len(os.listdir(log_time))!=0:
                print("文件夹复制成功")
            else:
                print("文件夹复制失败")
