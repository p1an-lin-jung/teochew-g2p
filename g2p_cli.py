# import tkinter as tk
import jieba
# from tkinter import *
from tkinter import Menu
import re
import jieba.analyse

teochew_dict=dict()
word_dict=dict()
madr_to_teochew=dict()
kityall_dict=dict()
swatow_dict=dict()
tenhigh_dict=dict()
low_fre_set=set()

with open('./dict_data/low_fre.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        zi,pinyin=line.strip().split('|',maxsplit=1)
        if "*" not in pinyin:
            low_fre_set.add(zi)

with open('./dict_data/convert/to_Kityall.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        tc_pinyin, target_pinyin=line.strip().split('\t')
        swatow_dict[tc_pinyin]=target_pinyin

with open('./dict_data/convert/to_Swatow.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        tc_pinyin, target_pinyin=line.strip().split('\t')
        kityall_dict[tc_pinyin]=target_pinyin
with open('./dict_data/convert/to_Tenhigh.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        tc_pinyin, target_pinyin=line.strip().split('\t')
        tenhigh_dict[tc_pinyin]=target_pinyin

with open('./dict_data/madr_to_tch.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        # try:
        md,tc=line.strip().split('|')
        # except:
            # print(line)
            # exit()    

        madr_to_teochew[md]=tc


with open('./dict_data/origin_vocab.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        zi,pinyins=line.strip().split('|',maxsplit=1)
        teochew_dict[zi]=pinyins

with open('./dict_data/vocab_extension.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        zi,pinyins=line.strip().split('|',maxsplit=1)
        teochew_dict[zi]=pinyins

with open('./dict_data/dict.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        if len(line.strip())==0:
            continue
        # try:
        word,pinyins=line.strip().split('#',maxsplit=1)
        word_dict[word]=pinyins.split(' ')
        # except:
            # print(line)

def transform_word(word,pinyin_ls):
    ls=[]
    for idx,ch in enumerate(word):
        ls.append(ch+'@'+pinyin_ls[idx])
        # ls.append()
    return ' '.join(ls)

def to_pinyin(text_list):
    ls = []
    for word in text_list:
        if word in madr_to_teochew.keys():
            ls.append('★')
        if word in word_dict.keys():
            ls.append(transform_word(word,word_dict[word]))
        else:
            for ch in word:
                if ch in teochew_dict.keys():
                    item = "@".join([ch,teochew_dict[ch]])
                    if ch in low_fre_set:
                        item='●'+item
                    ls.append(item)
                elif ch == '#':
                    continue
                else:
                    # 非文字，原样输出
                    ls.append(word)

    return ls

def to_other_accent(input_text, accent='st'):
    if accent=='st':
        target_dict=swatow_dict
    elif accent=='th':
        target_dict=tenhigh_dict
    else:
        target_dict=kityall_dict


    ls=input_text.split(' ')
    convert_ls=[]
    for item in ls:
        if '@' in item:
            ch,pinyin=item.split('@')
            if '|' in pinyin:
                pinyin_ls=pinyin.split('|')
                pinyin="|".join([target_dict[ch+'#'+one] 
                                 if ch+'#'+one in target_dict.keys() else one
                                 for one in pinyin_ls])
            else:
                pinyin= target_dict[ch+'#'+pinyin] if ch+'#'+pinyin in target_dict.keys() else pinyin

            convert_ls.append(ch+'@'+pinyin)            
        else:
            convert_ls.append(item)

    return ' '.join(convert_ls)


def add_spaces_around_punctuation(text):    
    punctuation = r"[，。？！、]"  
    pattern = rf'(?<!\s)({punctuation})(?!\s)'  
    
    replaced_text = re.sub(pattern, r' \1 ', text)  
      
    return replaced_text 

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('accent',type=str,default='st') # th、st、ky
    args = parser.parse_args()

    # 输入：第一行文件名，第二行文本
    # 输出第一行原本、第二行转换后，第三行空格
    fw=open('output.txt','w',encoding='utf-8')
    with open('input.txt','r',encoding='utf-8')as fr:
        for line in fr.readlines():
            if line.startswith('S'):
                print(line.strip(),file=fw)
                continue

            text = add_spaces_around_punctuation(line.strip())
            ls = text.split(' ')
            convert_ls=[]
            for item in ls:

                if item in madr_to_teochew.keys():
                    convert_ls.append('[ ')
                    convert_ls.append(item)
                    convert_ls.append(' : ')
                    convert_ls.append(' '.join(to_pinyin(madr_to_teochew[item])))
                    convert_ls.append(' ]')

        
            annotation =' '.join(to_pinyin(ls))
            annotation_dialect =''.join(convert_ls)
            # print(convert_ls)
            
            annotation=to_other_accent(annotation,args.accent)
            annotation_dialect=to_other_accent.wav(annotation_dialect,args.accent)
            
            print(f'{annotation}',file=fw)
            print(f'{annotation_dialect}',file=fw)
            print('',file=fw)
            # exit()
