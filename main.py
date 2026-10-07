from script.pyPengIm import pyPengIm 

pinyin_tool = pyPengIm()

# 默认模式
print(pinyin_tool.pinyin('中心 企业'))
print(pinyin_tool.pinyin('方耀 翁万达')) 

# exit()
# 多音字模式
print(pinyin_tool.pinyin('家中',heteronym=True)) 

## 口音转换
print(pinyin_tool.pinyin('恁揭阳')['result'])# 潮州市区口音
print(pinyin_tool.pinyin('恁揭阳',accent='st')['result']) # 转汕头市区口音
print(pinyin_tool.pinyin('恁揭阳',accent='th')['result']) # 转澄海口音
print(pinyin_tool.pinyin('恁揭阳',accent='ky')['result']) # 转揭阳口音

# print(pinyin_tool.pinyin('橄榄',accent='gz_c')['result']) # 转经典金石口音
# print(pinyin_tool.pinyin('人参',accent='ap')['result']) # 转庵埠口音

#
print(pinyin_tool.pinyin('我吃蘑菇中毒了')) 

# 口语转换
print(pinyin_tool.to_oral('你要去哪里玩',auto_split=True))
print(pinyin_tool.to_oral('我 要 去 做生意',auto_split=False))
print(pinyin_tool.to_oral('晚上 晚上1 晚上2 晚上3',auto_split=False))# 加数字1、2、3，启用备选词


# '#'号控制词汇读音。
print(pinyin_tool.pinyin('生理')['pinyin_seq'])# 普通话词义，表示生物体的有机活动
print(pinyin_tool.pinyin('生理#')['pinyin_seq'])# 潮汕话词义，表示生意 

print(pinyin_tool.pinyin('倚赖')['pinyin_seq'])# 普通话词义，表示依赖、依靠
print(pinyin_tool.pinyin('倚赖#')['pinyin_seq'])# 潮汕话词义，表示诬陷、诬赖 


# 查询单字的所有读音和口音
print(pinyin_tool.single_query('生'))


# 拼音序列 转国际音标 、转音素
pinyin_seq=pinyin_tool.pinyin('我吃蘑菇中毒了')['pinyin_seq']
print(pinyin_tool.to_IPA(pinyin_seq))
print(pinyin_tool.to_phoneme(pinyin_seq))

# 其它拼音方案：默认潮拼(pengim)；可选 dieghv 潮语拼音、fielde 斐尔德、puj/pujn/pujs 白话字(符号/数字/上标声调)、
# ggn/ggns 家己人拼音(数字/上标声调)、chen 陈恩泉拼音
for scheme in ['dieghv', 'fielde', 'puj', 'pujn', 'pujs', 'ggn', 'chen']:
    print(scheme, pinyin_tool.pinyin('我吃蘑菇中毒了', scheme=scheme)['pinyin_seq'])
print(pinyin_tool.to_scheme(pinyin_seq, 'pujs'))# 也可以直接转换已有的潮拼序列

# 拼音方案互转：from_scheme 指定输入用的方案（默认潮拼），任意两个方案之间都能转
print(pinyin_tool.to_scheme('úa ngṳk mô', 'ggns', from_scheme='puj'))
print(pinyin_tool.to_scheme('ua2 jwg4 mo5', 'puj', from_scheme='chen'))

# 口音互转：任意口音 -> 任意口音。需要同时给出汉字，和该口音下的读音（与汉字一一对应）
st = pinyin_tool.pinyin('冤家', accent='st', auto_split=False)['pinyin_seq']  # 汕头读音
print(pinyin_tool.convert_accent_between('冤家', st, 'st', 'ky'))   # 汕头 -> 揭阳
print(pinyin_tool.convert_accent_between('冤家', st, 'st', 'tc'))   # 汕头 -> 府城
# 只有单个音节、不知道汉字时，是粗略转换（同一音节可能对应多个府城音节）
print(pinyin_tool.accent_converter().convert_syllable('uang1', 'st', 'ky'))



print(pinyin_tool.pinyin('*',accent='ky')['result'])



## 处理阿拉伯数字
from script.utils import num_to_chinese,num_to_chinese_smart

print(num_to_chinese('15'))
print(num_to_chinese('120'))

print(num_to_chinese_smart('15'))
print(num_to_chinese_smart('120'))
