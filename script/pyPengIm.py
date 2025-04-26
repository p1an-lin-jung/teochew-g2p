from . import utils
import jieba
import types
import yaml
import os


jieba.load_userdict('./dict_data/word_dict/jieba_cut.txt')


class pyPengIm():
    def __init__(self, history=False) -> None:
        self._dict_paths = {
            "vocab": "./dict_data/vocab/origin_vocab.txt",
            "vocab_extension": "./dict_data/vocab/vocab_extension.txt",
            "word_dict": "./dict_data/word_dict/dict.txt",
            "teochew_word_dict": "./dict_data/word_dict/teochew_local_dict.txt",
            "translation_dict": "./dict_data/word_dict/madr_to_tch.txt",
            "surname_dict": "./dict_data/vocab/Surname.txt",
            "IPA_dict": "./dict_data/vocab/IPA_lexicon.txt",
            # "phoneme_dict": "./dict_data/vocab/phone.txt",
            "low_fre_dict": "./dict_data/vocab/low_fre.txt"
        }

        self.accent_dict = self._load_accent()

        self._loaded_dicts = {}
        
        # 是否启用中国历史词典，以支持古代年号、政权、官职、人名、民族等
        if history:
            self.word_dict.update(utils.load_dict("./dict_data/word_dict/history.txt"))
            self.word_dict.update(utils.load_dict("./dict_data/word_dict/reign_title.txt"))
            

    def __getattr__(self, name):
        if name in self._dict_paths:
            if name not in self._loaded_dicts:
                self._loaded_dicts[name] = utils.load_dict(self._dict_paths[name])
            return self._loaded_dicts[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _load_accent(self,accent_config_path="./dict_data/accent_convert/accent.yaml"):
        with open(accent_config_path, 'r', encoding='utf-8') as file:
            accent_config = yaml.safe_load(file)
            accent_dict = {}
            for k,v in accent_config.items():
                accent_dict[k] = (
                        utils.load_dict(os.path.join("./dict_data/accent_convert",v['path'])),
                        v['name']
                    )

        return accent_dict
    
    def pinyin(self, text, heteronym=False, accent='', auto_split=True):
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
            'pinyin_seq': self._to_pinyin_sequence(pinyin_list),
            'surname_notice': surname_list
        }

    def sentence_cut(self, text):
        new_text_list = []
        for ch in text:
            if ch not in self.vocab and ch not in self.vocab_extension:
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
        result = []
        for ch in text:
            if ch in self.surname_dict.keys():
                item = [ch, self._to_pinyin_list(self.surname_dict[ch])]
                result.append(item)
        return result

    def _pinyin_heteronym(self, text):
        result = []
        text = text.replace('#', '')
        for zh_char in text:
            item = []
            if zh_char in self.vocab.keys():
                item.extend(self._to_pinyin_list(self.vocab[zh_char]))
            if zh_char in self.vocab_extension.keys():
                item.extend(self._to_pinyin_list(self.vocab_extension[zh_char]))
            if zh_char in self.low_fre_dict.keys():
                item.extend(self._to_pinyin_list(self.low_fre_dict[zh_char]))
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
            if word in self.teochew_word_dict.keys():
                item.extend(self._word_to_pinyin(self.teochew_word_dict[word]))
                word_found_flag = True

            if not word_translate_flag and word in self.word_dict:
                item = [word]
                item.extend(self._word_to_pinyin(self.word_dict[word]))  # 在非翻译模式下，清空之前的拼音，仅保留 word_dict 结果，也就是只保存普通话语义
                word_found_flag = True

            elif not word_translate_flag or not word_found_flag:
                if word in self.word_dict:
                    item.extend(self._word_to_pinyin(self.word_dict[word]))
                    word_found_flag = True


            if not word_found_flag:
                for zh_char in word:
                    if zh_char in self.vocab.keys():
                        item.append(self._to_pinyin_list(self.vocab[zh_char]))
                    elif zh_char in self.vocab_extension.keys():
                        item.append(self._to_pinyin_list(self.vocab_extension[zh_char]))
                    else:
                        item.append(self._to_pinyin_list('None'))

            result.append(item)
        return result

    def convert_accent(self, pinyin_list, accent):
        target_vocab = self.accent_dict[accent][0]

        result = []
        for one_pair in pinyin_list:
            word, pinyins = one_pair[0], list(one_pair[1:])
            item = [word]
            for i, hanzi in enumerate(word):
                pronunciations = []
                for pronunciation in pinyins[i]:
                    query_item = f'{hanzi}_{pronunciation}'
                    target_accent = target_vocab.get(query_item, pronunciation)
                    pronunciations.extend(self._to_pinyin_list(target_accent))
                item.append(list(dict.fromkeys(pronunciations)))# 去重
            result.append(item)
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
                    ipa_item.append(split_char.join([self.IPA_dict[ph] if ph in self.IPA_dict else ph for ph in ph_list]))
                result.append("|".join(ipa_item))
            else:
                ph_list = utils.pinyin_to_phoneme_list(pinyin)
                result.append(split_char.join(self.IPA_dict[ph] if ph in self.IPA_dict else ph for ph in ph_list))

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

        return ' '.join([self.translation_dict.get(word, word) + '#' if word in self.translation_dict else word for word in word_list])

    def add_word_mapping(self, user_mapping: dict):
        self.translation_dict.update(user_mapping)

    # 查询单个字在不同地区的口音
    def single_query(self, single_char):
        if single_char not in self.vocab and single_char not in self.vocab_extension:
            return None

        if len(single_char) > 1:
            return None

        result_dict = {}
        pinyin_list = self._pinyin_heteronym(single_char)
        result_dict['府城'] = pinyin_list[0]

        for k,v in self.accent_dict.items():
            result_dict[v[1]] = self.convert_accent(pinyin_list, accent=k)[0]

        return result_dict