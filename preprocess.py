# -*- coding: utf-8 -*
from __future__ import division
from nlpir import *
import glob
import math
import re
import os

def read_file(root_path):
    #批量读取文件
    files_dict = dict()
    while root_path != "finish":
        if len(root_path) == 0:
            root_path = raw_input("该路径错误，或者路径下无txt类型文件，请重新输入：\n")
        else:
            root_path = root_path + '\\'
            path_check = False          #布尔变量，用于检查能否从该路径下读取txt文件
            path = glob.glob(root_path + '*' + 'txt')  #读取该路径下所有txt文件的路径
            for file_path in path:          #root_path 是文件夹路径，path是list，存放所有txt路径,file_path 是一次循环中用到的（一个）路径
                path_check = True
                file_name_check = True    #用来检查是否已经读取过重名文件
                name_suffix = 1      #用于重名文件添加文件名后缀
                try:
                    file = open(file_path, "r").read().decode("gbk").encode("utf-8")   #从路径打开文件
                except UnicodeDecodeError:
                    i = 0
                file_name = file_path.split("\\")          #从路径中取文件名
                file_name = file_name[-1]
                file_name = file_name.split(".")
                file_name = file_name[0]
                while file_name_check == True:
                    if files_dict.has_key(file_name):
                        if name_suffix == 1:
                            file_name = file_name + '_' + str(name_suffix)
                        else:
                            file_name = file_name - str(name_suffix) + str(name_suffix + 1)
                            name_suffix += 1
                    else:
                        break
                files_dict[file_name] = file
            if path_check == False:
                root_path = raw_input("该路径错误，或者路径下无txt类型文件，请重新输入：\n")
            else:
                root_path = "finish"
    print "已完成读取工作！"
    root_path = '0'
    return files_dict

def nlpir_segment(file_name_str):
    #nlpir 分词,参数为string格式文章，返回分词结果，list格式
    file_name_list = []
    for t in Seg(file_name_str):
        file_name_list.append('%s' % (t[0]))
    # print "已完成文档“" + file_name + "”的分词工作！"
    return file_name_list

def delete_stop(file_list):
    #删除停用词
    f = open("stoplist.txt", "r")
    stopword_list = list()
    for elem in open("stoplist.txt", "r"):
        stopword_list.append(f.readline().decode("gbk").encode("utf-8").replace("\n", ""))
    for elem in stopword_list:
        if elem in file_list:
            for i in range(file_list.count(elem)):
                file_list.remove(elem)
    # print "文档“" + file_name + "”已过滤停用词！"

def VSM_generate(file_name_list):
    #生成VSM,参数为单个文件的分词结果（list格式），返回dict格式的VSM结果，该dict里每一个特征作为一个键关联一个内层dict，
    #该内层dict里有‘count’键，关联的值为特征出现次数
    file_name_dict = dict()
    for elem in file_name_list:
        if file_name_dict.has_key(elem):
            file_name_dict[elem]['count'] += 1
        if file_name_dict.has_key(elem) == False:
            file_name_dict[elem] = dict()
            file_name_dict[elem]['count'] = 1
    # print "文档“" + file_name + "”已生成VSM!"
    return file_name_dict

def tfidf(files_dict):
    #对于文档集执行tf_idf算法
    file_count = 0  # 文档集中文档的数量，用于计算idf
    for file_namex in files_dict:    #计算文档集中文档的数量
        file_count += 1
    for file_name in files_dict:    #计算每一个特征的tfidf
        file_words_count = 0 # 该文档总字数,用于计算tf
        for elem in files_dict[file_name]:  # 计算文档总字数
            file_words_count += files_dict[file_name][elem]['count']
        for elem in files_dict[file_name]:
            occur_count = 0  # 包含该词的文档数，用于计算idf
            tf = files_dict[file_name][elem]['count']/file_words_count
            for file_name1 in files_dict:
                if files_dict[file_name1].has_key(elem):
                    occur_count += 1
            idf = math.log((file_count)/occur_count, 10)
            if idf == 0:
                idf = -100000000000000000000
            files_dict[file_name][elem]['tfidf'] = tf * idf


        # print "文档“" + file_name + "”已执行tfidf算法!"

