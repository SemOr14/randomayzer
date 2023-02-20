import datetime
import mysql.connector
from getpass import getpass
from mysql.connector import connect, Error
import cv2
import numpy as np
from collections import deque
 
today = datetime.datetime.today()       #Время
min_threshold = 10                      # эти значения используются для фильтрации нашего детектора.
max_threshold = 200                     # они могут быть изменены в зависимости от расстояния до камеры, угла наклона камеры, ...
min_area = 100                          # ... фокус, яркость и т.д.
min_circularity = 0.3
min_inertia_ratio = 0.5
 
cap = cv2.VideoCapture(0)               # '0' - это идентификатор веб-камеры. обычно это 0/1/2/3 / и т.д. "cap" - это видеообъект.
cap.set(15, -4)                         # '15' ссылается на экспозицию видео. '-4' устанавливает ее.
 
temp=0
counter = 0                             # скрипт будет использовать счетчик для обработки кадров в секунду.
readings = deque([0, 0], maxlen=10)     # списки используются для отслеживания количества пунктов.
display = deque([0, 0], maxlen=10)
 
try:
    with connect(
        host="0.0.0.0",
        user=input("Имя пользователя: "),
        password=getpass("Пароль: "),
        database="randomizer",
    ) as connection:
        print(connection)
except Error as e:
    print(e)

while True:
    ret, im = cap.read()                                    # 'im' будет кадром из видео.
 
    params = cv2.SimpleBlobDetector_Params()                # объявление параметры фильтра.
    params.filterByArea = True
    params.filterByCircularity = True
    params.filterByInertia = True
    params.minThreshold = min_threshold
    params.maxThreshold = max_threshold
    params.minArea = min_area
    params.minCircularity = min_circularity
    params.minInertiaRatio = min_inertia_ratio
 
    detector = cv2.SimpleBlobDetector_create(params)        # создайте объект детектора больших двоичных объектов.

    keypoints = detector.detect(im)                         # ключевые точки - это список, содержащий обнаруженные двоичные объекты.
 
    # здесь мы рисуем ключевые точки на рамке.
    im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 
    cv2.imshow("Dice Reader", im_with_keypoints)            # отображает рамку с добавленными ключевыми точками.
 
    if counter % 10 == 0:                                   # вводите этот блок каждые 10 кадров.
        reading = len(keypoints)                            # 'reading' подсчитывает количество ключевых точек (pips).
        readings.append(reading)                            # запишите показания из этого кадра.
 
        if readings[-1] == readings[-2] == readings[-3]:    # если последние 3 показания совпадают...
            display.append(readings[-1])                    # ... тогда у нас есть достоверное чтение.
 
        # если последнее допустимое значение изменилось, и оно отличается от нуля, то выведите его.
        if display[-1] != display[-2] and display[-1] != 0:
            msg = f"{display[-1]}\n****"
            print(msg)
            a=today.strftime("%d/%m/%Y") 
            b=today.strftime("%H.%M.%S")
            results = """
            INSERT INTO results (№_генерации, Дата, Время, Результат)
            VALUES
            (temp, a, b, msg),
            """
            temp+= 1
            counter += 1
            with connection.cursor() as cursor:
              cursor.execute(results)
              connection.commit()
 
    if cv2.waitKey(1) & 0xff == 27:                          # press [Esc] to exit.
        break
 
cv2.destroyAllWindows()

