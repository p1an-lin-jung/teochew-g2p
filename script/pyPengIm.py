from . import utils
import jieba.analyse

jieba.load_userdict('./dict_data/word_dict/jieba_cut.txt')


class pyPengIm():
    def __init__(self) -> None:
        self._dict_paths = {
            "vocab": "./dict_data/vocab/origin_vocab.txt",
            "vocab_extension": "./dict_data/vocab/vocab_extension.txt",
            "word_dict": "./dict_data/word_dict/dict.txt",
            "teochew_word_dict": "./dict_data/word_dict/teochew_local_dict.txt",
            "translation_dict": "./dict_data/word_dict/madr_to_tch.txt",
            "kityall_vocab": "./dict_data/accent_convert/to_Kityall.txt",
            "swatow_vocab": "./dict_data/accent_convert/to_Swatow.txt",
            "tenhigh_vocab": "./dict_data/accent_convert/to_Tenhigh.txt",
            "surname_dict": "./dict_data/vocab/Surname.txt",
            "IPA_dict": "./dict_data/vocab/IPA_lexicon.txt",
            "phoneme_dict": "./dict_data/vocab/phone.txt",
            "low_fre_dict": "./dict_data/vocab/low_fre.txt"
        }
        self._loaded_dicts = {}

    def __getattr__(self, name):
        if name in self._dict_paths:
            if name not in self._loaded_dicts:
                self._loaded_dicts[name] = utils.load_dict(self._dict_paths[name])
            return self._loaded_dicts[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def pinyin(self, text, heteronym=False, accent='tc', auto_split=True):
        if heteronym:
            pinyin_list = self._pinyin_heteronym(text)
        else:
            if auto_split:
                pinyin_list = self.pinyin_optimize(utils.preprocess_generator(jieba.cut(text)))
            else:
                pinyin_list = self.pinyin_optimize(text.split(' '))

        if accent in ['th','st','ky']:
            pinyin_list = self.convert_accent(pinyin_list, accent)

        surname_list = self._surname_notice(text)
        return {
            'result': pinyin_list,
            'pinyin_seq': self._to_pinyin_sequence(pinyin_list),
            'surname_notice': surname_list
        }

    def split(self, text, auto_split=True):
        if auto_split:
            return list(jieba.cut(text))
        else:
            return text.split(' ')            

    def _to_pinyin_sequence(self, pinyin_list):
        result = []
        for item in pinyin_list:
            for pinyin in item[1:]:
                if pinyin != ['None']:
                    result.append('|'.join([py.replace('*', '') for py in pinyin]))
        return ' '.join(result)

    def _surname_notice(self, text):
        # import pdb
        # pdb.set_trace()
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
        target_vocab = {
            'st': self.swatow_vocab,
            'ky': self.kityall_vocab
        }.get(accent, self.tenhigh_vocab)

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

    def to_IPA(self, pinyin_seq):
        return ['|'.join([self.IPA_dict[py] for py in pinyin.split('|')]) if '|' in pinyin else self.IPA_dict[pinyin] for pinyin in pinyin_seq.split(' ')]

    def to_phoneme(self, pinyin_seq):
        return ['|'.join([self.phoneme_dict[py[:-1]] + py[-1] for py in pinyin.split('|')]) if '|' in pinyin else self.phoneme_dict[pinyin[:-1]] + pinyin[-1] for pinyin in pinyin_seq.split(' ')]

    def to_oral(self, text, auto_split=True):
        word_list = jieba.cut(text) if auto_split else text.split(' ')
        return ' '.join([self.translation_dict.get(word, word) + '#' if word in self.translation_dict else word for word in word_list])

    def add_word_mapping(self, user_mapping: dict):
        self.translation_dict.update(user_mapping)

    # 查询单个字在不同地区的口音
    def single_query(self, single_char):
        if single_char not in self.vocab and single_char not in self.vocab_extension:
            return None

        if len(single_char) > 1:
            return None

        pinyin_list = self._pinyin_heteronym(single_char)
        st = self.convert_accent(pinyin_list, accent='st')
        th = self.convert_accent(pinyin_list, accent='th')
        ky = self.convert_accent(pinyin_list, accent='ky')

        return {
            '潮州': pinyin_list[0],
            '汕头': st[0],
            '澄海': th[0],
            '揭阳': ky[0]
        }
