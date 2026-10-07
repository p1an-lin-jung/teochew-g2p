import gradio as gr
import jieba
from script.pyPengIm import pyPengIm 
from script import utils
from script import romanization
import yaml

pinyin_tool = pyPengIm()

accent_dict={'tc':'府城'}

with open("./dict_data/accent_convert/accent.yaml", 'r', encoding='utf-8') as file:
    accent_config = yaml.safe_load(file)
    for k,v in accent_config.items():
        accent_dict[k] = v['name']

reversed_accent_dict = {value: key for key, value in accent_dict.items()}

# 拼音方案：展示名 -> 方案代码，默认潮拼
scheme_dict = romanization.available_schemes()
reversed_scheme_dict = {value: key for key, value in scheme_dict.items()}
default_scheme_name = scheme_dict['pengim']

def auto_segment(input_text):
    return " ".join(jieba.cut(input_text))

def manual_segment(input_text):
    return " ".join(input_text.split(' '))

def single_char_query(input_text):

    result_dict = pinyin_tool.single_query(input_text.strip()[0])
    result = []
    for k, v in result_dict.items():
        result.append(k+':')
        result.append(str(v))
        result.append('\n')
    return "".join(result)

def number_conversion_0(input_text):    
    return utils.num_to_chinese(input_text)

def number_conversion_1(input_text):
    return utils.num_to_chinese_smart(input_text)
    
def clear_all():
    return "", "", ""

def to_ipa(input_text, location, return_seq):
    pinyin_seq = pinyin_tool.pinyin(input_text,accent=reversed_accent_dict[location])['pinyin_seq']
    pinyin_seq = pinyin_tool.to_IPA(pinyin_seq, blank=False)

    if return_seq:
        return pinyin_seq

    zi_at_pinyin_seq = zi_and_pinyin(input_text,pinyin_seq)
    return zi_at_pinyin_seq

def restrip(text):
    text=text.replace(' ','')
    text=text.replace('#','')
    return text

def zi_and_pinyin(text, pinyin_seq):
    if isinstance(pinyin_seq, list):
        ls = pinyin_seq
    else:
        ls = pinyin_seq.split(' ')
    
    result = []
    text = restrip(text)

    for i in range(len(text)):
        if text[i] == ls[i]:
            # 非法字符
            result.append(text[i])
        else:
            result.append(text[i]+'@'+ls[i])
    return " ".join(result)

def process_text(input_text, location, return_seq, scheme_name=default_scheme_name):
    # print(input_text)
    pinyin_seq = pinyin_tool.pinyin(
        input_text,
        accent=reversed_accent_dict[location],
        auto_split=False,
        scheme=reversed_scheme_dict[scheme_name]
    )['pinyin_seq']
    
    if return_seq:
        return pinyin_seq
    
    zi_at_pinyin_seq = zi_and_pinyin(input_text, pinyin_seq)
    return zi_at_pinyin_seq

def convert_between(han, pinyin_seq, from_accent_name, to_accent_name, from_scheme_name, to_scheme_name):
    """口音互转 + 拼音方案互转：读音按“源拼音方案”解析成潮拼，转口音后再按“目标拼音方案”输出。"""
    han = restrip(han)
    pinyin_seq = pinyin_seq.strip()
    if not pinyin_seq:
        return ""
    try:
        chaopeng = pinyin_tool.to_scheme(pinyin_seq, 'pengim', from_scheme=reversed_scheme_dict[from_scheme_name])
        from_accent = reversed_accent_dict[from_accent_name]
        to_accent = reversed_accent_dict[to_accent_name]
        if han and from_accent != to_accent:
            chaopeng = pinyin_tool.convert_accent_between(han, chaopeng, from_accent, to_accent)
        elif from_accent != to_accent:
            return "口音互转需要同时填写汉字，且汉字个数要和读音个数一致"
        return pinyin_tool.to_scheme(chaopeng, reversed_scheme_dict[to_scheme_name])
    except ValueError as e:
        return str(e)

