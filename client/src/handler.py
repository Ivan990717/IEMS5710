import logging
import re
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
# 由于日志基本配置中级别设置为DEBUG，所以一下打印信息将会全部显示在控制台上
import re,socket,time,os,json

from client.config.setting import *
from client.utils.req import *

class Handler(object):
    def __init__(self):
        self.host = ip_address
        self.CUHKport = CUHKport
        self.BBport = BBport
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = []
        self.cert = {}
        self.session_key = {}


    def decrypt_session_key(self,conn,id):
        logging.info('*' * 20 + "STEP 5  DECRYPT SESSION_KEY" + '*' * 20)
        time.sleep(0.2)
        cipher_key = recv_data(conn).decode("utf8")
        from RC4 import RC4Decrypt

        key = RC4Decrypt(cipher_key,id*2)
        return key



    def MAC(self,conn,session_key,message):
        import hashlib
        import hmac
        # session_key = bytes(session_key,encoding = 'utf8')
        mac = hmac.new(session_key.encode('utf8'),message.encode('utf8'),hashlib.sha1)
        return mac.hexdigest()


    def say_hello(self,conn,i,input_id):
        askNo = recv_data(conn).decode('utf8')  #please input your student_id
        ID = input_id[i]
        send_data(conn, ID)
        msg = recv_data(conn).decode('utf8') # ID{} logins successfully
        print(msg)

        sign_finish = recv_data(conn).decode('utf8') # student {} sign finished
        print(sign_finish)
        self.id.append(ID)
        recv_save_file(conn,os.path.join(base_dir,"ca-public-key-{}.pem".format(ID)))
        fileline = ''
        with open(os.path.join(base_dir,"ca-public-key-{}.pem".format(ID)),'r') as obj:
            fileline += obj.read()
        self.cert[ID] = fileline
        # print(fileline)

    def run(self,input_id):
        while True:

            choice = input("please choose:\n"
                           "1: CUHK\n"
                           "2: BlackBoard\n"
                           "Q: exit\n")
            if not choice:
                logging.warning("Noting input is forbidden")
                continue

            if choice == "2" and self.cert == {}:
                logging.error("please enter your CUHK")
                continue

            if choice == '2' and self.cert != {}:
                logging.info('*' * 20 + "STEP 3 REQUEST TO BLACKBOARD" + '*' * 20)
                # print(self.cert)
                print(choice)
                self.connect.connect((ip_address,BBport))
                send_data(self.connect, choice)
                for i in input_id:

                    send_data(self.connect,i)
                    send_data(self.connect,self.cert[i])
                    cert_ans = recv_data(self.connect).decode("utf8")
                    logging.info(cert_ans)
                    time.sleep(0.2)
                    key = self.decrypt_session_key(self.connect,i)
                    msg = "This is submission from SID{}".format(i)*10
                    text_mac = self.MAC(self.connect,key,i)
                    text = '{}_{}'.format(msg,text_mac)
                    logging.info('*' * 20 + "STEP 6 SEND MSG_MAC" + '*' * 20)
                    time.sleep(0.2)
                    send_data(self.connect,text)
                    ans = recv_data(self.connect).decode('utf8')
                    logging.info(ans)
                    time.sleep(0.2)


            if choice == "1":
                try:
                #print(choice)
                    self.conn.connect((ip_address,CUHKport))
                except :
                    continue
                send_data(self.conn, choice)
                logging.info('*' * 20 + "STEP 2 DISPLAY SIGN FINISHED" + '*' * 20)
                for i in range(3):
                    self.say_hello(self.conn,i,input_id)



            if choice.upper() == "Q":
                logging.info("退出")
                send_data(self.conn, "q")
                break






