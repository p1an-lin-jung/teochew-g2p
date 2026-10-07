"""
多种潮州话拼音方案之间的转换。

内部统一使用本仓库的潮拼（``声母 + 韵母 + 声调数字``，如 ``zui2``）作为中间表示，
其它方案都是 潮拼 -> 目标方案 的单向映射，映射表放在 ``dict_data/romanization/``。

支持的方案（``scheme`` 参数）：

    pengim    潮拼 (默认，原样输出)
    dieghv    潮语拼音
    fielde    斐尔德拼音 (声调用附加符号)
    puj       白话字，声调用变音符号 (Pe̍h-ūe-jī)
    pujn      白话字，数字声调
    pujs      白话字，上标数字声调
    ggn       家己人拼音 (Gaginang Peng'im)，数字声调
    ggns      家己人拼音，上标数字声调
    chen      陈恩泉《潮语拼音方案》，数字声调
    ipa       国际音标 (由 pyPengIm.to_IPA 处理，这里也提供一个整合入口)

白话字、斐尔德、潮语拼音、家己人的声母/韵母对应关系整理自 pengim-js
(MIT License, Copyright (c) 2024 Learn Teochew)。
"""
import os
import re
import unicodedata

from .syllable import INITIALS, NASALS

_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'dict_data', 'romanization')

SUPERSCRIPT = {'1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸'}

# 方案名 -> (映射文件, 声调风格, 展示名)
SCHEMES = {
    'pengim': (None, 'digit', '潮拼 (Peng\'im)'),
    'dieghv': ('dieghv.txt', 'digit', '潮语拼音 (Dieghv)'),
    'fielde': ('fielde.txt', 'fielde', '斐尔德拼音 (Fielde)'),
    'puj':    ('puj.txt', 'puj', '白话字 (符号声调)'),
    'pujn':   ('puj.txt', 'digit', '白话字 (数字声调)'),
    'pujs':   ('puj.txt', 'super', '白话字 (上标数字声调)'),
    'ggn':    ('ggn.txt', 'digit', '家己人拼音 (数字声调)'),
    'ggns':   ('ggn.txt', 'super', '家己人拼音 (上标数字声调)'),
    'chen':   ('chen_enquan.txt', 'digit', '陈恩泉拼音'),
}

# 声调变音符号：1、4 调不标
_PUJ_TONES = {'2': '\u0301', '3': '\u0300', '5': '\u0302', '6': '\u0303', '7': '\u0304', '8': '\u030d'}
_FIELDE_TONES = {'2': '\u0301', '3': '\u0300', '5': '\u0302', '6': '\u0306', '7': '\u0304', '8': '\u0302'}
_TONE_MARKS = {'puj': _PUJ_TONES, 'fielde': _FIELDE_TONES}

_tables = {}


def _load_table(filename):
    """读取映射文件，返回 {'ini': {}, 'fin': {}, 'nas': {}}"""
    if filename in _tables:
        return _tables[filename]
    table = {'ini': {}, 'fin': {}, 'nas': {}}
    section = None
    with open(os.path.join(_ROOT, filename), 'r', encoding='utf-8') as fr:
        for line in fr:
            line = line.strip()
            if not line:
                continue
            if line.startswith('%'):
                if line.startswith('% 声母'):
                    section = 'ini'
                elif line.startswith('% 韵母'):
                    section = 'fin'
                elif line.startswith('% 纯鼻音'):
                    section = 'nas'
                continue
            if section is None or '#' not in line:
                continue
            key, value = line.split('#', 1)
            table[section][key] = unicodedata.normalize('NFC', value)
    _tables[filename] = table
    return table


def available_schemes():
    """返回 {方案名: 展示名}，用于 GUI 下拉框"""
    return {k: v[2] for k, v in SCHEMES.items()}