def printing(files_dict, amount): #输出，amount规定选择前amount个数值
    ranked_dict = dict()
    if os.path.isdir('result') == False:
        os.makedirs('result')
    for file_name in files_dict:

        file1 = open('result\\' + file_name + '_TF-IDF' + '.txt', 'w')
        file2 = open('result\\' + file_name + '_CHI' + '.txt', 'w')
        file3 = open('result\\' + file_name + '_MI' + '.txt', 'w')
        file4 = open('result\\' + file_name + '_IG' + '.txt', 'w')
        str1 = ''
        str2 = ''
        str3 = ''
        str4 = ''
        if len(files_dict[file_name]) < amount:
            tmp_amount = len(files_dict[file_name]) #避免要求输出特征数目超过已有数目
        else:
            tmp_amount = amount
        dict1 = dict()
        for i in range(tmp_amount):
            temp_value = 0 #临时变量，用于记录当前最大值
            temp_elem = "1"
            for elem in files_dict[file_name]:
                if files_dict[file_name][elem]['tfidf'] > temp_value and elem not in dict1:
                    temp_value = files_dict[file_name][elem]['tfidf']
                    temp_elem = elem
            if temp_elem != '1':
                str1 += str('\n' + str(temp_elem) + ":" + str(temp_value))
            dict1[temp_elem] = temp_value
        file1.write(str1)

        for i in range(amount):
            temp_value = 0 #临时变量，用于记录当前最大值
            temp_elem = "1"
            for elem in files_dict[file_name]:
                if files_dict[file_name][elem]['chi'] > temp_value and elem not in dict1:
                    temp_value = files_dict[file_name][elem]['chi']
                    temp_elem = elem
            if temp_elem != '1':
                str2 += str('\n' + str(temp_elem) + ":" + str(temp_value))
            dict1[temp_elem] = temp_value
        file2.write(str2)

        for i in range(amount):
            temp_value = 0  # 临时变量，用于记录当前最大值
            temp_elem = "1"
            for elem in files_dict[file_name]:
                if files_dict[file_name][elem]['mi'] > temp_value and elem not in dict1:
                    temp_value = files_dict[file_name][elem]['mi']
                    temp_elem = elem
            if temp_elem != '1':
                str3 += str('\n' + str(temp_elem) + ":" + str(temp_value))
            dict1[temp_elem] = temp_value
        file3.write(str3)

        for i in range(amount):
            temp_value = 0  # 临时变量，用于记录当前最大值
            temp_elem = "1"
            for elem in files_dict[file_name]:
                if files_dict[file_name][elem]['ig'] > temp_value and elem not in dict1:
                    temp_value = files_dict[file_name][elem]['ig']
                    temp_elem = elem
            if temp_elem != '1':
                str4 += str('\n' + str(temp_elem) + ":" + str(temp_value))
            dict1[temp_elem] = temp_value
        file4.write(str4)
    print("\n\n执行完毕，结果已输出至" + os.path.abspath('.') + '\\result')
    print("-----------------------------------")

def vsmprocess(files_dict):
    for file_name in files_dict:
        files_dict[file_name] = nlpir_segment(files_dict[file_name])
        delete_stop(files_dict[file_name])
        files_dict[file_name] = VSM_generate(files_dict[file_name])

def CHI(files_dict, trained_dict1, trained_dict2):
    N, A, B, C, D = 1, 1, 1, 1, 1
    for trained_name in trained_dict1:
        N += 1
    for files_name in files_dict:
        for elem in files_dict[files_name]:
            A, B, C, D = 1, 1, 1, 1
            for trained_name in trained_dict1:
                if elem in trained_dict1[trained_name]:
                    A += 1
                else:
                    C += 1
            for trained_name in trained_dict2:
                if elem in trained_dict2[trained_name]:
                    B += 1
                else:
                    D += 1
            files_dict[files_name][elem]['chi'] = float((N*(A*D-C*B)^2) / ((A+C)*(B+D)*(A+B)*(C+D)))
        # print "文档“" + file_name + "”已执行卡方检测算法!"

def MI(files_dict, trained_dict1, trained_dict2):
    #执行互信息算法
    for files_name in files_dict:
        for elem in files_dict[files_name]:
            pt = pc = ptc = 0   #
            train1_count = train2_count = 0 #分别计算训练文档中包含的文档数目
            for trained_name in trained_dict1:
                train1_count += 1
                if elem in trained_dict1[trained_name]:
                    ptc += 1
                    pt += 1
            for trained_name in trained_dict2:
                train2_count += 1
                if elem in trained_dict2[trained_name]:
                    pt += 1
            ptc = ptc/(train1_count + train2_count)
            pt = pt/(train1_count + train2_count)
            pc = train1_count/(train1_count + train2_count)
            mi = math.log10(ptc/(pt + pc))
            files_dict[files_name][elem]['mi'] = mi

