# -*- coding: UTF-8 -*-
import os

# 验证码中的字符设置
# string.digits + string.ascii_uppercase
NUMBER = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# 验证码相关设置
ALL_CHAR_SET = NUMBER + ALPHABET
ALL_CHAR_SET_LEN = len(ALL_CHAR_SET)
MAX_CAPTCHA = 4

# 验证码尺寸设置
IMAGE_HEIGHT = 100
IMAGE_WIDTH = 180

# 验证码保存路径
PREDICT_DATASET_PATH = "captcha" + os.path.sep + "img" + os.path.sep

# 爬虫登录账号设置
USER_ID = "6168218d884484b96b11adb8"

# 断点ID设置
BREAK_POINT = '6167f1d5227d6c6a3647abe6'

# 代理ID设置
PROXY_LIST = '616c1efcb5b6d832ad606b3d'