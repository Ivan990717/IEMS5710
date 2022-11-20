import os,re,time,json,socket
import datetime,time
from getpass import getpass
from server.config.setting import base_dir


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# from server.db.account import student_info
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
# 由于日志基本配置中级别设置为DEBUG，所以一下打印信息将会全部显示在控制台上
from server.utils import req
from server.config import setting
from server.src import pki_helper
from cryptography import x509
from cryptography.x509.oid import NameOID

class Verifyboard(object):
    def __init__(self,conn):
        self.conn = conn



    def get_certid(self,name):
        id = name[14:-4]

    def blackboard_login(self,conn):
        logging.info('*' * 20 + "STEP 3 CHECK CERTIFICATE" + '*' * 20)
        time.sleep(0.2)
        ## supposed that blackborad server share the same CA files with cuhk server
        cert_line = ''
        id = req.recv_data(conn).decode('utf8')
        id_cert = req.recv_data(conn).decode("utf8")
        with open(os.path.join(base_dir,"ca-public-key-{}.pem".format(id)),'r') as obj:
            cert_line += obj.read()
        # print(cert_line)
        if id_cert == cert_line:
            req.send_data(conn,"{} has been verified".format(id))
            logging.info("{} has been verified".format(id))
            time.sleep(0.2)

        return id


    def generate_session_key(self,conn,id):
        logging.info('*' * 20 + "STEP 4 GENERATE SESSION_KEY" + '*' * 20)
        time.sleep(0.2)
        '''
        the default key is same as the CA root private key:
        regina
        we will use a key to encrypt the regina and then send to client
        encryption method is RC4
        '''

        from RC4 import RC4Encrypt
        cipher_key = RC4Encrypt("regina",id*2)
        # print(cipher_key)
        req.send_data(conn,cipher_key)
        logging.info('session_key has been generated')
        return cipher_key


    def recv_mac_msg(self,session_key="regina",conn = None,id = 0):
        logging.info('*' * 20 + "STEP 6 VERIFY MAC" + '*' * 20)
        time.sleep(0.2)
        mac_msg = req.recv_data(conn).decode('utf8')
        msglist = mac_msg.split('_')
        msg = msglist[0]
        mac = msglist[1]

        import hashlib
        import hmac
        # session_key = bytes(session_key, encoding='utf8')
        mac_verify = hmac.new(session_key.encode('utf8'), str(id).encode('utf8'), hashlib.sha1).hexdigest()

        # print(mac,mac_verify)
        if mac == mac_verify:
            logging.info("student{} message:{}".format(id,msg))
        else:
            logging.error("student{} mac verification failed".format(id))
            return False

        return True

    def execute_(self):
        conn = self.conn
        cmd = req.recv_data(conn).decode('utf8')

        while True:
            if cmd.upper() == "Q":
                logging.info(("client exit"))
                return False

            if cmd.upper() == "2":
                ID = self.blackboard_login(conn)
                session_key = self.generate_session_key(conn, ID)
                mac_ver = self.recv_mac_msg(conn=conn,id = ID)
                if mac_ver:
                    req.send_data(conn,"massage sent!")
                else:
                    req.send_data(conn,"mac verification failed!")



