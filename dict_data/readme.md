
# 字典、词典文件简介

文件命名约定：单字字表以 `char_` 开头，词表以 `word_` 开头，音节层面的映射放在 `phonology/`。所有文件均为 UTF-8，每行 `键#值`，以 `%` 开头的行是注释。

```
dict_data/
├── char_dict/        单字读音
├── word_dict/        词汇读音、普通话→潮汕话映射、分词词典
├── phonology/        音节 → 音素 / 国际音标
├── accent_convert/   府城音 → 各地口音
├── romanization/     潮拼 → 其它拼音方案
└── sentence/         句子语料
```

## accent_convert 目录
顾名思义，本目录存放着口音转换字典，几个txt文件分别是府城音到汕头(Swatow)、揭阳(Kityall)、澄海(Tenhigh)、金石、庵埠等地口音的映射对照。

每行有两种写法：
- 字对字：`字_府城音节#目标音节`，如 `反_huêng2#huang2`。
- 词对词：`词_府城读音#目标读音`，读音按字用空格分隔，每个字的多个候选用 `|` 分隔，如 `家己_ga1 gi7#ga1 di7|li7`。只有整个词出现、且府城读音对得上时才生效，用于只在特定词里发生的口音变化。

## char_dict 目录

本文件夹存放着多个核心字典文件，包括：

#### 1、char_main.txt
主字表。该文件是从潮州音字典的原始数据修改而来，去掉了较为低频或只用于特定词汇的发音，并对部分读音进行修改、优化。

#### 2、char_low_frequency.txt
该文件记录了 char_main.txt 中剔除的较为低频读音，其中带星号(*)表示极为低频。

#### 3、char_extension.txt
该文件记录了原字典里没有收录汉字，或者针对有音无字问题引入、改造的新字。也包括了部分英语字母。

#### 4、char_nasal_variants.txt
同一个字既可读鼻化韵、也可读非鼻化韵的读音对（声母、声调相同），如 `底#doi2|doin2`。按韵母分组：i-in、iu-iun、ua-uan、ui-uin、oi-oin 等。

#### 5、char_mispronunciation.txt

由于现在的义务教育大力推普，加上传统的文化行业（如方言小品剧、讲古）的衰落，以及潮汕话电子版资料相对较少，很多潮汕人很多发音习惯会受普通话的影响，例如：

```
趁: 读成 cêng3
奔：读成 bung1
荐: 读成 giang3
标：读成 biou1
宠：读成 cong2
揣：读成 cuai2
蹭：读成 cêng3
```
此类的错误发音已经成为事实，因此我增加了 `char_mispronunciation.txt` 的文件，记录此类错误发音。

该文件将持续记录。

#### 6、char_traditional.txt
繁体字（与简体字读音有别时）的读音，如 臟、髒。

## word_dict 目录
本文件夹存放着多个核心词典文件，包括：

#### 1、word_common.txt
存放常用词汇的读音，用于多音字消歧。主要是普通话词汇为主，因为项目早期没做特别区分，所以也混杂了一些潮汕话方言词汇进去，待后续检查、改进。

#### 2、word_teochew.txt
存放方言词汇的读音。例如【生理】，在 word_common.txt 中是【sên1 li2】，表示【生物机体的生命活动和各个器官的机能】；在 word_teochew.txt 中是【sêng1 li2】，表示【生意、买卖】。

#### 3、word_surname.txt
该文件整理了常用姓氏（含复姓）的潮汕话读音情况。

#### 4、word_place.txt
整理古今中外和潮汕本土地名，基本涵盖世界上大部分国家和地区，以及主要城市。
本土地名尽量遵循习惯读法和白读音。
国内其他地区和国外地名优先遵循习惯读法，如该地名较少用，则优先用文读音。

#### 5、word_history.txt
存放历史相关词汇（朝代、政权名、民族、人名、官职）。

#### 6、word_reign_title.txt
记录古代皇帝年号专用词。

#### 7、mandarin_to_teochew.txt
用于将普通话词汇映射到更为地道的潮汕话词汇。

#### 8、homophone_substitution.txt
谐音字替换。记录潮汕人在微信、抖音等平台习惯喜欢用的谐音字。

#### 9、jieba_userdict.txt
jieba 用户词典。针对上述词典文件进行整理，辅助 jieba 库的分词，使之更加适配潮汕话的分词。

## phonology 目录

#### 1、syllable_to_phone.txt / syllable_to_phone_nasalized.txt
将拼音映射为更小的音素，也就是 `声母 + 韵母` 的模式。分两份：
- `syllable_to_phone.txt`：原版，m/n/ng 声母后的元音不标鼻化，如 `ma#m a`。
- `syllable_to_phone_nasalized.txt`：鼻化版，m/n/ng 声母后的元音一律带鼻化，如 `man#m an`、`muênh#m uênh`，与当前字典、词典和语料的标注约定一致。

#### 2、syllable_to_ipa.txt
该文件将拼音映射到国际音标IPA，方便与现有多语言语音大模型接轨。

## 文件更名对照

| 旧路径 | 新路径 |
|---|---|
| vocab/origin_vocab.txt | char_dict/char_main.txt |
| vocab/low_fre.txt | char_dict/char_low_frequency.txt |
| vocab/vocab_extension.txt | char_dict/char_extension.txt |
| vocab/鼻音.txt | char_dict/char_nasal_variants.txt |
| vocab/error_pronunciation.txt | char_dict/char_mispronunciation.txt |
| vocab/traditional_chinese.txt | char_dict/char_traditional.txt |
| vocab/Surname.txt | word_dict/word_surname.txt |
| vocab/phone.txt | phonology/syllable_to_phone.txt |
| vocab/IPA_lexicon.txt | phonology/syllable_to_ipa.txt |
| word_dict/dict.txt | word_dict/word_common.txt |
| word_dict/teochew_local_dict.txt | word_dict/word_teochew.txt |
| word_dict/place.txt | word_dict/word_place.txt |
| word_dict/history.txt | word_dict/word_history.txt |
| word_dict/reign_title.txt | word_dict/word_reign_title.txt |
| word_dict/madr_to_tch.txt | word_dict/mandarin_to_teochew.txt |
| word_dict/homophonic_substitution.txt | word_dict/homophone_substitution.txt |
| word_dict/jieba_cut.txt | word_dict/jieba_userdict.txt |
