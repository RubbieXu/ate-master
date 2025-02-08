# !/usr/bin/python3
# coding=utf-8
import pytest
import time
import os
import argparse
import glob
import shutil
from common.utils.log import Log
# from common.script.relayswitch import switch

log_path = './logs'

# ALL case
test_files_all = [
    # 'case/register/test_reg.py::test_case1_Reset',
    # 'case/register/test_reg.py::test_case2_DefaultValue',
    # 'case/register/test_reg.py::test_case3_WriteReg',
    # 'case/register/test_reg.py::test_case4_RegularSingle',
    # 'case/register/test_reg.py::test_case5_RegularContinuous',
    # 'case/register/test_reg.py::test_case6_Resolution',
    # 'case/register/test_reg.py::test_case7_ClockDivider',
    # 'case/register/test_reg.py::test_case8_SampleTime',
    # 'case/register/test_reg.py::test_case9_Discontinuous_001',
    # # 'case/register/test_reg.py::test_case9_Discontinuous_002',
    'case/register/test_reg.py::test_case10_DMA',
    # # 'case/register/test_reg.py::test_case11_Cali',
    # 'case/register/test_reg.py::test_case12_IOTrigger',
    # 'case/register/test_reg.py::test_case13_Inject',
    # # 'case/register/test_reg.py::test_case14_TriggerManage_001',
    # # 'case/register/test_reg.py::test_case14_TriggerManage_002',
    # 'case/register/test_reg.py::test_case15_SRAM',
    # 'case/register/test_reg.py::test_case16_GPIO',
    # 'case/register/test_reg.py::test_case17_AclkDiv4',
    # 'case/register/test_reg.py::test_case18_Parallel',
    # 'case/register/test_reg.py::test_case19_OverSample',
    # 'case/register/test_reg.py::test_case20_AWD',
    # 'case/register/test_reg.py::test_case21_Sync',
    # 'case/register/test_reg.py::test_case22_DualMode',
    # 'case/register/test_reg.py::test_case23_XCLK_Freq',

                ]
# selected case
test_files_slt = [

                ]
# 模块case
test_files_module = [
    'case/interface/test_hse_no_osc.py',
                     ]


# log文件夹整理
def move_core1_logcat_to_latest_autotest_folder():
    core1_logcat_path = './logs/core1_logcat.txt'
    core2_logcat_path = './logs/core2_logcat.txt'
    autotest_folders = glob.glob('./logs/autotest*')
    latest_autotest_folder = max(autotest_folders, key=os.path.getctime)
    # 移动 core1_logcat.txt 到最近创建的 autotest 文件夹
    destination_folder = latest_autotest_folder
    if os.path.exists(core1_logcat_path):
        shutil.move(core1_logcat_path, destination_folder)
    if os.path.exists(core2_logcat_path):
        shutil.move(core2_logcat_path, destination_folder)


# 生成测试报告
def generate_test_report(test_files, run_count=1, run_duration=None, report_filename='test_report.html'):
    html_report_paths = []
    for i in range(run_count):
        if run_duration:
            # Run tests for the specified duration
            start_time = time.time()
            end_time = start_time + run_duration
            while time.time() < end_time:
                html_report_path = f'./report/{report_filename[:-5]}_{len(html_report_paths) + 1}.html'
                pytest_args = test_files + ['-v', '-s', f'--html={html_report_path}', '--self-contained-html',
                                            '--log-level=DEBUG']
                result = pytest.main(pytest_args)
                html_report_paths.append(html_report_path)
        else:
            html_report_path = f'./report/{report_filename[:-5]}_{i + 1}.html'
            pytest_args = test_files + ['-v', '-s', f'--html={html_report_path}', '--self-contained-html',
                                        '--log-level=DEBUG']
            result = pytest.main(pytest_args)
            html_report_paths.append(html_report_path)

    # 合并报告文件
    merge_reports(report_filename, html_report_paths)
    move_core1_logcat_to_latest_autotest_folder()


def merge_reports(report_filename, html_report_paths):
    merged_report_path = f'./report/{report_filename}'
    with open(merged_report_path, 'w') as merged_report:
        # 写入 HTML 报告头部
        merged_report.write('<html><head><title>Test Report</title></head><body>')
        # 读取并合并各个报告文件内容
        for report_path in html_report_paths:
            with open(report_path, 'r') as report:
                # 跳过 HTML 报告的头部和尾部
                lines = report.readlines()[2:-1]
                # 将报告内容写入合并报告文件
                merged_report.writelines(lines)
            # 删除单个报告文件
            os.remove(report_path)
        # 写入 HTML 报告尾部
        merged_report.write('</body></html>')

def power_on():
    # switch.switching()
    pass

def main():
    power_on()
    parser = argparse.ArgumentParser(description="Run different sets of test cases.")
    parser.add_argument("-all", action="store_true", help="Run all test cases",default=True)
    parser.add_argument("-slt", action="store_true", help="Run selected test cases")
    parser.add_argument("-module", action="store_true", help="Run selected test cases")
    parser.add_argument("-count", type=int, default=1, help="Number of times to run the tests (default: 1)")
    parser.add_argument("-time", type=int, default=None, help="Duration in seconds to run the tests")
    parser.add_argument("-report", default="test_report.html", help="Specify the report filename")
    args = parser.parse_args()
    if args.all:
        generate_test_report(test_files_all, args.count, args.time, args.report)
    elif args.slt:
        generate_test_report(test_files_slt, args.count, args.time, args.report)
    elif args.module:
        generate_test_report(test_files_module, args.count, args.time, args.report)

    else:
        print("Please provide a valid option: -all or -slttest")


class Runner(object):
    if __name__ == '__main__':
        main()
