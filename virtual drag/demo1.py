"""
演示一个简单的虚拟拖拽
步骤：
1、opencv 读取视频流
2、在视频图像上画一个方块
3、通过mediapipe库获取手指关节坐标
4、判断手指是否在方块上
"""

#导入opencv的包
import cv2
import numpy as np
# 导入mediapipe：https://google.github.io/mediapipe/solutions/hands
import mediapipe as mp
import math

# mediapipe 相关参数
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

#获取摄像头视频流
cap = cv2.VideoCapture(0)

#获取画面宽度和高度
width1=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height1=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 方块的相关参数
x=100
y=100
width = 100
square_color=(255,0,0)

L1=0
L2=0
on_square=False

while True:
    
    # 读取每一帧
    ret, frame = cap.read()

    # 对图像进行处理
    frame = cv2.flip(frame,1)
    
    # mediapipe处理
    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 识别
    results = hands.process(frame)

    # 判断是否出现双手
    if results.multi_hand_landmarks:
        
    # 解析遍历每一双手
        for hand_landmarks in results.multi_hand_landmarks:
            
            #绘制21个关键点（对其中一双手进行处理）
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
            # 遍历每一个关键点
            # 保存21个x，y坐标
            x_list=[]
            y_list=[]
            for landmark in hand_landmarks.landmark:
                #添加x和y坐标
                x_list.append(landmark.x)
                y_list.append(landmark.y)

            # 获取食指指尖
            index_finger_x = int(x_list[8]*width1)
            index_finger_y = int(y_list[8]*height1)

            # 获取中指指尖
            middle_finger_x = int(x_list[12]*width1)
            middle_finger_y = int(y_list[12]*height1)

            # 计算食指指尖和中指指尖的距离 math的一个函数，用来计算两个点之间的距离（勾股定理）
            finger_len = math.hypot((middle_finger_x-index_finger_x),(middle_finger_y-index_finger_y))

            # # 画一个圆来验证
            # cv2.circle(frame,(index_finger_x,index_finger_y),20,(255,0,0),-1)


            #如果距离小于30，算激活
            if finger_len<30:
            # 判断食指指尖是否在方块上
                if index_finger_x > x and index_finger_x < x + width and index_finger_y > y and index_finger_y < y + width:
                    if on_square == False: # 仅当手指刚进入方块时触发  比较运算符，所以使用==
                        #print('在方块上')
                        L1=abs(index_finger_x-x)
                        L2=abs(index_finger_y-y)
                        on_square=True
                        square_color=(255,0,255)
                else:
                    #print('不在方块上')
                    pass
            else:# 取消激活
                on_square=False
                square_color=(255,0,0)
            
            if on_square: #如果食指在方块上，就实现我们的移动
                x=index_finger_x-L1
                y=index_finger_y-L2

    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # 画一个方块
    # cv2.rectangle(frame,(x,y),(x+width,y+width),(255,0,0),-1)

    # 画一个半透明的方块
    overlay = frame.copy()
    cv2.rectangle(frame,(x,y),(x+width,y+width),square_color,-1)
    frame = cv2.addWeighted(overlay,0.5,frame,0.5,0)

    # 显示
    cv2.imshow('video drag',frame)

    # 退出条件
    if cv2.waitKey(10) & 0xFF == 27:
        break

cap.release()
cv2.destoryAllWindows()
