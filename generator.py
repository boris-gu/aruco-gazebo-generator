#!/usr/bin/env python3

import argparse
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

# ПАРСЕР
parser = argparse.ArgumentParser(
    description='marker model generator for Gazebo simulator')
parser.add_argument('num', type=int, metavar='NUMBER',
                    help='numbers of markers')
parser.add_argument('size_xy', type=float, metavar='SIZE',
                    help='marker size in meters')
parser.add_argument('size_z', type=float, metavar='THICKNESS',
                    help='thickness of marker model in meters')
parser.add_argument('-d', '--dict', default='ARUCO_4X4_1000', metavar='DICT',
                    choices=MARKER_DICTS, help='dictionary')
parser.add_argument('--no-static', dest='static', action='store_false',
                    help='if set, the model is simulated in the dynamics engine')
parser.add_argument('--no-collision', dest='collision', action='store_false',
                    help='if set, the model has no collision mesh')
args = parser.parse_args()
parser.set_defaults(static=True)
parser.set_defaults(collision=True)


# УДАЛЯЕМ ПРЕДЫДУЩУЮ ГЕНЕРАЦИЮ
str_dict_out = args.dict.replace('ARUCO', 'ArUco')
str_dict_out = str_dict_out.replace('APRILTAG', 'AprilTag')
rmtree('./models', True)
""" for i in range(args.num):
    makedirs(f'./models/{str_dict_out}_{i}/collada') """


# СОЗДАЕМ ТЕКСТУРУ
marker_dict = cv2.aruco.Dictionary_get(MARKER_DICTS.get(args.dict))  # Словарь
try:
    for i in range(args.num):
        img = np.zeros((504, 504), dtype="uint8")  # min, 504 % 6,7,7,9 == 0
        cv2.aruco.drawMarker(marker_dict, i, 504, img)
        img = np.pad(img, 42, constant_values=255)  # рамка == marker/6/2
        cv2.putText(img, f'{str_dict_out}_{i}', (10, 20),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)
        makedirs(f'./models/{str_dict_out}_{i}/collada')
        cv2.imwrite(f'./models/{str_dict_out}_{i}/collada/marker.png', img)
except:
    pass


# СОЗДАЕМ ФАЙЛ .dae
# добавляем размер для рамки и /2 для центрирования
point_xy = (args.size_xy + args.size_xy/6)/2
# формируем строку с координатами вершин
str_mesh = f'{-point_xy} {point_xy} {args.size_z}'
str_mesh += f' {-point_xy} {point_xy} 0'
str_mesh += f' {-point_xy} {-point_xy} 0'
str_mesh += f' {-point_xy} {-point_xy} {args.size_z}'
str_mesh += f' {point_xy} {-point_xy} 0'
str_mesh += f' {point_xy} {-point_xy} {args.size_z}'
str_mesh += f' {point_xy} {point_xy} 0'
str_mesh += f' {point_xy} {point_xy} {args.size_z}'

with open('./template/marker.dae', 'r') as template:
    text = template.read()
    template.close
text = text.replace('CHANGE MESH', str_mesh)

try:
    for i in range(args.num):
        with open(f'./models/{str_dict_out}_{i}/collada/marker.dae', 'w') as out_dae:
            out_dae.write(text)
            out_dae.close()
except:
    pass

# СОЗДАЕМ ФАЙЛ .sdf
str_static = str(args.static).lower()
size_collision_xy = args.size_xy + args.size_xy/6
str_z_collision = str(args.size_z/2)
str_collision = f'{size_collision_xy} {size_collision_xy} {args.size_z}'

with open('./template/model.sdf', 'r') as template:
    text = template.read()
    template.close
text = text.replace('CHANGE STATIC', str_static)
if args.collision:
    text = text.replace('CHANGE Z COLLISION', str_z_collision)
    text = text.replace('CHANGE COLLISION', str_collision)
else:
    remove_col_start = text.find('\n      <collision name="collision">')
    remove_col_stop = text.find('\n      <visual name="visual">')
    text = text[:remove_col_start] + text[remove_col_stop:]
try:
    for i in range(args.num):
        str_name = f'{str_dict_out} No.{i}'.replace('_', ' ')
        str_visual = fr'model://{str_dict_out}_{i}/collada/marker.dae'
        text_loop = text.replace('CHANGE NAME', str_name)
        text_loop = text_loop.replace('CHANGE VISUAL', str_visual)
        with open(f'./models/{str_dict_out}_{i}/model.sdf', 'w') as out_sdf:
            out_sdf.write(text_loop)
            out_sdf.close()
except:
    pass


# СОЗДАЕМ ФАЙЛ .config
with open('./template/model.config', 'r') as template:
    text = template.read()
    template.close

try:
    for i in range(args.num):
        str_name = f'{str_dict_out} No.{i}'.replace('_', ' ')
        text_loop = text.replace('CHANGE NAME', str_name)
        with open(f'./models/{str_dict_out}_{i}/model.config', 'w') as out_config:
            out_config.write(text_loop)
            out_config.close()
except:
    pass

print('OK')