def split_syllable(pinyin):
    """把潮拼音节拆成 (声母, 韵母, 声调, 是否纯鼻音)。

    合法输入形如 ``zui2``、``ng5``；不合法（如非汉字字符、英文原词）返回 None。
    """
    if len(pinyin) < 2 or pinyin[-1] not in '12345678':
        return None
    tone, body = pinyin[-1], pinyin[:-1]
    if body in NASALS:
        return '', body, tone, True
    if body[0] not in INITIALS:
        return '', body, tone, False
    k = 2 if body[:2] in ('bh', 'gh', 'ng') else 1
    return body[:k], body[k:], tone, False


def _add_tone_mark(toneless, tone, marks):
    """把变音符号放到音节的主要元音上：先 a/e/o/u/ṳ/w，其次 i，最后 n/m。"""
    mark = marks.get(tone)
    if mark is None:
        return toneless
    text = unicodedata.normalize('NFD', toneless)
    idx = None
    for pattern in (r'[aeouw]', r'i', r'[nm]'):
        m = re.search(pattern, text)
        if m:
            idx = m.start()
            break
    if idx is None:
        return toneless
    # 带下点的 ṳ / o̤ 有组合符号跟在后面，声调符号要放在它们之后
    end = idx + 1
    while end < len(text) and unicodedata.combining(text[end]) and text[end] == '\u0324':
        end += 1
    return unicodedata.normalize('NFC', text[:end] + mark + text[end:])


def convert_syllable(pinyin, scheme='pengim'):
    """把一个潮拼音节转换成目标方案。无法识别时原样返回。"""
    if scheme not in SCHEMES:
        raise ValueError("未知拼音方案: {}，可选: {}".format(scheme, ', '.join(SCHEMES)))
    filename, tone_style, _ = SCHEMES[scheme]
    if filename is None:
        return pinyin

    parts = split_syllable(pinyin)
    if parts is None:
        return pinyin
    initial, final, tone, is_nasal = parts
    table = _load_table(filename)

    if is_nasal:
        body = table['nas'].get(final)
    else:
        ini = table['ini'].get(initial, '') if initial else ''
        fin = table['fin'].get(final) if final else ''
        body = None if (initial and initial not in table['ini']) or fin is None else ini + fin
    if body is None:
        return pinyin

    if tone_style == 'digit':
        return body + tone
    if tone_style == 'super':
        return body + SUPERSCRIPT[tone]
    return _add_tone_mark(body, tone, _TONE_MARKS[tone_style])


def convert_sequence(pinyin_seq, scheme='pengim'):
    """转换以空格分隔的潮拼序列；``a|b`` 形式的多音字候选逐个转换。"""
    if scheme == 'pengim':
        return pinyin_seq
    out = []
    for token in pinyin_seq.split(' '):
        out.append('|'.join(convert_syllable(p, scheme) for p in token.split('|')))
    return ' '.join(out)


# ---------------------------------------------------------------------------
# 反向：其它方案 -> 潮拼。有了它，任意两个方案之间都可以互转（经潮拼中转）。
# ---------------------------------------------------------------------------

_TONE_CHARS = {'\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0306', '\u030d'}
_SUPERSCRIPT_REVERSE = {v: k for k, v in SUPERSCRIPT.items()}
_PUJ_TONES_REVERSE = {v: k for k, v in _PUJ_TONES.items()}
# 斐尔德的 5 调与 8 调都写 ^，靠入声韵尾区分，所以不放进这张表
_FIELDE_TONES_REVERSE = {'\u0301': '2', '\u0300': '3', '\u0306': '6', '\u0304': '7'}

# 同一个写法对应多个潮拼时的取舍。陈恩泉方案里 en 与 ng 都写成 wn，词典里 en 从未出现，故取 ng
_REVERSE_PREFER = {'chen_enquan.txt': {'wn': 'ng', 'hwn': 'hng'}}

_reverse_tables = {}


