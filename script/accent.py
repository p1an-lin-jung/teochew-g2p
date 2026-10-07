"""
口音互转：任意口音 -> 任意口音（经府城音中转）。

口音映射表 ``dict_data/accent_convert/to_*.txt`` 记录的是 ``汉字_府城音节#目标口音音节``，
只能府城 -> 其它口音。要反过来或在两个非府城口音之间互转，需要先还原成府城音节：

* 知道汉字时（``convert_char``、``convert_word``）：用 (汉字, 本口音读音) 反查，
  对词典里全部 12000 多个 (字, 音) 的测试里 99.9% 能唯一还原。
* 只有音节时（``candidates``）：同一个音节可能对应多个府城音节，返回按字数排序的候选，
  仅作参考，不保证唯一。

口音代码：tc 府城、ky 揭阳、st 汕头、th 澄海、gz_c 金石-经典、gz_g 金石-泛、ap 庵埠。
"""
import collections
import os

import yaml

_ACCENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'dict_data', 'accent_convert')
_VOCAB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          'dict_data', 'vocab')
_VOCAB_FILES = ('origin_vocab.txt', 'vocab_extension.txt', 'low_fre.txt')

BASE = 'tc'   # 中转用的基准口音：府城


def _load_dict(path):
    """读取 ``键#值`` 格式的词典，跳过空行和 % 注释。"""
    result = {}
    with open(path, 'r', encoding='utf-8') as fr:
        for line in fr:
            line = line.strip()
            if not line or line.startswith('%') or '#' not in line:
                continue
            key, value = line.split('#', 1)
            result[key] = value
    return result


class AccentConverter:
    """口音互转。第一次使用时才加载词典和映射表。"""

    def __init__(self):
        self._names = {BASE: '府城'}
        self._forward = {}          # 口音 -> {'字_府城音节': [目标音节, ...]}
        self._reverse = {}          # 口音 -> {(字, 目标音节): {府城音节, ...}}
        self._syllable_rev = {}     # 口音 -> {目标音节: Counter({府城音节: 字数})}
        self._char_prons = None     # 字 -> [府城音节, ...]
        self._load_registry()

    # ---------------------------------------------------------------- 加载
    def _load_registry(self):
        with open(os.path.join(_ACCENT_DIR, 'accent.yaml'), 'r', encoding='utf-8') as fr:
            config = yaml.safe_load(fr)
        self._paths = {}
        for code, item in config.items():
            self._names[code] = item['name']
            self._paths[code] = item['path']

    def accents(self):
        """返回 {口音代码: 口音名}，含府城。"""
        return dict(self._names)

    def _check(self, accent):
        if accent not in self._names:
            raise ValueError("未知口音: {}，可选: {}".format(accent, ', '.join(self._names)))

    def _vocab(self):
        if self._char_prons is None:
            chars = collections.OrderedDict()
            for filename in _VOCAB_FILES:
                for ch, value in _load_dict(os.path.join(_VOCAB_DIR, filename)).items():
                    if len(ch) != 1:
                        continue
                    chars.setdefault(ch, [])
                    for py in value.split('|'):
                        py = py.replace('*', '')
                        if py not in chars[ch]:
                            chars[ch].append(py)
            self._char_prons = chars
        return self._char_prons

    def _forward_table(self, accent):
        if accent not in self._forward:
            raw = _load_dict(os.path.join(_ACCENT_DIR, self._paths[accent]))
            self._forward[accent] = {k.replace('*', ''): [x.replace('*', '') for x in v.split('|')]
                                     for k, v in raw.items()}
        return self._forward[accent]

    def _to_accent(self, ch, tc_syllable, accent):
        """府城 (字, 音节) -> 目标口音的音节列表。表里没有就和府城相同。"""
        if accent == BASE:
            return [tc_syllable]
        return self._forward_table(accent).get('{}_{}'.format(ch, tc_syllable)) or [tc_syllable]

    def _reverse_table(self, accent):
        """(字, 该口音音节) -> 府城音节集合"""
        if accent not in self._reverse:
            rev = collections.defaultdict(set)
            for ch, prons in self._vocab().items():
                for tc in prons:
                    for target in self._to_accent(ch, tc, accent):
                        rev[(ch, target)].add(tc)
            self._reverse[accent] = rev
        return self._reverse[accent]

    def _syllable_table(self, accent):
        """该口音音节 -> Counter({府城音节: 词典里有多少个字这样对应})"""
        if accent not in self._syllable_rev:
            rev = collections.defaultdict(collections.Counter)
            for ch, prons in self._vocab().items():
                for tc in prons:
                    for target in self._to_accent(ch, tc, accent):
                        rev[target][tc] += 1
            self._syllable_rev[accent] = rev
        return self._syllable_rev[accent]

    # ---------------------------------------------------------------- 转换
    def to_base(self, ch, syllable, from_accent):
        """已知汉字时，把某口音的读音还原成府城音节列表（通常只有 1 个）。

        字不在词典里、或该读音不是这个字在这个口音下的读音时，退化为按音节候选还原；
        再不行就原样返回，不报错。
        """
        self._check(from_accent)
        if from_accent == BASE:
            return [syllable]
        exact = self._reverse_table(from_accent).get((ch, syllable))
        if exact:
            return sorted(exact)
        cands = self.candidates(syllable, from_accent)
        return cands or [syllable]

    def convert_char(self, ch, syllable, from_accent, to_accent):
        """单字转换：某口音的 (汉字, 读音) -> 另一个口音的读音列表（去重，保持顺序）。"""
        self._check(to_accent)
        result = []
        for tc in self.to_base(ch, syllable, from_accent):
            for target in self._to_accent(ch, tc, to_accent):
                if target not in result:
                    result.append(target)
        return result

    def convert_word(self, word, syllables, from_accent, to_accent):
        """词转换。word 是汉字串，syllables 与汉字一一对应，每项是该字在 from_accent 下的候选读音列表。

        返回与 syllables 同样结构的列表。非汉字（字长不匹配、候选为 None 等）原样保留。
        """
        self._check(from_accent)
        self._check(to_accent)
        out = []
        for ch, prons in zip(word, syllables):
            merged = []
            for syllable in prons:
                for target in self.convert_char(ch, syllable, from_accent, to_accent):
                    if target not in merged:
                        merged.append(target)
            out.append(merged)
        return out

    def candidates(self, syllable, from_accent):
        """只有音节、不知道汉字时：返回可能的府城音节，按词典里对应的字数从多到少排序。"""
        self._check(from_accent)
        if from_accent == BASE:
            return [syllable]
        counter = self._syllable_table(from_accent).get(syllable)
        if not counter:
            return []
        return [py for py, _ in counter.most_common()]

    def convert_syllable(self, syllable, from_accent, to_accent, top=1):
        """只有音节时的粗略转换：取最可能的 top 个府城音节再转到目标口音。

        同一音节可能对应多个府城音节（反向多解约占 8%–27%，因口音而异），
        结果仅供参考；能提供汉字时请用 convert_char / convert_word。
        """
        self._check(to_accent)
        result = []
        for tc in self.candidates(syllable, from_accent)[:top] or [syllable]:
            # 没有汉字时，目标口音的写法取“对词典里这个府城音节的字最常见的写法”
            counter = collections.Counter()
            for ch, prons in self._vocab().items():
                if tc in prons:
                    for target in self._to_accent(ch, tc, to_accent):
                        counter[target] += 1
            for target, _ in counter.most_common(1) or [(tc, 0)]:
                if target not in result:
                    result.append(target)
        return result
