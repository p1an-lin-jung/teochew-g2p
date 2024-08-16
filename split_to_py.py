import os

import jieba

import re

def replace_punctuation(input_string):
    # 定义需要替换的标点符号
    pattern = r"[，!?。《》、]"
    # 使用正则表达式替换
    return re.sub(pattern, ' ', input_string)

# input_string = "Hello, 'world'! \"Python\" is great."
# output_string = replace_punctuation(input_string)
# print(output_string)


low_fr= 'low_fre.txt'
low_dict=set()
with open(low_fr,'r',encoding='utf-8') as fp:
    for line in fp.readlines():
        if line[-1]=='*':
            continue
        low_dict.add(line.strip().split('|')[0])


full_dict={}
dict_path='full_dict.txt'

with open(dict_path,'r',encoding='utf-8') as fp:
    for line in fp.readlines():
        ls=line.strip().split('|')
        if len(ls)==2:
            out="".join(ls[1:])
            if ls[0] in low_dict:
                out+='】'
            full_dict[ls[0]]=out
        else:
            out='['+",".join(ls[1:])+']'
            if ls[0] in low_dict:
                out += '】'
            full_dict[ls[0]] = out

annotation_path='S020F001.txt'
st=set()
output='out_S020F001.txt'
fw=open(output,'w',encoding='utf-8')
with open(annotation_path,'r',encoding='utf-8')as fr:
    for line in fr.readlines():
        if len(line.strip())==0:
            continue
        if not line.startswith('S'):
            continue

        line = line.strip().split('|')[1]
        # for word in jieba.cut(line, cut_all=False):
        #     if len(word) >= 2:
        #         st.add(word)

        line = replace_punctuation(line)
        for words in line.strip().split(' '):
            # for word in words.split('，'):
            if len(words)>=2:
                st.add(words)

    for item in sorted(list(st)):
        temp=[]
        for s in item:
            if s not in full_dict.keys():
                continue
            temp.append(full_dict[s])
        pyin= " ".join(temp)
        if '[' in pyin or '】' in pyin:
            print(f"{item}|{pyin}",file=fw)
