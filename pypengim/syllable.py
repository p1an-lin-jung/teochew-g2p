
# 声母
__initials__ = [
    'b', 'bh', 'c', 'd', 'g',
    'gh', 'h', 'k', 'l', 'm',
    'n', 'ng', 'p', 'r', 's',
    't', 'z'
]

# 补充声母: 用于部分词汇，如英语iphone、汕头市区的“for”
__pad_initials__ = [
    'f'
]

# 闭口韵 
__rhyme_with_a_labial_ending__ = [
    "am", "iam", "im", "om", "uam",
    "ab", "iab", "ib", "uab",
]

# 鼻化韵、鼻化元音
__nasal_vowel__  = [
    "ain", "an", "en", "ian",
    "in", "iaon", "iaonh", "inh",
    "ioun", "ion", "oin", "on", "iun",
    "iounh", "oun", "uain", "uan", "uin", "ên", "ênh",
    "uên", "aon", "uanh",
    # 鼻音声母(m n ng)后的元音统一带鼻化，以下韵母由此产生
    "anh", "aonh", "iên", "oinh", "onh", "uênh",
]

# 韵母
__finals__ = [
    "a", "ag", "ah", "ai", "aih", "ang",
    "ao", "aoh", "e", "eg", "eh", "eng",
    "i", "ia", "iag", "iah", "iang", "iao", "iaoh",
    "ig", "ih", "ing", "io", "iog", "ioh", "iong", "iou", "iouh",
    "iu", "iê", "iêg", "iêh", "iêng",
    "o", "og", "oh", "oi", "oih", "ong", "ou",
    "u", "ua", "uag", "uah", "uai", "uang",
    "ug", "uh", "ui", "ung", "uê", "uêg", "uêh", "uêi", "uêng",
    "ê", "êg", "êh", "êi", "êng"
]

# 高化元音, 主要是府城音的特有变体: iam、iap、iau 
__raised_vowel__ = [
    "iem", "ieb", "ieu"
]


# 金石、沙溪、龙湖
__gimzieh__ = [
    'er', 'erh', 'ern'
]

INITIALS = __initials__ + __pad_initials__
FINALS = __finals__ + __nasal_vowel__ + __rhyme_with_a_labial_ending__ + __gimzieh__

# 纯鼻音
NASALS = [
    'hm', 'hng', 'hngh', 'ngh', 'ng', 'm'
]
