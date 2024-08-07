import tkinter as tk
import jieba
# from tkinter import *
from tkinter import Menu

import jieba.analyse

# jieba.analyse.set_stop_words(r'D:\dict_1.txt')

def second_split(word):
    # if "今天" in word:
        # word.split
    sub = '今天'
    return word.replace(sub, f' {sub} ')
# 需要增加停止词汇，没遇到一个词就分割


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.input_var, width=150)
        self.button0 = tk.Button(self, text="   潮州府城   ", command=self.transform)
        self.button1 = tk.Button(self, text="   汕头   ", command=self.transform)
        self.button2 = tk.Button(self, text="   揭阳   ", command=self.transform)
        self.button3 = tk.Button(self, text="   澄海   ", command=self.transform)

        self.label = tk.Text(self,height=15, width=150)
        self.label_1 = tk.Text(self,height=15, width=150)

        # self.v = tk.IntVar()
        # self.rb1=tk.Radiobutton(self, text='潮州', variable=self.v, value=1).pack(anchor=tk.W)
        # self.rb2=tk.Radiobutton(self, text='汕头', variable=self.v, value=2).pack(anchor=tk.W)
        # self.rb3=tk.Radiobutton(self, text='揭阳', variable=self.v, value=2).pack(anchor=tk.W)

        self.setup_ui()

    # def transform(self):
    #     print(1)
    #     self.output_var.set("1111")
    def to_pinyin(self,text):

        return " ".join(text.split(','))
    def transform(self):
        # self.output_var.set("1111")
        input_value = self.input_var.get()
        print(input_value)
        print(self.to_pinyin(input_value))

        self.label.delete('1.0', 'end')
        self.label.insert(tk.END, self.to_pinyin(input_value))  # insert new content

        self.label_1.delete('1.0', 'end')
        # self.label_1.insert(tk.END, "|".join(jieba.cut(input_value, cut_all=False)))  # insert new content
        self.label_1.insert(tk.END, "|".join(jieba.cut_for_search(input_value)))  # insert new content
        print(second_split('今天天气'))
        # segs = jieba.cut_for_search(text)
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
    app.geometry('1400x700')
    app.mainloop()