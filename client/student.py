'''
designed by ivanlee
'''
import time

from client.src.handler import Handler
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig
# function configures the output format and method of the log



if __name__ == "__main__":
    stu = []
    logging.info('*'*20 + "STEP 0" + '*'*20)
    time.sleep(0.2)
    for i in range(3):

        stu.append(input("please input the id: "))
    logging.info('*' * 20 + "STEP 1" + '*' * 20)
    handler = Handler()
    handler.run(stu)

