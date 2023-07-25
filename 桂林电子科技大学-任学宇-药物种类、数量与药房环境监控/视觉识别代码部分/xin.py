import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(0) #需要更改调出摄像头的数字0，1
#初始化窗口
color_search = np.zeros((200, 200, 3), np.uint8)
color_selected = np.zeros((200, 200, 3), np.uint8)

hue = 0
font = cv2.FONT_HERSHEY_SIMPLEX
lower_red = np.array([0, 150, 150])
higher_red = np.array([10, 255, 255])
lower_green = np.array([35, 110, 106])  # 绿色阈值下界
higher_green = np.array([77, 255, 255])  # 绿色阈值上界
lower_black = np.array([0, 0, 0])
higher_black = np.array([25, 35, 46])
cap = cv2.VideoCapture(0)  # 打开电脑内置摄像头,需要更改调出摄像头的数字0，1
#颜色的选择采集
def select_color(event, x, y, flags, param):
    global hue  #变为全局变量

    B = frame[y, x][0]
    G = frame[y, x][1]
    R = frame[y, x][2]
    color_search[:] = (B, G, R)

    if event == cv2.EVENT_LBUTTONDOWN:
        color_selected[:] = (B, G, R)
        hue = hsv[y, x][0]

#采集当前种类药片的数目
def search_contours(mask):
    contours_count = 0
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if 200 < area < 10000:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            contours_count += 1

            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            cv2.circle(frame, (cX, cY), 3, (255, 255, 255), -1)
            cv2.putText(frame, f"{contours_count}", (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255),
                        2)#在图像上标出序号

    return contours_count


def nothing(x):
    pass

#鼠标进行颜色的选择采集
cv2.namedWindow('image')
cv2.setMouseCallback('image', select_color)

cv2.namedWindow('Trackbars')
cv2.resizeWindow('Trackbars', 400, 80)#设置窗口的长和宽
#添加一个滑动条,用于调节颜色浮动范围
cv2.createTrackbar('Lower-Hue', 'Trackbars', 14, 179, nothing)
cv2.createTrackbar('Upper-Hue', 'Trackbars', 18, 179, nothing)

while True:

    _, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)#截取帧
#将浮动条放入窗口
    diff_lower_hue = cv2.getTrackbarPos('Lower-Hue', 'Trackbars')
    diff_upper_hue = cv2.getTrackbarPos('Upper-Hue', 'Trackbars')

    lower_hue = 0 if hue - diff_lower_hue < 0 else hue - diff_lower_hue
    upper_hue = hue + diff_upper_hue if hue + diff_upper_hue < 179 else 179

    lower_hsv = np.array([lower_hue, 50, 20])
    upper_hsv = np.array([upper_hue, 255, 255])

    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

    count = search_contours(mask)

    cv2.putText(frame, f'yaopian-count: {count}', (200, 40), font, 1, (60, 100, 230), 1, cv2.LINE_AA)
    if 0 < count < 3:#数量不足时报警
           cv2.putText(frame, f'count-low', (20, 350), font, 1, (60, 20, 230), 1, cv2.LINE_AA)
  # cv2.imshow('mask', mask)
    cv2.imshow('image', frame)#实时图像
   # cv2.imshow('color_search', color_search)
   # cv2.imshow('color_selected', color_selected)#选到的颜色
    ret, frame = cap.read()  # 读取一帧
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(img_hsv, lower_red, higher_red)  # 过滤出红色部分，获得红色的掩膜,去掉背景
    mask_red = cv2.medianBlur(mask_red, 7)  # 中值滤波
    mask_green = cv2.inRange(img_hsv, lower_green, higher_green)  # 获得绿色部分掩膜
    mask_green = cv2.medianBlur(mask_green, 7)
    mask_black = cv2.inRange(img_hsv, lower_black, higher_black)
    mask_black = cv2.medianBlur(mask_black, 7)


    cnts1, hierarchy1 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
    cnts2, hierarchy2 = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts3, hierarchy3 = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in cnts1:
        (x, y, w, h) = cv2.boundingRect(cnt)  # 该函数返回矩阵四个点
        cv2.rectangle(frame, (x, y - 20), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的药片框起来
        cv2.putText(frame, 'red', (x, y - 20), font, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f'yaopian cuowu', (20, 470), font, 1, (60, 20, 230), 1, cv2.LINE_AA)#药片的读取错误
    for cnt in cnts2:
        (x, y, w, h) = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
        cv2.putText(frame, 'black', (x, y - 1), font, 0.7, (0, 0, 0), 2)
        cv2.putText(frame, f'yaopian cuowu', (20,360), font, 1, (60, 20, 230), 1, cv2.LINE_AA)
    for cnt in cnts3:
        (x, y, w, h) = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y - 50), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, 'green', (x, y - 50), font, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f'yaopian cuowu', (20, 240), font, 1, (60, 20, 230), 1, cv2.LINE_AA)
    cv2.imshow('frame', frame)
    k = cv2.waitKey(20) & 0xFF  #判断按键

    if k == 27:
        break
    if cv2.waitKey(1) & 0xFF == 27:
        break
