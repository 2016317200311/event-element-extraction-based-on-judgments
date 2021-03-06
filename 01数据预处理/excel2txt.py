# -*- coding: utf-8 -*-
# 从excel中导出txt格式的案件信息,分别为【辩护人意见】、【审理查明】、【法院意见】和【判决结果】

import xlrd
import re
import os
from data_preprocess import preprocess

# 路径设置
excel_file = "./所有案件.xlsx"  # excel文件路径
txt_folder = "./txt_files"  # 导出的txt文件路径
argument_path = os.path.join(txt_folder, "argument.txt")  # 辩护人意见
truth_path = os.path.join(txt_folder, "truth.txt")  # 审理查明
court_opinion_path = os.path.join(txt_folder, "court_opinion.txt")  # 法院意见
sentence_path = os.path.join(txt_folder, "sentence.txt")  # 判决结果
all_cases_path = os.path.join(txt_folder, "cases.txt")  # 完整案件

# 读取excel
wb = xlrd.open_workbook(excel_file)
sheet0 = wb.sheets()[0]  # 获取第一个工作表
# 读取指定列
records = sheet0.col_values(21)[1:]  # 第21列代表庭审过程，包含【辩护人意见】和【审理查明】两部分
court_opinion = sheet0.col_values(27)[1:]  # 第27列代表法院意见
sentence = sheet0.col_values(29)[1:]  # 第29列代表判决结果
# 提取辩护人意见
re_argument = re.compile(
    r"辩护人.{0,6}(提出|认为|所提|辩解|要求|建议|辩护|辩称).*?。")
# 提取审理查明
re_truth = re.compile(
    r"(公诉机关指控|检察院.{0,5}指控|经.*?查明).*?(上述事实|以上事实|上述案件事实|公诉机关认为|公诉机关认定|为证实|该院认为|检察院认为|被告人.*?异议)")
re_truth_1 = re.compile(r"(公诉机关指控|检察院.{0,5}指控|经.*?查明).*")
# 提取判决结果
re_sentence = re.compile(r"判决如下.*?(被告人.*(年|月|处罚))")

# 写入文本文件
f1 = open(argument_path, "w", encoding='utf-8')  # 辩护人意见
f2 = open(truth_path, 'w', encoding='utf-8')  # 审理查明
f3 = open(court_opinion_path, 'w', encoding='utf-8')  # 法院意见
f4 = open(sentence_path, 'w', encoding='utf-8')  # 判决结果
f5 = open(all_cases_path, "w", encoding="utf-8")  # 完整的案件

for elem1, elem2, elem3 in list(zip(records, court_opinion, sentence)):
    # 预处理
    elem1 = preprocess(elem1)
    elem2 = preprocess(elem2)
    elem3 = preprocess(elem3)

    # 写入判决结果
    # 若判决结果为空，则跳过该案件
    search_sentence = re_sentence.search(elem3)
    if search_sentence:
        f4.write(search_sentence.group(1) + '\n')
    else:
        # f4.write("None\n")
        continue

    # 写入辩护人意见
    search_argument_1 = re_argument.search(elem1)
    search_argument_2 = re_argument.search(elem2)
    if search_argument_1:
        f1.write(search_argument_1.group() + '\n')
    elif search_argument_2:
        f1.write(search_argument_2.group() + '\n')
    else:
        f1.write("None\n")

    # 写入审理查明
    search_truth = re_truth.search(elem1)
    if search_truth:
        f2.write(search_truth.group() + '\n')
    else:
        search_truth_1 = re_truth_1.search(elem1)
        if search_truth_1:
            f2.write(search_truth_1.group() + '\n')
        else:
            f2.write("None\n")

    # 写入法院意见
    if elem2 == "":
        f3.write("None\n")
    else:
        f3.write(elem2 + '\n')

    # 写入完整案件
    f5.write(elem1 + elem2 + elem3 + "\n")

f1.close()
f2.close()
f3.close()
f4.close()
f5.close()
