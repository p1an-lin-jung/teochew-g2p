

import cn2an

num_map = {  
    '0': '零', '1': '【一 幺】', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'  
}

def num_to_chinese(num):
    chinese_num = ""
    for ch in num:
        if ch in num_map.keys():
            chinese_num+=num_map[ch]
        else:
            chinese_num+=ch
    # chinese_num = HanziConv.toSimplified(str(num))
    return chinese_num

def num_to_chinese_smart(num):

    return cn2an.transform(num,'an2cn')