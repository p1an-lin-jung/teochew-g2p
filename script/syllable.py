
# 声母
INITIALS = [
    'b','bh','c','d','g',
    'gh','h','k','l','m',
    'n','ng','p','r','s',
    't','z'
]

# 闭口韵 
__rhyme_with_a_labial_ending__ = [
    "am","iam","im","om","uam",
    "ab","iab","ib","uab",
]

# 鼻化韵、鼻化元音
__nasal_vowel__  = [
    "ain","an","en","ian",
    "in","iaon","iaonh","inh",
    "ioun","ion","ion","oin","on","iun",
    "iounh","oun","uain","uan","uin","ên","ênh",
    "uên","aon","uanh",
]

# 韵母
FINALS = [
    "a","ag","ah","ai",
    "aih","ang",
    "ao","aoh","e","eg",
    "eh","eng","i","ia",
    "iag","iah",
    "iang","iao","iaoh",
    "ig","ih",
    "ing","io","iog","ioh",
    "iong","iou","iouh",
    "iu","iê","iêg",
    "iêh","iêng",
    "o","og","oh","oi","oih",
    "ong","ou",
    "u","ua","uag",
    "uah","uai",
    "uang","ug","uh","ui",
    "ung","uê","uêg","uêh",
    "uêi","uêng","ê","êg",
    "êh","êi","êng",
]



# 金石、沙溪、龙湖
__gimzieh__ = [
    'eo','eoh','eon'
]
FINALS = FINALS + __nasal_vowel__ + __rhyme_with_a_labial_ending__ + __gimzieh__

# 纯鼻音
NASALS = [
    'hm','hng','hngh','ngh','ng','m'
]
