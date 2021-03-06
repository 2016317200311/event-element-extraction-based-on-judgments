import re


def remove_duplicate_elements(l):
    """
    去除列表中重复元素，同时保持相对顺序不变
    :param l: 可能包含重复元素的列表
    :return: 去除重复元素的新列表
    """
    new_list = []
    for elem in l:
        if elem not in new_list:
            new_list.append(elem)
    return new_list


def find_element(l, *ss):
    """
    查找列表l的元素中是否包含s
    :param l:列表
    :param ss:一个或多个字符串
    """
    for s in ss:
        for element in l:
            if s in element:
                return "1"
    return "0"


def text2num(text):
    '''中文数字转阿拉伯数字,只适用于不超过四位数的情况'''
    # 将text序列连接成字符串
    text = "".join(text)
    digit = {
        '一': 1,
        '二': 2,
        '两': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9}
    num = 0
    if text:
        idx_q, idx_b, idx_s = text.find('千'), text.find('百'), text.find('十')
        if idx_q != -1:
            num += digit[text[idx_q - 1:idx_q]] * 1000
        if idx_b != -1:
            num += digit[text[idx_b - 1:idx_b]] * 100
        if idx_s != -1:
            # “十”前没有数字时默认为“一十”
            num += digit.get(text[idx_s - 1:idx_s], 1) * 10
        if text[-1] in digit:
            num += digit[text[-1]]
    return num


def num_extract(text):
    '''查找语句中的中文数字并转为阿拉伯数字,只适用于个位数的情况，后续修改'''
    # 如果语句中已经含有阿拉伯数字，则直接提取并返回
    num = re.findall(r"\d+", text)
    if num:
        return num[0]
    else:
        chinese = re.findall(r"[一二两三四五六七八九十]", text)
        if chinese:
            return text2num(chinese[0])
        else:
            return 1  # 默认为一


def extract_death_num(content):
    '''提取死亡人数'''
    if content == None:
        return 0
    re_dead = re.compile(r'[1234567890一二两三四五六七八九十]?人死亡')  # 致几人死亡
    search_dead = re.search(re_dead, content)
    if search_dead:
        return num_extract(search_dead.group())
    else:
        re_dead_1 = re.compile(r"致.{0,8}人死亡")  # 处理不指明人数的情况，如“致受害人死亡”
        search_dead_1 = re.search(re_dead_1, content)
        if search_dead_1:
            return 1
        else:
            return 0


def extract_injured_num(content):
    '''提取轻微伤人数、轻伤人数、重伤人数'''
    if content == None:
        return 0, 0, 0
    # 轻微伤人数
    re_slight = re.compile(r'[1234567890一二两三四五六七八九十]?人轻微伤')
    search_slight = re.search(re_slight, content)
    if search_slight:
        num_slight = num_extract(search_slight.group())
    else:
        # 处理不指明人数的情况，如“致受害人轻微伤/致人轻微伤”，下同
        re_slight_1 = re.compile(r"致.{0,8}人轻微伤")
        search_slight_1 = re.search(re_slight_1, content)
        if search_slight_1:
            num_slight = 1
        else:
            num_slight = 0
    # 轻伤人数
    re_minor = re.compile(r'[1234567890一二两三四五六七八九十]?人轻伤')
    search_minor = re.search(re_minor, content)
    if search_minor:
        num_minor = num_extract(search_minor.group())
    else:
        re_minor_1 = re.compile(r"致.{0,8}人轻伤")
        search_minor_1 = re.search(re_minor_1, content)
        if search_minor_1:
            num_minor = 1
        else:
            num_minor = 0
    # 重伤人数
    re_severe = re.compile(r'[1234567890一二两三四五六七八九十]*人重伤')
    search_severe = re.search(re_severe, content)
    if search_severe:
        num_severe = num_extract(search_severe.group())
    else:
        re_severe_1 = re.compile(r"致.{0,8}人重伤")
        search_severe_1 = re.search(re_severe_1, content)
        if search_severe_1:
            num_severe = 1
        else:
            num_severe = 0

    return num_slight, num_minor, num_severe


def sentence_result_number(content):
    '''提取有期徒刑刑期，单位为月份'''
    if content == None:
        return 0
    r1 = re.compile(r'(有期徒刑|拘役)[一二三四五六七八九十又年零两]{1,}(个月|年)')
    r2 = re.search(r1, content[0])
    if r2 is None:
        num = 0
    else:
        text = r2.group()
        r3 = re.compile(u'[一二三四五六七八九十两]{1,}')
        r4 = r3.findall(text)
        if len(r4) > 1:
            num1 = text2num(r4[0])
            num2 = text2num(r4[1])
            num = 12 * num1 + num2
        elif text.find(u"年") != -1:
            num = 12 * text2num(r4)
        else:
            num = text2num(r4)
    return num


