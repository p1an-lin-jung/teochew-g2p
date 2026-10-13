from . import utils
from . import romanization
from .accent import AccentConverter
import jieba
import types
import yaml
import os

from . import DATA_DIR


def _data(*parts):
    """包内数据文件的绝对路径，与当前工作目录无关。"""
    return os.path.join(DATA_DIR, *parts)


with open(_data('word_dict', 'jieba_userdict.txt'), 'rb') as _fr:
    jieba.load_userdict(_fr)

class pyPengIm():
    def __init__(self, history=False) -> None:
        self._dict_paths = {
            "char_main": _data('char_dict', 'char_main.txt'),
            "char_extension": _data('char_dict', 'char_extension.txt'),
            "word_common": _data('word_dict', 'word_common.txt'),
            "word_teochew": _data('word_dict', 'word_teochew.txt'),
            "mandarin_to_teochew": _data('word_dict', 'mandarin_to_teochew.txt'),
            "word_surname": _data('word_dict', 'word_surname.txt'),
            "syllable_to_ipa": _data('phonology', 'syllable_to_ipa.txt'),
            # "syllable_to_phone": _data('phonology', 'syllable_to_phone.txt'),
            "char_low_frequency": _data('char_dict', 'char_low_frequency.txt')
        }

        self.accent_dict = self._load_accent()
        self._accent_converter = AccentConverter()

        self._loaded_dicts = {}
        
        # 是否启用中国历史词典，以支持古代年号、政权、官职、人名、民族等
        if history:
            self.word_common.update(utils.load_dict(_data('word_dict', 'word_history.txt')))
            self.word_common.update(utils.load_dict(_data('word_dict', 'word_reign_title.txt')))

        jieba.cut('')# 预热

    # 旧属性名 -> 新属性名，兼容外部代码
    _LEGACY_NAMES = {
        'vocab': 'char_main',
        'vocab_extension': 'char_extension',
        'low_fre_dict': 'char_low_frequency',
        'word_dict': 'word_common',
        'teochew_word_dict': 'word_teochew',
        'translation_dict': 'mandarin_to_teochew',
        'surname_dict': 'word_surname',
        'IPA_dict': 'syllable_to_ipa',
    }

    def __getattr__(self, name):
        name = self._LEGACY_NAMES.get(name, name)
        if name in self._dict_paths:
            if name not in self._loaded_dicts:
                self._loaded_dicts[name] = utils.load_dict(self._dict_paths[name])
            return self._loaded_dicts[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _load_accent(self, accent_config_path=None):
        accent_config_path = accent_config_path or _data('accent_convert', 'accent.yaml')
        with open(accent_config_path, 'r', encoding='utf-8') as file:
            accent_config = yaml.safe_load(file)
            accent_dict = {}
            for k,v in accent_config.items():
                accent_dict[k] = (
                        utils.load_dict(_data('accent_convert', v['path'])),
                        v['name']
                    )

        return accent_dict
    
    def pinyin(self, text, heteronym=False, accent='', auto_split=True, scheme='pengim'):
        """汉字转拼音。

        scheme: 输出的拼音方案，默认 'pengim'（潮拼）。可选值见 romanization.available_schemes()。
                'result' 字段始终保持潮拼，只有 'pinyin_seq' 会按 scheme 转换。
        """
        if scheme not in romanization.SCHEMES:
            raise ValueError("未知拼音方案: {}，可选: {}".format(scheme, ', '.join(romanization.SCHEMES)))
        text = text.upper()
        if heteronym:
            pinyin_list = self._pinyin_heteronym(text)
        else:
            if auto_split:
                pinyin_list = self.pinyin_optimize(utils.preprocess_generator(self.sentence_cut(text)))
            else:
                pinyin_list = self.pinyin_optimize(text.split(' '))

        if accent in self.accent_dict:
            pinyin_list = self.convert_accent(pinyin_list, accent)

        surname_list = self._surname_notice(text)

        return {
            'result': pinyin_list,
            'pinyin_seq': self.to_scheme(self._to_pinyin_sequence(pinyin_list), scheme),
            'surname_notice': surname_list
        }

    def to_scheme(self, pinyin_seq, scheme='pengim', from_scheme='pengim'):
        """拼音方案互转：把 from_scheme 写的拼音序列（空格分隔，多音字用 | 分隔）转成 scheme。

        不写 from_scheme 时，输入按潮拼处理。任意两个方案之间都可以互转，内部经潮拼中转。
        scheme / from_scheme 可选: pengim(潮拼)、dieghv(潮语拼音)、fielde(斐尔德)、puj(白话字，符号声调)、
        pujn(白话字，数字声调)、pujs(白话字，上标声调)、ggn(家己人)、ggns(家己人，上标声调)、chen(陈恩泉)。
        反向解析时，无法识别的音节原样保留。
        """
        for name in (scheme, from_scheme):
            if name not in romanization.SCHEMES:
                raise ValueError("未知拼音方案: {}，可选: {}".format(name, ', '.join(romanization.SCHEMES)))
        return romanization.convert_between(pinyin_seq, from_scheme, scheme)

    def convert_accent_between(self, word, pinyin_seq, from_accent, to_accent):
        """口音互转：把 from_accent 口音下 word 的读音，转成 to_accent 口音。

        word 是汉字串；pinyin_seq 是与汉字一一对应的潮拼序列（空格分隔，多音字候选用 | 分隔），
        可以是任意口音的读音，只要和 from_accent 一致。返回同样格式的字符串。
        口音代码见 accent_converter().accents()：tc 府城、ky 揭阳、st 汕头、th 澄海、gz_c / gz_g 金石、ap 庵埠。
        已知汉字时能精确还原（词典里 99.9% 的 (字,音) 可唯一还原）；word 与读音数量对不上时抛 ValueError。
        """
        syllables = [token.split('|') for token in pinyin_seq.split(' ')]
        if len(word) != len(syllables):
            raise ValueError("汉字数 {} 与读音数 {} 不一致".format(len(word), len(syllables)))
        converted = self._accent_converter.convert_word(word, syllables, from_accent, to_accent)
        return ' '.join('|'.join(item) if item else syl for item, syl in zip(converted, pinyin_seq.split(' ')))

    def accent_converter(self):
        """返回口音互转器，可直接调用 convert_char / convert_syllable / candidates 等。"""
        return self._accent_converter

    def sentence_cut(self, text):
        new_text_list = []
        for ch in text:
            if ch not in self.char_main and ch not in self.char_extension:
                new_text_list.append(' {} '.format(ch))
            else:
                new_text_list.append(ch)
        
        return jieba.cut("".join(new_text_list))


    def _to_pinyin_sequence(self, pinyin_list):
        result = []
        for item in pinyin_list:
            for pinyin in item[1:]:
                if pinyin != ['None']:
                    result.append('|'.join([py.replace('*', '') for py in pinyin]))
                else:
                    result.append(item[0]) ## 非法字符，原样输出

        return ' '.join(result)

    def _surname_notice(self, text):
        """找出文本里的姓氏及其读音。复姓优先（最长匹配），如「诸葛亮」只报「诸葛」。

        返回格式与 pinyin() 的 result 一致：[姓氏, [第1字读音...], [第2字读音...]]。
        """
        surnames = self.word_surname
        max_len = max((len(k) for k in surnames), default=1)
        result = []
        i = 0
        while i < len(text):
            for length in range(min(max_len, len(text) - i), 0, -1):
                word = text[i:i + length]
                if word in surnames:
                    result.append([word] + [self._to_pinyin_list(s) for s in surnames[word].split(' ')])
                    i += length
                    break
            else:
                i += 1
        return result

    def _pinyin_heteronym(self, text):
        result = []
        text = text.replace('#', '')
        for zh_char in text:
            item = []
            if zh_char in self.char_main.keys():
                item.extend(self._to_pinyin_list(self.char_main[zh_char]))
            if zh_char in self.char_extension.keys():
                item.extend(self._to_pinyin_list(self.char_extension[zh_char]))
            if zh_char in self.char_low_frequency.keys():
                item.extend(self._to_pinyin_list(self.char_low_frequency[zh_char]))
            result.append([zh_char, item])

        return result

    def _to_pinyin_list(self, pinyin_item):
        return pinyin_item.split('|') if '|' in pinyin_item else [pinyin_item]

    def _word_to_pinyin(self, item_word):
        if ' ' in item_word:
            return [self._to_pinyin_list(pinyin) for pinyin in item_word.split(' ')]
        return [[item_word]]

    def pinyin_optimize(self, word_list):
        result = []
        for word in word_list:
            if not word.strip():
                continue

            word_translate_flag = word.endswith('#')
            word = word.rstrip('#')
            word_found_flag = False

            item = [word]
            if word in self.word_teochew.keys():
                item.extend(self._word_to_pinyin(self.word_teochew[word]))
                word_found_flag = True

            if not word_translate_flag and word in self.word_common:
                item = [word]
                item.extend(self._word_to_pinyin(self.word_common[word]))  # 在非翻译模式下，清空之前的拼音，仅保留 word_common 结果，也就是只保存普通话语义
                word_found_flag = True

            elif not word_translate_flag or not word_found_flag:
                if word in self.word_common:
                    item.extend(self._word_to_pinyin(self.word_common[word]))
                    word_found_flag = True


            if not word_found_flag:
                for zh_char in word:
                    if zh_char in self.char_main.keys():
                        item.append(self._to_pinyin_list(self.char_main[zh_char]))
                    elif zh_char in self.char_extension.keys():
                        item.append(self._to_pinyin_list(self.char_extension[zh_char]))
                    else:
                        item.append(self._to_pinyin_list('None'))

            result.append(item)
        return result

    def convert_accent(self, pinyin_list, accent):
        """府城音 -> 目标口音。每个分词结果内先匹配词级映射（如揭阳「家己」），其余按字转换。"""
        result = []
        for one_pair in pinyin_list:
            word, pinyins = one_pair[0], list(one_pair[1:])
            if len(word) != len(pinyins):      # 字数与读音数对不上（如词典数据有误），原样保留
                result.append([word] + pinyins)
                continue
            converted = self._accent_converter.convert_from_base(word, pinyins, accent)
            result.append([word] + converted)
        return result

    def to_IPA(self, pinyin_seq, blank=True):
        if blank:
            split_char = ' '
        else:
            split_char = ''

        result = []
        for pinyin in pinyin_seq.split(' '):
            if '|' in pinyin:
                ipa_item = []
                for py in pinyin.split('|'):
                    ph_list = utils.pinyin_to_phoneme_list(py)
                    ipa_item.append(split_char.join([self.syllable_to_ipa[ph] if ph in self.syllable_to_ipa else ph for ph in ph_list]))
                result.append("|".join(ipa_item))
            else:
                ph_list = utils.pinyin_to_phoneme_list(pinyin)
                result.append(split_char.join(self.syllable_to_ipa[ph] if ph in self.syllable_to_ipa else ph for ph in ph_list))

        return result

    def to_phoneme(self, pinyin_seq):
        return ['|'.join([utils.pinyin_to_phoneme(py) for py in pinyin.split('|')]) if '|' in pinyin else utils.pinyin_to_phoneme(pinyin) for pinyin in pinyin_seq.split(' ')]

    def to_oral(self, text, auto_split=True):
        if isinstance(text, list) or isinstance(text, types.GeneratorType):
            word_list = text
        elif isinstance(text, str):
            word_list = jieba.cut(text) if auto_split else text.split(' ')
        else:
            return None

        return ' '.join([self.mandarin_to_teochew.get(word, word) + '#' if word in self.mandarin_to_teochew else word for word in word_list])

    def add_word_mapping(self, user_mapping: dict):
        self.mandarin_to_teochew.update(user_mapping)

    # 查询单个字在不同地区的口音
    def single_query(self, single_char):
        if single_char not in self.char_main and single_char not in self.char_extension:
            return None

        if len(single_char) > 1:
            return None

        result_dict = {}
        pinyin_list = self._pinyin_heteronym(single_char)
        result_dict['府城'] = pinyin_list[0]

        for k,v in self.accent_dict.items():
            result_dict[v[1]] = self.convert_accent(pinyin_list, accent=k)[0]

        return result_dict