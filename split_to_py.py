import jieba
import os
madr_to_teochew=dict()

with open('./dict_data/madr_to_tch.txt','r',encoding='utf-8')as fr:
    for line in fr.readlines():
        # try:
        md,tc=line.strip().split('#')
        # except:
            # print(line)
            # exit()    
        
        if md in ['他' ,'的' ,'这个','这位','今天','咱们','我们','这里','说','和']:
            continue            
        madr_to_teochew[md]=tc



fw= open('input.txt','w',encoding='utf-8')
path=r'F:\audio\要标注\S009'
for file in os.listdir(path):
    if file == 'S009F002.txt':

        with open(os.path.join(path,file),'r',encoding='utf-8')as fr:
            for line in fr.readlines():

                if len(line.strip())==0:
                    continue
                # name,annot=line.strip().split('|')
                # text_ls = jieba.cut(annot)
                # print(f'{name}\n{" ".join(text_ls)}',file=fw)
                if line.startswith('S'):
                    print('',file=fw)
                    print(f'{line.strip()}',file=fw)
                    # fname,annot=line.strip().split('|')
                    # print(fname,file=fw)
                    
                    # text_ls = jieba.cut(annot)
                    # ls=[]
                    # for item in text_ls:
                    #     if item in madr_to_teochew.keys():
                    #         ls.append(item+'#')
                    #     else:
                    #         ls.append(item)
                    # print(' '.join(ls),end=' ',file=fw)
                else:
                # if True:
                    # ls=line.strip().split('|')
                    # print(ls[0],file=fw)

                    # annot=ls[1]
                    annot=line.strip()
                    text_ls = jieba.cut(annot)
                    ls=[]
                    for item in text_ls:
                        if item in madr_to_teochew.keys():
                            ls.append(item+'#')
                        else:
                            ls.append(item)
                    print(' '.join(ls),end=' ',file=fw)