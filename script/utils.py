
import re
import cn2an
from .syllable import *

num_map = {  
    '0': '零', '1': '【一 幺】', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'  
}



# 将数字直接转为汉字，适用于年份、电话号、身份证号等情况，15->一五、幺五 ； 110->一一零、幺幺零
def num_to_chinese(num):
    chinese_num = ""
    for ch in num:
        if ch in num_map.keys():
            chinese_num+=num_map[ch]
        else:
            chinese_num+=ch
    # chinese_num = HanziConv.toSimplified(str(num))
    return chinese_num

# 将数字智能转换，适用于表示数值的情况， 15->十五， 110->一百一十
def num_to_chinese_smart(num):
    return cn2an.transform(num,'an2cn')

# 在
def add_spaces_around_punctuation(text):
    punctuation = r"[，。？！、]"
    pattern = rf'(?<!\s)({punctuation})(?!\s)'

    replaced_text = re.sub(pattern, r' \1 ', text)

    return replaced_text

def load_dict(dict_path='./dict_data/vocab/origin_vocab.txt'):
    vocab = dict()
    with open(dict_path,'r',encoding='utf-8')as fr:
        for line in fr.readlines():
            if len(line.strip())==0:
                continue
            if line.strip().startswith('%'):
                continue
            left_item,right_item=line.strip().split('#',maxsplit=1)
            vocab[left_item]=right_item
    return vocab


# 整合jieba库分割的词汇，因为遇到#会分割。
def preprocess_generator(input_gen):
    result = []

    for item in input_gen:
        if item == '#':
            # 将#与前一个词合并
            if result:
                result[-1] += '#'
        elif item == ' ':
            # 忽略空字符串
            continue
        else:
            # 直接添加到结果中
            result.append(item)

    return result


def pinyin_to_phoneme(pinyin):
    tone = pinyin[-1]
    initial_final = pinyin[:-1]

    if initial_final in NASALS:
        return pinyin
    
    if initial_final[0] not in INITIALS:
        return pinyin

    split_idx=1
    if initial_final[:2] in ['bh','gh','ng']:
        split_idx=2

    initial = initial_final[:split_idx]
    final = initial_final[split_idx:]

    return "{} {}{}".format(initial,final,tone)

def pinyin_to_phoneme_list(pinyin):
    if len(pinyin)<=1:
        return pinyin
    
    tone = pinyin[-1]
    initial_final = pinyin[:-1]

    if initial_final in NASALS:
        return [initial_final, tone]
    
    if initial_final[0] not in INITIALS:
        return [initial_final, tone]

    split_idx=1
    if initial_final[:2] in ['bh','gh','ng']:
        split_idx=2

    initial = initial_final[:split_idx]
    final = initial_final[split_idx:]

    return [initial,final,tone]