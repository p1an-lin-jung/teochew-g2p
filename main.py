
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



print(pinyin_tool.pinyin('*',accent='ky')['result'])



## 处理阿拉伯数字
from script.utils import num_to_chinese,num_to_chinese_smart

print(num_to_chinese('15'))
print(num_to_chinese('120'))

print(num_to_chinese_smart('15'))
print(num_to_chinese_smart('120'))
