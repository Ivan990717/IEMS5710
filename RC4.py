
import base64


def RC4(text, key):
    lk = len(key)
    S = [0] * 256  
    T = ''  
    for i in range(256):
        S[i] = i  
        T += key[i % lk]  
    # 根据密钥打乱S盒
    j = 0
    for i in range(256):
        j = (j+S[i]+ord(T[i])) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    ans = ""
    for x in text:
        i = (i+1) % 256
        j = (j+S[i]) % 256
        S[i], S[j] = S[j], S[i]
        t = (S[i]+S[j]) % 256
        k = S[t]
        ans += chr(ord(x) ^ k)
    return ans
# RC4加密: 明文转成base64编码的密文


def RC4Encrypt(message, key):
    return str(base64.b64encode(RC4(message, key).encode('utf-8')), "utf-8")
# RC4解密: base64编码的密文转成明文


def RC4Decrypt(cipher, key):
    return RC4(str(base64.b64decode(cipher), "utf-8"), key)