def get_event_elements(case_file):
    """
    将案件中属于同一事件要素的词语合并，最终返回完整的事件要素
    :param case_file: 记录单个案件的文本文件
    :return event_elements: 返回一个字典，键为事件要素类型，值为对应的事件要素组成的list
    """
    words = []  # 保存标注为事件要素的词语
    element_types = []  # 保存上述词语对应的事件要素类型

    with open(case_file, "r", encoding='utf-8') as f1:
        rows = []
        # 将文本转换成list，方便后续处理
        for line in f1.readlines():
            rows.append(line.strip("\n").split("\t"))

        for index, row in enumerate(rows):
            if "S" in row[-1]:
                # S出现在最后一个位置，说明这是一个单独的事件要素，将其加入words列表
                words.append(row[0])
                element_types.append(row[-1][-1])

            elif "B" in row[-1]:
                # 处理由多组单词构成的事件要素
                words.append(row[0])
                element_types.append(row[-1][-1])
                j = index + 1
                while "I" in rows[j][-1] or "E" in rows[j][-1]:
                    words[-1] += rows[j][0]
                    j += 1
                    if j == len(rows):
                        break

        # 将事件要素进行分类（将words列表中的元素按照类别分成6类）
        T = []  # 投案
        G = []  # 如实供述
        Z = []  # 自首
        R = []  # 认罪
        P = []  # 赔偿
        Q = []  # 取得谅解

        for i in range(len(element_types)):
            if element_types[i] == "T":
                T.append(words[i])
            elif element_types[i] == "G":
                G.append(words[i])
            elif element_types[i] == "Z":
                Z.append(words[i])
            elif element_types[i] == "R":
                R.append(words[i])
            elif element_types[i] == "P":
                P.append(words[i])
            elif element_types[i] == "Q":
                Q.append(words[i])

        # 整理抽取结果
        event_elements = dict()  # 用字典存储各类事件要素
        event_elements["投案"] = remove_duplicate_elements(T)
        event_elements["如实供述"] = remove_duplicate_elements(G)
        event_elements["自首"] = remove_duplicate_elements(Z)
        event_elements["认罪"] = remove_duplicate_elements(R)
        event_elements["赔偿"] = remove_duplicate_elements(P)
        event_elements["取得谅解"] = remove_duplicate_elements(Q)

        # 打印出完整的事件要素
        # for key, value in event_elements.items():
        #     print(key, value)

        return event_elements


def get_crime_stage(content):
    """
        得到犯罪阶段
    """
    if content == None:
        return "0"
    r1 = re.compile(u'预备')
    r2 = re.search(r1, content)
    if r2 != None:
        return "1"
    else:
        r3 = re.compile(u'(未遂|中止)')
        r4 = re.search(r3, content)
        if r4 != None:
            return "2"
        else:
            r5 = re.compile(u'既遂')
            r6 = re.search(r5, content)
            if r6 != None:
                return "3"
            else:
                return "0"


def judge_T_F(content):
    """
    事件要素值为False or True 的转化为数值
    """
    if(content == None):
        return "-1"  # 这里主要针对没有主动提到前科问题
    elif (content == True):
        return "1"
    else:
        return "0"


def get_patterns(event_elements):
    """
    将提取出的事件要素转换成特征
    :param event_elements: 字典形式的事件要素
    :return patterns: 字典形式的特征
    """
    patterns = dict()

    # 从事件要素中的"死亡情况"提取出特征：01死亡人数
    patterns["01死亡人数"] = extract_death_num(event_elements["死亡情况"])

    # 从事件要素中的"受伤情况"提取出三个特征：02轻微伤人数、03轻伤人数、04重伤人数
    patterns["02轻微伤人数"], patterns["03轻伤人数"], patterns["04重伤人数"] = extract_injured_num(
        event_elements["受伤情况"])

    # 从事件要素中的"罪名"提取出特征：05罪名
    if event_elements["罪名"] == "故意伤害罪":
        patterns["05罪名"] = "1"
    elif event_elements["罪名"] == "故意杀人罪":
        patterns["05罪名"] = "2"  # 故意杀人罪
    else:
        patterns["05罪名"] = "0"

    # 从事件要素中的"犯罪阶段"提取出特征：06犯罪阶段
    if (patterns["05罪名"] == 1) or (event_elements["犯罪阶段"] == None):
        patterns["06犯罪阶段"] = "0"
    else:
        patterns["06犯罪阶段"] = get_crime_stage(event_elements["犯罪阶段"])

    patterns["07是否投案"] = find_element(
        event_elements["投案"], "拨打110报警电话", "自动投案", "主动投案",  "主动要求他人帮忙报案")
    patterns["08是否如实供述"] = find_element(
        event_elements["如实供述"], "如实供述", "系坦白", "系坦白", "具有坦白情节", "主动供述", "主动交代")

    if patterns["07是否投案"] == "1" and patterns["08是否如实供述"] == "1":
        patterns["09是否自首"] = "1"
    else:
        patterns["09是否自首"] = find_element(
            event_elements["自首"], "是自首", "属自首", "构成自首", "具有自首情节")

    patterns["10是否认罪"] = find_element(
        event_elements["认罪"], "自愿认罪认罚",  "自愿认罪",  "认罪认罚",  "认罪态度较好")
    patterns["11是否赔偿"] = find_element(event_elements["赔偿"], "赔偿")
    patterns["12是否取得谅解"] = find_element(event_elements["取得谅解"], "谅解")

    patterns["13是否立功"] = judge_T_F(event_elements["是否立功"])
    patterns["14是否限制刑事责任能力"] = judge_T_F(event_elements["是否限制刑事责任能力"])
    patterns["15是否有前科"] = judge_T_F(event_elements["是否有前科"])
    patterns["16被害人是否有过错"] = judge_T_F(event_elements["被害人是否有过错"])

    patterns["判决结果"] = sentence_result_number(event_elements["判决结果"])

    return patterns
