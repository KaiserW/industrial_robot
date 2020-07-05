from utils import ImageTaker, CoordTransformer

import socket

# 建立Socket服务器
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host_ip = '192.168.125.2'
port = 8080

s.bind((host_ip, port))
s.listen()

print("Server establised, listening...")

# 监听ABB机器人（客户端），每次返回一个坐标
i = 0
detect_bytes = None

while True:
    conn, addr = s.accept()
    print("Connectted to Client: {}".format(addr))
    
    while True:

        data = conn.recv(1024)
        print("接收请求代码", data)

        # 相机就位，开始拍照，并检测目标位置
        if data == b'01':
            print("采集图像并检测")
            image, img_filename = ImageTaker()
            detect_bytes = CoordTransformer(image, img_filename)
            #conn.send(b"Detection complete")

        # 请求下一个目标位置
        elif data == b'02':
            if detect_bytes is None:
                print("还未采集图像")
                #conn.send(b"Image note taken")
        
            else:
                if i < len(detect_bytes):
                    print("Sending Coord: {}, {}".format(i, detect_bytes[i]))
                    conn.send(detect_bytes[i])
                    i += 1

                else:
                    print("已发送所有目标位置")
                    #conn.send(b"All Coords sent")

                    
        else:
            print("本轮请求结束")
            #conn.send(b"Query complete")
            i = 0
            break
    
    conn.close()