def IG(files_dict, trained_dict1, trained_dict2):
    pc1, pc2, pt ,pT = 0, 0, 0, 0
    #pc1表示的是在c1类里包含特征项t的文档概率，pc2表示的是在c2类里包含特征项t的文档概率
    #pt表示的是待处理的文档集里出现特征t的文档的概率，pT表示的是待处理的文档集里没有出现特征t的文档的概率
    for files_name in files_dict:
        for elem in files_dict[files_name]:
            pc1, pc2, pt, pT = 0, 0, 0, 0   #计算每个特征MI值之前重置临时数据
            hc = 0
            hct = 0
            hcT = 0
            pt1 = pt2 = pc1 = pc2 = hc1 = hcT1 = hc2 = hcT2 = 0
            for files_name1 in files_dict:
                if elem in files_dict[files_name1]:
                    pt += 1
            for trained_name in trained_dict1:
                if elem in trained_dict1[trained_name]:
                    pc1 += 1
            for trained_name in trained_dict2:
                if elem in trained_dict2[trained_name]:
                    pc2 += 1
            pt = pt/len(files_dict)
            pT = 1 - pt
            pc1 = pc1/len(trained_dict1)
            pc2 = pc2 / len(trained_dict2)
            if pt == 0:
                if pc1 == 0:
                    hc1 = 0
                    hcT1 = 0
                else:
                    hc1 = pc1 * math.log10(pc1)
                    hcT1 = (pc1 / pT) * math.log10(pc1 / pT)
                if pc2 == 0:
                    hc2 = 0
                    hcT2 = 0
                else:
                    hc2 = pc2 * math.log10(pc2)
                    hcT2 = (pc2 / pT) * math.log10(pc2 / pT)
                hc = -(hc1 + hc2)
                hct = 0
                hcT = pT*(hcT1+hcT2)
            elif pt == 1:
                if pc1 == 0:
                    hc1 = 0
                    hct1 = 0
                else:
                    hc1 = pc1 * math.log10(pc1)
                    hct1 = (pc1 / pt) * math.log10(pc1 / pt)
                if pc2 == 0:
                    hc2 = 0
                    hct2 = 0
                    hcT2 = 0
                else:
                    hc2 = pc2 * math.log10(pc2)
                    hct2 = (pc2 / pt) * math.log10(pc2 / pt)
                hc = -(hc1 + hc2)
                hct = pt * (hct1 + hct2)
                hcT = 0
            else:
                if pc1 == 0:
                    hc1 = 0
                    hct1 = 0
                    hcT1 = 0
                else:
                    hc1 = pc1 * math.log10(pc1)
                    hct1 = (pc1 / pt) * math.log10(pc1 / pt)
                    hcT1 = (pc1 / pT) * math.log10(pc1 / pT)
                if pc2 == 0:
                    hc2 = 0
                    hct2 = 0
                    hcT2 = 0
                else:
                    hc2 = pc2 * math.log10(pc2)
                    hct2 = (pc2 / pt) * math.log10(pc2 / pt)
                    hcT2 = (pc2 / pT) * math.log10(pc2 / pT)
                hc = -(hc1 + hc2)
                hct = pt * (hct1 + hct2)
                hcT = pT * (hcT1 + hcT2)
            ig = hc + hct + hcT
            print ' ig: ' + str(ig) + ' hc' + str(hc) + ' hct' + str(hct)
            files_dict[files_name][elem]['ig'] = ig


if __name__ == "__main__":
    #main
    files_dict = dict()
    trained_dict1 = dict()
    trained_dict2 = dict()
    files_path = raw_input(u"请输入待处理文件路径：\n")
    files_dict = read_file(files_path)
    trained_path1 = raw_input(u"请输入该类文档的训练文档路径：\n")
    trained_dict1 = read_file(trained_path1)
    trained_path2 = raw_input(u"请输入非该类文档的训练文档路径：\n")
    trained_dict2 = read_file(trained_path2)
    chara_count = raw_input("请输入需要的特征向量的数目：\n")
    m = re.match(r'\D', chara_count) #和下面的m一起，检查输入的正确性
    while m != None or len(chara_count) <= 0:
        chara_count = raw_input("必须为整数，请重新输入：\n")
        m = re.match(r'\D+|\d+\D+', chara_count)
    print "正在执行算法。。。"
    vsmprocess(files_dict)
    vsmprocess(trained_dict1)
    vsmprocess(trained_dict2)
    tfidf(files_dict)
    CHI(files_dict, trained_dict1, trained_dict2)
    MI(files_dict, trained_dict1, trained_dict2)
    IG(files_dict, trained_dict1, trained_dict2)
    printing(files_dict, int(chara_count))



