import pdftotext
import re
import regex
import numpy as np
from PyPDF2 import PdfFileWriter, PdfFileReader

def complete_patterns(file):
    with open(file, "rb") as f:
        pdf = pdftotext.PDF(f)
    
    '''
    handling ocr-requried
    '''
    if pdf[2] == '':
        #print(f'{file}: This file is protected, no way to parse except ocr!')
        return 'Ocr required'
    
    if ('\x10' in pdf[2]) or ('\u2e4e' in pdf[2]):
        #print(f'{file}: This file has severe codex issue, no way to parse except ocr!')
        return 'Ocr required'
    
    '''
    pattern 1 EX: 惠文高中
    '''
    try:
        output = []        
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])

        score_sheet = pdf[2]
        output += re.findall('姓名：(\w{2,3})',score_sheet)
        output.append(re.findall('^(.*?)\n',score_sheet)[0].replace(' ',''))
        for s in ['班排','群排','年排']:
            output += [round(eval(i),3)for i in re.findall('\d{1,3}/\d{2,3}',re.findall(s+'(.*?\n)',score_sheet)[0])]
        
        output.append('Complete pattern 1')
        return output
    
    except:
        pass
    
    '''
    pattern 2 ex: 臺北市立和平高級中學
    '''
    try:
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])


        score_sheet = pdf[2]
        output.append(re.findall('姓 名(.*?)班',score_sheet)[0].replace(' ',''))
        school = score_sheet[20:80].replace(' ','')
        if school == '':
            school = re.findall('目前成績(.*?)申請入學',score_sheet)[0].replace(' ','')
        output.append(school)
        try:
            L = re.split(' +',re.findall('\n學業成績(.*?)\n',score_sheet)[0])[1:]
        except:
            L = re.split(' +',re.findall('\n學業成績(.*?)\n',pdf[3])[0])[1:]
        try:
            PL = re.split(' +',re.findall('\n總人數(.*?)\n',score_sheet)[0])[1:]
        except:
            PL = re.split(' +',re.findall('\n總人數(.*?)\n',pdf[3])[0])[1:]
        RL = [L[i] for i in [1,2,3,8,9,10,15,16,17,22,23,24,29,30,31]]
        TL = [round(eval(i+'/'+j),3) for i,j in zip(RL,PL)]
        for i in range(3):
            output += TL[i::3]
            
        output.append('Complete pattern 2')
        return output    
        
    except:
        pass
    '''
    pattern 3 ex: 高雄市立中正高級中學
    '''
    try:
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])

        score_sheet = pdf[2]
        name = re.findall('姓名： (\w*?) ',score_sheet)
        if name:
            output += name
        else:
            output.append('XXX')
        output.append(re.findall('^(.*?)\n',score_sheet)[0].replace(' ',''))
        output += [round(eval(i),3) for i in re.findall('\d{1,3}/\d{2,3}',re.findall('班級人數 百分比(.*?)符號註記',score_sheet)[0])]
        output += [round(eval(i),3) for i in re.findall('\d{1,3}/\d{2,3}',re.findall('類組排名/類組人數(.*?)為不及格',score_sheet)[0])]
        output += [round(eval(i),3) for i in re.findall('\d{1,3}/\d{2,3}',re.findall('年級排名/年級人數(.*?)M 為重修',score_sheet)[0])]
        
        output.append('Complete pattern 3')
        return output 
    except:
        pass
    
            
    '''
    中文複製貼上會錯亂的pattern pattern4
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])

        output.append(re.findall('姓名：(.*?)\n',pdf[0])[0].replace(' ',''))
        output += re.findall('學校：(\w*?) ',score_sheet[0:100])
        try:
            for p in ['班','組','年級']:
                output += [round(float(i)/100,2) for i in re.findall('\d{1,3}\.\d{2,3}',re.findall(f'{p}百身比(.*){p}百身比',score_sheet)[0])]
            output.append('Complete pattern 4-1')
        except:
            for p in ['班','組','年級']:
                if p == '班':
                    output += [round(float(i)/100,2) for i in regex.findall(' (\d.*?) ',re.findall(f'{p}百分比(.*){p}百分比',score_sheet)[0],overlapped=True)[1::2]] 
                else:
                    output += [round(float(i)/100,2) for i in re.findall(' (\d.*?) ',re.findall(f'{p}百分比(.*){p}百分比',score_sheet)[0])] 
    
            output.append('Complete pattern 4')

        return output
    except:
        pass
    
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])

        output.append(re.findall('姓名：(.*?)\n',pdf[0])[0].replace(' ',''))
        output += ['XXX']
        output += [round(float(i)/100,2) for i in re.findall('\d{1,3}\.\d{2,3}',re.findall('班百身比(.*)班百身比',score_sheet)[0])[1::2]] 
        output += [round(float(i)/100,2) for i in re.findall(' (\d.*?) ',re.findall('組百身比(.*)組百身比',score_sheet)[0])] 

        for p in ['學級','學國','學揚']:
            try:
                output += [round(float(i)/100,2) for i in re.findall(' (\d.*?) ',re.findall(f'{p}百身比(.*){p}百身比',score_sheet)[0])]                 
                if len(output) != 19:
                    #print('Very special case...')
                    return 'skipped'
                output.append('Complete pattern 4-2')
                return output
            except:
                pass
    except:
        pass
    
    '''
    pattern 5
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])

        output += re.findall('姓名：(\w*?) ',score_sheet)
        output.append(re.findall('(.*?)學生',score_sheet)[0].replace(' ',''))
        if '類組(科別)排名' not in score_sheet:
            score_sheet = pdf[3]

        for p in ['班級','類組\(科別\)','年級']:
            output += [round(eval(i),2) for i in re.findall('\d{1,3}/\d{2,3}',re.findall(p+'排名(.*?)\n',score_sheet)[0])]
        
        output.append('Complete pattern 5')
        return output
    except:
        pass
    
    '''
    pattern 6
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])
        output += re.findall('姓名：(\w.*?)  ',score_sheet)
        output += ['XXX']
        temp = []
        for i in range(1,4):
            tl = re.split(' +',re.findall('學業平均(.*?)\n',score_sheet)[0].split('│')[i])
            if i == 3:
                temp += [tl[j] for j in [4,8,6]]
            else:
                temp += [tl[j] for j in [4,8,6,11,15,13]]
        for i in range(3):
            output += [round(float(i)/100,2) for i in temp[i::3]]
        
        output.append('Complete pattern 6')
        return output

    except:
        pass
    
    '''
    pattern 7
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])

        output += re.findall('姓名： (\w*?) ',score_sheet)
        output.append(re.findall('^(.*?)\n',score_sheet)[0].replace(' ',''))

        for p in ['班級','學程','年級']:
            output += [round(eval(i),2) for i in re.findall('\d{1,3}/\d{2,3}',re.findall(p+'排名(.*?)\n',score_sheet)[0])]
        
        output.append('Complete pattern 7')
        return output
    except:
        pass
    
    '''
    pattern 8 
    a format very similar to the dominant skipped ones, however, 
    it contains one additional line to show all required info
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])

        output.append(re.findall('姓名：(\w*?) ',score_sheet)[0])
        output.append(re.findall('^(.*?)\n',score_sheet)[0].replace(' ',''))
        for p in ['班','類','校']:
            output += [int(i)/100 for i in re.findall(' (\d\d) ',re.findall('各學期成績校排(.*?)\n',score_sheet)[0])]
        
        output.append('Complete pattern 8')
        return output
    except:
        pass

    
    '''
    Skipped files
    '''
    score_sheet = pdf[2]
    for p in ['個人成績單暨班級百分比對照表','個人成績單暨百分比對照表',
              '個人成績單暨類組百分比對照表','學生個人成績單暨百分比對',
             '個人成績單暨年級百分比對照表']:
        if p in score_sheet[0:120]:
            #print('This is a type of score sheet that doesnot contain enough info')
            return 'skipped'

    if (' 成績證明書\n' in score_sheet[0:120]) or \
    ('學生個人成績證明書\n' in score_sheet[0:120]) \
    or ('學 生 成 績 表' in score_sheet)\
    or ('成績一覽表' in score_sheet)\
    or ('學生個人成績單\n' in score_sheet[0:120]) \
    or ('成 績 報 告 單' in score_sheet[0:300]) \
    or ('歷年成績單-補考、重修後' in score_sheet[:300]) \
    or ('桃園市新興高級中等學校' in score_sheet[:300]):
        #print('This is a type of score sheet that doesnot contain enough info')
        return 'skipped'
    
    '''
    Nothing matched at all, return False
    '''
    #print('No pattern matched!')
    return False

def missing_patterns(file):
    
    with open(file, "rb") as f:
        pdf = pdftotext.PDF(f)
    
    '''
    skipped pattern 1
    either lacking of 年級百分 or 類組百分 for each semester
    (62 matched)
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])
        output += re.findall('姓名： (.*?) ',score_sheet)
        output.append(re.findall('^(.*?)\n',score_sheet)[0].replace(' ',''))
        # so dirty, just can't come up with a better way to handle these consecutive try
        for i in [2,3]:
            try:
                tl = re.split(' +',re.findall('學科平均(.*?)\n',pdf[i])[0])
                break
            except:
                try:
                    tl = re.split(' +',re.findall('智育成績(.*?)\n',pdf[i])[0])
                    break
                except:
                    pass
            
        if len(tl) == 38:
            ip = [4,10,16,22,28],[6,12,18,24,30]
        else:
            ip = [4,12,20,28,36],[7,15,23,31,39]

        if re.search('班 +班 +年 +年',score_sheet):
            output += [int(tl[i])/100 for i in ip[0]]
            output += [np.nan]*5
            output += [int(tl[i])/100 for i in ip[1]]

        elif re.search('班 +班 +類 +類',score_sheet):
            output += [int(tl[i])/100 for i in ip[0]]
            output += [int(tl[i])/100 for i in ip[1]]
            output += [np.nan]*5
        else:
            pass
        
        if len(output) == 19:
            output.append('Missing pattern 1')
            return output
    except:
        pass

    
    '''
    skipped pattern 2
    only have mean of 班,組, and 年百分, so I fill all values for each semester by mean
    There are 22 cases specify 班百分 in each semester
    ***so many different style met this pattern, must seperate them carefully
    (30 matched)
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])
        output += re.findall('姓名：(.*?) ',score_sheet)
        output += re.findall('^ +(.*?) ',score_sheet)
        # ... so many different style met this pattern, must seperate them carefully
        tl = re.split(' +',re.findall('學業平均(.*?)\n',score_sheet)[0])
        
        if len(tl) in [18,23,24]:
            if len(tl) == 24:
                k = -6
            else:
                k = -5
            if '班級排名百分' in score_sheet:
                ttl = re.findall(' \d\d',re.findall('班級排名百分(.*?)\n',score_sheet)[0])
                output += [float(i)/100 for i in ttl]
            else:
                output += [float(tl[k])/100]*5

            for p in [-3,-1]:
                output += [float(tl[p])/100]*5
            if len(output) == 19:
                output.append('Missing pattern 2')
                return output
            else:
                pass
    
    except:
        pass
    
    '''
    skipped pattern 3
    similar situation as p2
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])
        output += re.findall('姓名： (.*?) ',score_sheet)
        output.append(re.findall('^(.*?)\n',score_sheet)[0].replace(' ',''))
        try:
            tl = re.split(' +',re.findall('學科平均(.*?)\n',score_sheet)[0])
        except:
            tl = re.split(' +',re.findall('智育成績(.*?)\n',score_sheet)[0])
        if len(tl) == 21:
            for p in [-8,-5,-2]:
                output += [float(tl[p])/100]*5
            output.append('Missing pattern 3')
            return output
        else:
            pass
    
    except:
        pass
    '''
    skipped pattern 4
    10 matched
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])
        output += re.findall('姓名：(.*?) ',score_sheet)
        output += re.findall('^ +(.*?) +\w',score_sheet)
        output += [float(i)/100 for i in re.findall(' (\d\d)',re.findall('班百分比(.*?)\n',score_sheet)[0])]
        output += [np.nan]*5
        output += [float(i)/100 for i in re.findall(' (\d\d)',re.findall('年百分比(.*?)\n',score_sheet)[0])]
        if len(output) == 19:
            output.append('Missing pattern 4')
            return output
        else:
            pass
    except:
        pass
    
    '''
    pattern 5
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])
        output += re.findall('姓名：(.*?) ',score_sheet)
        output.append('XXXX')
        try:
            tl = re.split(' +',re.findall('學業平均(.*?)\n',score_sheet)[0])
        except:
            tl = re.split(' +',re.findall('學業平均(.*?)\n',pdf[3])[0])
        if '\x1b' in tl:
            tl.remove('\x1b')

        ip = [8,13,18,23,28],[10,15,20,25,30]

        if len(tl) == 31:
            output += [round(float(tl[i])/100,2) for i in ip[0]]
            output += [round(float(tl[i])/100,2) for i in ip[1]]
            output += [np.nan]*5
            output.append('Missing pattern 5')
            return output
    except:
        pass
    '''
    pattern 6
    9 matched
    '''
    try:
        score_sheet = pdf[2]
        output = []
        output.append(file.split('/')[1])
        output.append(file.split('/')[2])
        output += re.findall('姓名：(.*?) ',score_sheet)
        school = re.findall('^ +(.*?)\n',score_sheet)
        if '列印日期' in school[0]:
            raise AssertionError("text")
        output += school
        tl = re.split(' +',re.findall('學業成績(.*?)\n',score_sheet)[0])

        if len(tl) == 13:
            for j in [round(eval(i),2) for i in tl if '/' in i]:
                output += [j]*5
            output.append('Missing pattern 6')
            return output
    except:
        return False

