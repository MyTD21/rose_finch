import time
import subprocess
import GPUtil
import os
import torch
import logging
import subprocess
import threading

from datetime import datetime

def get_gpu_count():
    result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    gpu_list = output.strip().split('\n')
    return len(gpu_list)


def gpu_occpy():
    gpu_count = get_gpu_count()
#    print(f"Number of GPUs: {gpu_count}")
#    print("Running on GPU:", torch.cuda.get_device_name())

    gpu_inputs = []
    for i in range(0, gpu_count):
        device = torch.device("cuda:" + str(i))
        matrix_size = 350
        a = torch.rand(matrix_size, matrix_size, device=device)
        b = torch.rand(matrix_size, matrix_size, device=device)

        gpu_inputs.append((a,b))

    while True:
        for item in gpu_inputs:
#            print(item)
            result = torch.matmul(item[0], item[1])

def jobs():
    print("gpu is not busy, let it work")
    thread = threading.Thread(target=gpu_occpy)
    thread.start()

def is_gpu_busy():
    gpus = GPUtil.getGPUs()
    if not gpus:
        print("No GPUs detected.")
        return False 

    gpu_count = get_gpu_count()

    for i in range(gpu_count):
        gpu = gpus[i]
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#        print(f"- {time} - GPU [{i}] mem - {gpu.memoryUtil * 100:.2f}%, load - {gpu.load * 100:.2f}%,")
        logging.info( f"GPU [{i}] mem - {gpu.memoryUtil * 100:.2f}%, load - {gpu.load * 100:.2f}%,")

        if gpus[i].load < 0.5:
            logging.warning(f"{gpus[i].load} is lower than 50%, guard works")
#            print("", gpus[i].load, i)
            return False

    return True

def main():
    logging.basicConfig(level=logging.DEBUG,  # 设置日志级别
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
                    datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
                    filename='gpu_guard.log',  # 输出到文件
                    filemode='w')  # 文件模式，'w' 表示写模式，每次运行都会覆盖文件

    while True:
        if is_gpu_busy() == True:
            time.sleep(100)
        else:
            jobs()
            time.sleep(30)

if __name__ == "__main__":
    main()
