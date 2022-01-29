#!/usr/bin/env python3

from shutil import rmtree
from os import makedirs
import cv2
import numpy as np

MARKER_DICTS = {
    'ARUCO_4X4_50': cv2.aruco.DICT_4X4_50,
    'ARUCO_4X4_100': cv2.aruco.DICT_4X4_100,
    'ARUCO_4X4_250': cv2.aruco.DICT_4X4_250,
    'ARUCO_4X4_1000': cv2.aruco.DICT_4X4_1000,
    'ARUCO_5X5_50': cv2.aruco.DICT_5X5_50,
    'ARUCO_5X5_100': cv2.aruco.DICT_5X5_100,
    'ARUCO_5X5_250': cv2.aruco.DICT_5X5_250,
    'ARUCO_5X5_1000': cv2.aruco.DICT_5X5_1000,
    'ARUCO_6X6_50': cv2.aruco.DICT_6X6_50,
    'ARUCO_6X6_100': cv2.aruco.DICT_6X6_100,
    'ARUCO_6X6_250': cv2.aruco.DICT_6X6_250,
    'ARUCO_6X6_1000': cv2.aruco.DICT_6X6_1000,
    'ARUCO_7X7_50': cv2.aruco.DICT_7X7_50,
    'ARUCO_7X7_100': cv2.aruco.DICT_7X7_100,
    'ARUCO_7X7_250': cv2.aruco.DICT_7X7_250,
    'ARUCO_7X7_1000': cv2.aruco.DICT_7X7_1000,
    'ARUCO_ORIGINAL': cv2.aruco.DICT_ARUCO_ORIGINAL,
    'APRILTAG_16h5': cv2.aruco.DICT_APRILTAG_16h5,
    'APRILTAG_25h9': cv2.aruco.DICT_APRILTAG_25h9,
    'APRILTAG_36h10': cv2.aruco.DICT_APRILTAG_36h10,
    'APRILTAG_36h11': cv2.aruco.DICT_APRILTAG_36h11,
}


# ПАРАМЕТРЫ ПО УМОЛЧАНИЮ
num = [0, 1, 2, 3, 4]
size_xy = 0.006
size_z = 0.005
str_dict = 'ARUCO_5X5_1000'
static = True
collision = True


# СОЗДАЕМ ПУТЬ
str_dict_out = str_dict.replace('ARUCO', 'ArUco')
str_dict_out = str_dict_out.replace('APRILTAG', 'AprilTag')
rmtree('./models', True)
for i in num:
    makedirs(f'./models/{str_dict_out}_{i}/collada')


# СОЗДАЕМ ТЕКСТУРУ
marker_dict = cv2.aruco.Dictionary_get(MARKER_DICTS.get(str_dict))  # Словарь
for i in num:
    img = np.zeros((504, 504), dtype="uint8")  # 504 - min, 504 % 6,7,7,9 == 0
    cv2.aruco.drawMarker(marker_dict, i, 504, img)
    img = np.pad(img, 42, constant_values=255)  # рамка == marker/6/2
    cv2.putText(img, f'{str_dict_out}_{i}', (10, 20),
                cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.imwrite(f'./models/{str_dict_out}_{i}/collada/marker.png', img)


# СОЗДАЕМ ФАЙЛ .dae
# добавляем размер для рамки и /2 для центрирования
point_xy = (size_xy + size_xy/6)/2
# формируем строку с координатами вершин
str_mesh = f'{-point_xy} {point_xy} {size_z}'
str_mesh += f' {-point_xy} {point_xy} 0'
str_mesh += f' {-point_xy} {-point_xy} 0'
str_mesh += f' {-point_xy} {-point_xy} {size_z}'
str_mesh += f' {point_xy} {-point_xy} 0'
str_mesh += f' {point_xy} {-point_xy} {size_z}'
str_mesh += f' {point_xy} {point_xy} 0'
str_mesh += f' {point_xy} {point_xy} {size_z}'

with open('./template/marker.dae', 'r') as template:
    text = template.read()
    template.close
text = text.replace('CHANGE MESH', str_mesh)

for i in num:
    with open(f'./models/{str_dict_out}_{i}/collada/marker.dae', 'w') as out_dae:
        out_dae.write(text)
        out_dae.close()

# СОЗДАЕМ ФАЙЛ .sdf
str_static = str(static).lower()
size_collision_xy = size_xy + size_xy/6
str_z_collision = str(size_z/2)
str_collision = f'{size_collision_xy} {size_collision_xy} {size_z}'

with open('./template/model.sdf', 'r') as template:
    text = template.read()
    template.close
text = text.replace('CHANGE STATIC', str_static)
if collision:
    text = text.replace('CHANGE Z COLLISION', str_z_collision)
    text = text.replace('CHANGE COLLISION', str_collision)
else:
    remove_col_start = text.find('\n      <collision name="collision">')
    remove_col_stop = text.find('\n      <visual name="visual">')
    text = text[:remove_col_start] + text[remove_col_stop:]

for i in num:
    str_name = f'{str_dict_out} No.{i}'.replace('_', ' ')
    str_visual = fr'model://{str_dict_out}_{i}/collada/marker.dae'
    text_loop = text.replace('CHANGE NAME', str_name)
    text_loop = text_loop.replace('CHANGE VISUAL', str_visual)
    with open(f'./models/{str_dict_out}_{i}/model.sdf', 'w') as out_sdf:
        out_sdf.write(text_loop)
        out_sdf.close()


# СОЗДАЕМ ФАЙЛ .config
with open('./template/model.config', 'r') as template:
    text = template.read()
    template.close

for i in num:
    str_name = f'{str_dict_out} No.{i}'.replace('_', ' ')
    text_loop = text.replace('CHANGE NAME', str_name)
    with open(f'./models/{str_dict_out}_{i}/model.config', 'w') as out_config:
        out_config.write(text_loop)
        out_config.close()

print('OK')