def keep_score_sheet_only(infile, outfile):
    pages_to_keep = [2, 3] # page numbering starts from 0
    infile = PdfFileReader(infile, 'rb')
    output = PdfFileWriter()

    for i in pages_to_keep:
        p = infile.getPage(i)
        output.addPage(p)

    with open(outfile, 'wb') as f:
        output.write(f)
        
        
def additional_table_parser(table_txt):
    output = []
    name = re.findall('就讀學校：(.*?)\n',table_txt)[0].replace('_','')
    school = re.findall('姓名：(.*?)性',table_txt)[0].replace(' ','')
    output += [name,school]
    for i in ['一上','一下','二上','二下','三上']:
        tt = re.findall(f'高{i}(.*?)\n',table_txt)[0]
        tl = [round(eval(j),2) for j in re.findall('\d{1,3}/\d{2,3}',tt)]
        if len(tl) < 3:
            class_year = False
            for c in re.findall('( +)',tt):
                '''
                check how long the space is to determine the missing...
                so dirty...
                '''
                if len(c) > 10:
                    class_year = True
                    break
            if class_year:
                output += [tl[0],np.nan,tl[1]]
            elif len(tl) == 2:
                output += [tl[0],tl[1],np.nan]
            else:
                output += [tl[0],np.nan,np.nan]
        else:
            output += tl;

    output = [output[i] for i in [0,1,2,5,8,11,14,3,6,9,12,15,4,7,10,13,16]]
    tt = re.findall('擇最佳成績填入\)\n([\s\S]+)\n    一、您為何選擇本系就讀？',table_page)[0]
    if ('公民' in tt) or ('生涯' in tt):
        '''
        土木系與外文系
        '''
        tt = re.split(' +',tt.replace('\n',''))
        rest = [tt[2],float(tt[3]),tt[4],float(tt[5]),tt[1]+tt[-1],float(tt[-2])]
    else:
        tt = re.split(' +',tt.replace('\n',''))[1:]            
        rest = [float(tt[i]) if i%2 == 1 else tt[i] for i in range(len(tt))]
        
    while len(rest) < 6:
        '''
        生機系: len(tt) == 4 else 6
        '''
        rest.append(np.nan)
        
    output += rest
    output.insert(0,file.split('/')[1])
    output.insert(1,file.split('/')[2])
    return output