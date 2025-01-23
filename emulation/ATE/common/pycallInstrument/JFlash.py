import subprocess

##注意！！
## JFlash.exe 所在路径要设置一下环境变量
##注意！！
def BootLoad_JFlash(HexPath,JFlashPath):

    command = f'cmd /c JFlash.exe -openprj"{JFlashPath}" -open"{HexPath}",0x000000 -auto -exit'
    try:
        output = subprocess.check_output(command, shell=True)
        print(output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"命令执行出错：{e}")
        return False

if __name__ == "__main__":
    HexPath = r'D:\Pro\Instrument Pannel\InstrumentPannelAPP\canfd_flash_qspi2_800M.hex'
    JFlashPath = r'D:\Program Files (x86)\SEGGER\JLink\test1.jflash'
    BootLoad_JFlash(HexPath,JFlashPath)
