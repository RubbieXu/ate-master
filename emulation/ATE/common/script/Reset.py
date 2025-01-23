import subprocess
import psutil

from common.utils.log import log

JLinkPath = r'D:\Program Files\SEGGER\JLink\JLink.exe'


def ReSet(mode):
    arg1 = f"connect\n\n\n\n\nRSetType {str(mode)}\n" + "r\n" + "go\n"
    # log.info(arg1)
    try:
        result = subprocess.run(JLinkPath, input=arg1, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            output = result.stdout.strip()
            log.info("\n-------------reset完成-------------")
        else:
            log.info(f"----------fail:reset命令执行出错：{result.stderr}----------")
            raise ValueError(f"---fail:reset命令执行出错：{result.stderr}---")
    except subprocess.TimeoutExpired:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == "JLink.exe":
                proc.kill()
        raise ValueError("-----------fail:reset命令执行超时--------------")
    except subprocess.CalledProcessError as e:
        log.info(f"fail:reset命令执行出错：{e}")