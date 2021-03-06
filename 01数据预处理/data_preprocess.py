# -*- coding:UTF-8 -*-
# 数据预处理

import re

# 标点符号和特殊字符
punctuation = '''，、:；（）?ＸX×xa"“”,<《》.\t\n'''
# 冗余词
re_redundant_1 = re.compile(
    r'(缓刑考验|刑期).*?(止|计算)|判决执行.*?止|(依照|依据).*?规定|(扣押)?作案工具.*?没收|《.*?》|如不服.*份|第.*?条|第.*?款|的|了|其|另|已|且|审判.*?月')
re_redundant_2 = re.compile(r'的|了|已|且|(刑期.*?算.*月)')


def preprocess(line):
    """数据预处理"""
    line1 = re.sub(r"（.*?）", "", line)  # 去除括号内注释
    line2 = re.sub("[%s]+" % punctuation, "", line1)  # 去除标点、特殊字符
    line3 = re_redundant_1.sub("", line2)  # 去除冗余词
    return line3
