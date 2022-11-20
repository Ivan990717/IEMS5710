import os,re,time,json,socket
import datetime,time
from getpass import getpass
from server.config.setting import base_dir
str = 'ca-public-key-44.pem'


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

class Verify(object):
    def __init__(self,conn):
        self.conn = conn

        self.id = None
        self.CA_private_key = None




    @property
    def ca_private_key(self):
        self.CA_private_key = pki_helper.generate_private_key("ca-private-key.pem","regina")
        print("CA_private_key",self.CA_private_key)
        return self.CA_private_key

    def CSR_request(self,conn,ID):
        if not self.CA_private_key:
            # print("没有根")
            self.CA_private_key = self.ca_private_key
            # time_number = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        csr_file_name = "server-csr_{}.pem".format(ID)
        client_csr = pki_helper.generate_csr(self.CA_private_key,csr_file_name,
                                            country = "CN",
                                            state = "HongKOng",
                                            locality = "HongKong",
                                            org = "Cuhk",
                                            hostname = "CUHK.com",
        )
        # print(client_csr)
        csr_file = open("server-csr_{}.pem".format(ID), "rb")
        csr = x509.load_pem_x509_csr(csr_file.read(), default_backend())

        pki_helper.generate_public_key(self.CA_private_key,"ca-public-key-{}.pem".format(ID),country = "CN",
                                                state = "HongKOng",
                                                locality = "HongKong",
                                                org = "Cuhk",
                                                hostname = "CUHK.com",)
        ca_public_key_file = open("ca-public-key-{}.pem".format(ID), "rb")
        public_key = x509.load_pem_x509_certificate(
            ca_public_key_file.read(),
            default_backend())
        # print(public_key)

        ca_private_key_file = open("ca-private-key.pem", "rb")
        private_key = serialization.load_pem_private_key(
            ca_private_key_file.read(),
            getpass().encode("utf-8"),
            default_backend(), )
        sign_file_name = "server-public-key-{}.pem".format(ID)
        pki_helper.sign_csr(csr,public_key,private_key,sign_file_name)
        req.send_data(conn,"student {} sign finished".format(ID))
        # return_file = open(sign_file_name,'rb')
        req.send_file(conn,os.path.join(base_dir,"ca-public-key-{}.pem".format(ID)))
        return True


    def enter_Stu(self,conn):
        req.send_data(conn,"please input your student_id")
        ID = req.recv_data(conn).decode('utf8')  # id

        logging.info("student_id: {}".format(ID))
        req.send_data(conn,"ID{} logins successfully".format(ID))
        return ID



        return True



    def _execute(self):
        conn = self.conn
        cmd = req.recv_data(conn).decode('utf8')
        while True:

            if cmd.upper() == "Q":
                logging.info(("client exit"))
                return False
            if cmd.upper() == "1":
                ID = self.enter_Stu(conn)
                logging.info('*' * 20 + "STEP 2 SEND CERT" + '*' * 20)
                time.sleep(0.2)
                file_name = self.CSR_request(conn,ID)