def auto_translate(text):
    return pinyin_tool.to_oral(jieba.lcut(text))

def manual_translate(text):
    return pinyin_tool.to_oral(text.split(" "))

with gr.Blocks() as demo:
    gr.Markdown("### 潮州话文本处理工具")
    gr.Markdown("输入文本，选择地区，先进行分词，然后根据分词结果进行拼音转换")
    input_text = gr.Textbox(label="输入文本①")
    
    with gr.Row():
        return_type = gr.Dropdown(
                choices=[False,True],
                label="是否只输出纯拼音序列",
                value=False
        )

        location = gr.Dropdown(
                choices=reversed_accent_dict.keys(),
                label="地区选择",
                value="府城"
        )

        scheme = gr.Dropdown(
                choices=list(reversed_scheme_dict.keys()),
                label="拼音方案（国际音标请点“转国际音标”）",
                value=default_scheme_name
        )

    with gr.Row():
        num_conv_btn_1 = gr.Button("阿拉伯数字转汉字（智能）")
        num_conv_btn_0 = gr.Button("阿拉伯数字转汉字（直接）")
        single_char_btn = gr.Button("单字查询(查询输入文本的第一个字)")
        clear_btn = gr.Button("清空")

    # with gr.Row():
    seg_output = gr.Textbox(label="分词结果")
    pinyin_output = gr.Textbox(label="拼音转换结果")
    
    with gr.Row():
        auto_seg_btn = gr.Button("自动分词②")
        manual_seg_btn = gr.Button("手动分词(自己手动打空格)②")
        auto_translate_btn = gr.Button("翻译成口语（自动分词）")
        manual_translate_btn = gr.Button("翻译成口语（手动分词）")

    with gr.Row():
        ipa_btn = gr.Button("转国际音标③")
        pinyin_btn = gr.Button("拼音转换③")
    
    gr.Markdown("### 口音 / 拼音方案互转")
    gr.Markdown("填写汉字和对应的读音（空格分隔，每个字一个读音，多音字候选用 | 分隔），选择源与目标口音、源与目标拼音方案。"
                "只转拼音方案时可以不填汉字且口音保持一致。")
    with gr.Row():
        convert_han = gr.Textbox(label="汉字（口音互转需要）")
        convert_seq = gr.Textbox(label="读音")
    with gr.Row():
        from_accent = gr.Dropdown(choices=list(reversed_accent_dict.keys()), label="源口音", value="府城")
        to_accent = gr.Dropdown(choices=list(reversed_accent_dict.keys()), label="目标口音", value="府城")
        from_scheme = gr.Dropdown(choices=list(reversed_scheme_dict.keys()), label="源拼音方案", value=default_scheme_name)
        to_scheme = gr.Dropdown(choices=list(reversed_scheme_dict.keys()), label="目标拼音方案", value=default_scheme_name)
    convert_btn = gr.Button("互转")
    convert_output = gr.Textbox(label="互转结果")

    # 按钮事件绑定
    auto_seg_btn.click(auto_segment, input_text, seg_output)
    manual_seg_btn.click(manual_segment, input_text, seg_output)
    auto_translate_btn.click(auto_translate, input_text, seg_output)
    manual_translate_btn.click(manual_translate, input_text, seg_output)

    num_conv_btn_0.click(number_conversion_0, input_text, seg_output)
    num_conv_btn_1.click(number_conversion_1, input_text, seg_output)

    single_char_btn.click(single_char_query, input_text, pinyin_output)
    clear_btn.click(clear_all, None, [input_text, seg_output, pinyin_output])
    ipa_btn.click(to_ipa, [seg_output, location], pinyin_output)
    pinyin_btn.click(process_text, [seg_output, location, return_type, scheme], pinyin_output)
    convert_btn.click(convert_between, [convert_han, convert_seq, from_accent, to_accent, from_scheme, to_scheme], convert_output)

demo.launch()