def _reverse_table(filename):
    """生成反向索引 {'syl': 整个音节(去声调)的写法 -> 潮拼, 'nas': 成音节鼻音写法 -> 潮拼}。

    以整个音节为单位索引，而不是分别索引声母和韵母：不同方案里声母和韵母的写法会粘连，
    例如陈恩泉的 hwn 既可以是 h+wn，也可以是 hng 的整体写法。
    """
    if filename in _reverse_tables:
        return _reverse_tables[filename]
    table = _load_table(filename)
    syl = {}
    for ini in [''] + list(table['ini']):
        ini_written = table['ini'][ini] if ini else ''
        for fin, fin_written in table['fin'].items():
            syl.setdefault(ini_written + fin_written, ini + fin)
    nas = {written: py for py, written in table['nas'].items()}
    for written, py in _REVERSE_PREFER.get(filename, {}).items():
        nas[written] = py
    syl.update(nas)       # 成音节鼻音优先于“声母+韵母”的拆法
    result = {'syl': syl, 'nas': nas}
    _reverse_tables[filename] = result
    return result


def _is_entering(toneless):
    """入声：以 p t k h 收尾，或鼻化入声（白话字 ⁿh、斐尔德 hⁿ，即 h 后面再跟 ⁿ）。"""
    return bool(re.search(r'[ptkh]ⁿ?$', toneless))


def _parse_tone(text, tone_style):
    """从目标方案的写法里拆出 (去掉声调的写法, 声调数字)。无法识别声调时声调为 None。"""
    if tone_style == 'digit':
        if text and text[-1] in '12345678':
            return text[:-1], text[-1]
        return text, None
    if tone_style == 'super':
        if text and text[-1] in _SUPERSCRIPT_REVERSE:
            return text[:-1], _SUPERSCRIPT_REVERSE[text[-1]]
        return text, None
    # 变音符号方案（白话字、斐尔德）：声调符号在 NFD 里是独立的组合字符
    decomposed = unicodedata.normalize('NFD', text)
    marks = [c for c in decomposed if c in _TONE_CHARS]
    plain = unicodedata.normalize('NFC', ''.join(c for c in decomposed if c not in _TONE_CHARS))
    if not marks:   # 1 调、4 调不标，靠是否入声区分
        return plain, '4' if _is_entering(plain) else '1'
    mark = marks[0]
    if tone_style == 'fielde' and mark == '\u0302':   # 斐尔德 ^：入声韵是 8 调，其余是 5 调
        return plain, '8' if _is_entering(plain) else '5'
    table = _PUJ_TONES_REVERSE if tone_style == 'puj' else _FIELDE_TONES_REVERSE
    return plain, table.get(mark)


def to_pengim_syllable(text, scheme):
    """把某个方案的一个音节还原成潮拼。无法识别时返回 None。"""
    if scheme not in SCHEMES:
        raise ValueError("未知拼音方案: {}，可选: {}".format(scheme, ', '.join(SCHEMES)))
    filename, tone_style, _ = SCHEMES[scheme]
    if filename is None:
        return text
    plain, tone = _parse_tone(unicodedata.normalize('NFC', text), tone_style)
    if tone is None or not plain:
        return None
    # 白话字、斐尔德的 5 调与 8 调以外的调号可能和声调符号无关，统一用 NFC 比对
    py = _reverse_table(filename)['syl'].get(plain)
    return None if py is None else py + tone


def to_pengim_sequence(seq, scheme):
    """把某个方案的拼音序列还原成潮拼，格式同 convert_sequence。无法识别的 token 原样保留。"""
    if scheme == 'pengim':
        return seq
    out = []
    for token in seq.split(' '):
        out.append('|'.join(to_pengim_syllable(p, scheme) or p for p in token.split('|')))
    return ' '.join(out)


def convert_between(seq, from_scheme, to_scheme):
    """任意两个拼音方案互转（经潮拼中转）。"""
    return convert_sequence(to_pengim_sequence(seq, from_scheme), to_scheme)
