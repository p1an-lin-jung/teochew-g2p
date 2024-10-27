import tkinter as tk
import jieba
# from tkinter import *
from tkinter import Menu

import jieba.analyse

teochew_dict=dict()
word_dict=dict()
madr_to_teochew=dict()
kityall_dict=dict()
swatow_dict=dict()
tenhigh_dict=dict()

with open('./dict_data/convert/to_Kityall.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        tc_pinyin, target_pinyin=line.strip().split('\t')
        swatow_dict[tc_pinyin]=target_pinyin

with open('./dict_data/convert/to_Swatow.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        tc_pinyin, target_pinyin=line.strip().split('\t')
        kityall_dict[tc_pinyin]=target_pinyin
with open('./dict_data/convert/to_Tenhigh.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        tc_pinyin, target_pinyin=line.strip().split('\t')
        tenhigh_dict[tc_pinyin]=target_pinyin

# with open('./dict_data/madr_to_tch.txt','r',encoding='utf-8')as fr:
#     for line in fr.readlines():
#         try:
#             md,tc=line.strip().split('|')
#         except:
#             print(line)
#             # exit()    

#         if tc.startswith('['):
#             words=tc[1:-1].split(',')
#             pys=pinyins[1:-1].split(',')
#         else:
#             words=list([tc,""])
#             pys=list([pinyins,""])    

#         madr_to_teochew[md]=(words,pys)


with open('./dict_data/origin_vocab.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        zi,pinyins=line.strip().split('|',maxsplit=1)
        teochew_dict[zi]=pinyins

with open('./dict_data/dict.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        if len(line.strip())==0:
            continue
        try:
            word,pinyins=line.strip().split('#',maxsplit=1)
            word_dict[word]=pinyins.split(' ')
        except:
            print(line)

# jieba.analyse.set_stop_words(r'D:\dict_1.txt')

# def second_split(word):
    # if "今天" in word:
        # word.split
    # sub = '今天'/
    # return word.replace(sub, f' {sub} ')
# 需要增加停止词汇，没遇到一个词就分割


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.input_var, width=150)
        self.button0 = tk.Button(self, text="   潮州府城   ", command=self.transform)
        self.button1 = tk.Button(self, text="   汕头   ", command=self.transform)
        self.button2 = tk.Button(self, text="   揭阳   ", command=self.transform_ky)
        self.button3 = tk.Button(self, text="   澄海   ", command=self.transform)

        self.label = tk.Text(self,height=15, width=150)
        self.label_1 = tk.Text(self,height=15, width=150)

        # self.v = tk.IntVar()
        # self.rb1=tk.Radiobutton(self, text='潮州', variable=self.v, value=1).pack(anchor=tk.W)
        # self.rb2=tk.Radiobutton(self, text='汕头', variable=self.v, value=2).pack(anchor=tk.W)
        # self.rb3=tk.Radiobutton(self, text='揭阳', variable=self.v, value=2).pack(anchor=tk.W)

        self.setup_ui()

    def transform_word(self,word,pinyin_ls):
        ls=[]
        for idx,ch in enumerate(word):
            ls.append(ch+'@'+pinyin_ls[idx])
            # ls.append()
        return ' '.join(ls)
    
    def to_pinyin(self,text):
        words = jieba.cut(text)
        # print(words)
        ls = []
        to_tc_word_ls=[]
        for word in words:
            # print(word)
            # print(madr_to_teochew['一起'])
            if word in madr_to_teochew.keys():
                tc_ls,py_ls=madr_to_teochew[word]
                # print(tc_ls[0],py_ls[0])

                to_tc_word_ls.append(word+':')
                to_tc_word_ls.append(self.transform_word(tc_ls[0],py_ls[0].split(' ')))
                to_tc_word_ls.append('\n')
                ls.append('【】')
            if word in word_dict.keys():
                ls.append(self.transform_word(word,word_dict[word]))
            else:
                for ch in word:
                    if ch in teochew_dict.keys():
                        item = "@".join([ch,teochew_dict[ch]])
                        ls.append(item)
                    else:
                        ls.append(word)

        return ls,to_tc_word_ls
    
    def transform(self):
        input_value = self.input_var.get()
        text_ls = jieba.cut(input_value)
        self.label.delete('1.0', 'end')
        self.label.insert(tk.END, " ".join(text_ls))


        # input_value = self.input_var.get()
        # text_ls,to_tc_word_ls =self.to_pinyin(input_value)

        # self.label.delete('1.0', 'end')
        # self.label.insert(tk.END, " ".join(text_ls))  # insert new content

        # self.label_1.delete('1.0', 'end')
        # # self.label_1.insert(tk.END, "|".join(jieba.cut(input_value, cut_all=False)))  # insert new content
        # self.label_1.insert(tk.END, " ".join(to_tc_word_ls))  # insert new content
    
    def transform_ky(self):
        return ''
        input_value = self.input_var.get()
        text_ls,to_tc_word_ls = self.to_pinyin(input_value)
        text_ls=" ".join(text_ls).split(' ')
        print(text_ls)
        new_text_ls=[]
        for item in text_ls:

            if '%' in item:
                try:
                    ch,pinyin_ls=item.split('%')
                except:
                    print(item)
            else:
                ch= item            
            if ch not in kityall_dict.keys():
                new_text_ls.append(item)
                continue
            if '|' in pinyin_ls:
                target='|'.join([kityall_dict[ch+'#'+pinyin] for pinyin in pinyin_ls.split('|')])
                    
            else:
                target=kityall_dict[ch+'#'+pinyin_ls]
            new_text_ls.append(ch+' '+target)

        new_convert_ls=[]
        for item in to_tc_word_ls:
            try:
                ch,pinyin_ls=item.split(' ')
            except :
                print(item)

            if ch not in kityall_dict.keys():
                new_convert_ls.append(item)
                continue
            if '|' in pinyin_ls:
                target='|'.join([kityall_dict[ch+'#'+pinyin] for pinyin in pinyin_ls.split('|')])
            
            else:
                target=kityall_dict[ch+'#'+pinyin_ls]
            new_convert_ls.append(ch+' '+target)

        self.label.delete('1.0', 'end')
        self.label.insert(tk.END, ' '.join(new_text_ls))  # insert new content

        self.label_1.delete('1.0', 'end')
        # self.label_1.insert(tk.END, "|".join(jieba.cut(input_value, cut_all=False)))  # insert new content
        self.label_1.insert(tk.END, ' '.join(new_convert_ls))  # insert new content
    
    def setup_ui(self):
        self.entry['font'] =  ("Helvetica", 10)
        self.label['bg'] = '#CCFF99'
        self.label['fg'] = 'black'
        self.label['relief'] = 'ridge'
        self.label['borderwidth'] = 5
        # self.label['anchor'] = 'center'
        # self.label['justify'] = 'left'

        # self.label['wraplength'] = 800
        self.label['padx'] = 10
        self.label['pady'] = 10
        self.label['cursor'] = 'hand2'
        self.bind_events()
        self.place_elements()

        label_input = tk.Label(self, text="Input")
        label_input.grid(row=0, column=0,sticky="W")
        self.entry.grid(row=1, column=0)
        # button_transfer = tk.Button(self, text="Transfer", command=self.transform)
        label_output = tk.Label(self, text="Output")
        label_output.grid(row=2, column=0,sticky="W")
        self.label.grid(row=3, column=0)
        label_output = tk.Label(self, text="")
        label_output.grid(row=4, column=0,sticky="W")

        label_None = tk.Label(self, text="\t")
        label_None.grid(row=4, column=1,sticky="E")

        self.label_1.grid(row=5, column=0)
        self.button0.grid(row=1, column=2,sticky="E")
        self.button1.grid(row=3, column=2,sticky="E")
        self.button2.grid(row=5, column=2,sticky="E")
        self.button3.grid(row=4, column=2,sticky="E")
        # self.rb1.grid(row=7, column=0)
        # self.rb2.grid(row=7, column=1)
        # self.rb3.grid(row=7, column=1)

    def bind_events(self):
        self.entry.bind('<Return>', lambda event: self.update())

    def place_elements(self):
        self.entry.grid(row=0, column=0, sticky='ew')
        self.button0.grid(row=0, column=1, columnspan=2, padx=5)
        self.label.grid(row=1, column=0, sticky='news')

    def update(self):
        input_value = self.input_var.get()
        # self.output_var.insert('1.0', input_value)

if __name__ == "__main__":
    app = App()
    app.geometry('1200x500')
    app.mainloop()