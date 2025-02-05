from register.test_reg import *
from drivers.spi import spi
from usr.test_itf import test_itf


class EVtest:
    def __init__(self):
        self.ip_osc = '192.168.1.10'

    def run(self):
        pass

    def test(self):
        itf = test_itf(spi())
        itf.reset([])
        itf.OSC_output_clock([0x0])


    def write_to_csv(self, data, filename, headers=None):
        """
        将列表中的内容写入CSV文件。

        :param data: 要写入的列表数据
        :param filename: 目标CSV文件的名称
        :param headers: 可选参数，CSV文件的标题行
        """
        # 检查文件是否存在
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # 如果文件不存在且提供了标题行，则写入标题行
            if not file_exists and headers:
                writer.writerow(headers)

            writer.writerows(data)


if __name__ == "__main__":
    test = EVtest()
    test.test()
