# !/usr/bin/env python
# -*- coding:utf-8 -*-

'The second part of edgar'

__author__='Walter Xiong'

import os
import shutil
import sys
import re

def main():

    for dirpath,dirnames,filenames in os.walk(os.path.abspath('.')):
        for filename in filenames:
            if os.path.splitext(filename)[1]=='.idx':
                if os.path.splitext(filename)[0] in dirnames:
                    original_dir=os.path.join(os.path.abspath('.'),os.path.splitext(filename)[0])

                    cleaned_dir = os.path.join(os.path.abspath('.'), os.path.splitext(filename)[0]+'_CLEANED')

                    if os.path.isdir(cleaned_dir):
                        shutil.rmtree(cleaned_dir)

                    if not os.path.isdir(cleaned_dir):
                        os.mkdir(cleaned_dir)

                    if not os.path.isdir(os.path.join(cleaned_dir, 'Manual_Clean')):
                        os.mkdir(os.path.join(cleaned_dir, 'Manual_Clean'))

                else:
                    sys.exit('Error: Original directory %r cannot be found'%os.path.splitext(filename)[0])

    traverse_folders(original_dir,cleaned_dir)

def traverse_folders(original_dir,cleaned_dir):

    original_folders=os.listdir(original_dir)

    count=0

    for f in original_folders:

        if f=='ConnError.txt' or f=='IOError.txt' or f=='Not_Found.txt' or f=='.DS_Store'or os.path.splitext(f)[1].lower()=='.swp':
            continue
        if os.path.splitext(f)[1].lower()=='.pdf' or os.path.splitext(f)[1].lower()=='.xml' or os.path.splitext(f)[1].lower()=='.paper':
            shutil.copy(os.path.join(original_dir,f),cleaned_dir)
            continue
        if os.path.splitext(f)[1].lower()=='.htm' or os.path.splitext(f)[1].lower()=='.txt':
            count=count+1
            print f
            print str(count)+ ' of '+str(len(original_folders))+' files\n'
            clean_htm_file(original_dir,cleaned_dir,f)
        else:
            print 'Processing '+f+' ...\n'

            if not os.path.isdir(os.path.join(cleaned_dir,f)):
                os.mkdir(os.path.join(cleaned_dir,f))

            traverse_folders(os.path.join(original_dir,f),os.path.join(cleaned_dir,f))

def clean_htm_file(original_dir,cleaned_dir,file):

    global tag_pattern
    global messy_pattern

    content=open(os.path.join(original_dir,file))
    content_lines=content.readlines()
    content.close()

    content_size=os.path.getsize(os.path.join(original_dir,file))

    cleaned_file=open(os.path.join(cleaned_dir,file),'w')

    table_buffer=[]
    tag_pattern = re.compile('<.*?>')
    messy_pattern = re.compile('&.*?;')

    if float(len(content_lines))/float(content_size)<=0.001:
        file_clean=True
        temp_lines=[]

        for c in content_lines:

            if not '</tr>' in c:
                temp_lines.append(c)
                continue

            index_list=[]

            k=c.lower().find('</tr>')

            while k>=0:
                index_list.append(k)
                k=c.lower().find('</tr>',k+1)

            if len(index_list)>=2:
                temp_lines.append(c[:index_list[0]]+'\n')
                for i in range(len(index_list)-1):
                    temp_lines.append(c[index_list[i]:index_list[i+1]]+'\n')
                temp_lines.append(c[index_list[i+1]:]+'\n')

        if float(len(temp_lines))/float(content_size)<0.0003:
            file_clean=False

        if file_clean==True:
            content_lines=temp_lines
        else:
            shutil.copy(os.path.join(original_dir,file),os.path.join(cleaned_dir,'Manual_Clean'))

    for c in content_lines:

        if len(table_buffer) != 0:

            if '</table>' in c.lower():
                table_buffer.append(c)
                table_check(table_buffer, cleaned_file)
                table_buffer = []
            else:
                table_buffer.append(c)
                continue
        else:
            if '<table' in c.lower():
                if '</table>' in c.lower():
                    table_buffer.append(c)
                    table_check(table_buffer, cleaned_file)
                    table_buffer = []
                else:
                    table_buffer.append(c)
                    continue
            else:
                text_replace(c, cleaned_file)

    if len(table_buffer)==0:
        cleaned_file.close()
    else:
        table_check(table_buffer, cleaned_file)
        cleaned_file.close()

def table_check(table_buffer,cleaned_file):

    buffer_len=0
    new_buffer_len=0
    new_table_buffer=[]

    for tb in table_buffer:

        buffer_len+=int(len(tb))

        tag_set=tag_pattern.findall(tb)
        messy_set=messy_pattern.findall(tb)

        for tag_subset in tag_set:
            tb=tb.replace(tag_subset,' ')

        for messy_subset in messy_set:
            tb = tb.replace(messy_subset, ' ')

        new_buffer_len+=int(len(tb))

        new_table_buffer.append(tb)

    if float(new_buffer_len)/float(buffer_len)>0.1:
        for tb in new_table_buffer:
            tb_splite=set(tb)
            if not len(tb_splite)==1 and not (len(tb_splite)==2 and ' ' in tb_splite):

                if not tb.endswith('\n'):
                    tb=tb+'\n'
                    cleaned_file.write(tb)
                cleaned_file.write(tb)
    else:
        for tb in new_table_buffer:
            if 'item' in tb.lower():
                if not tb.endswith('\n'):
                    tb=tb+'\n'
                    cleaned_file.write(tb)
                cleaned_file.write(tb)

def text_replace(text,cleaned_file):

    tag_set = tag_pattern.findall(text)
    messy_set = messy_pattern.findall(text)

    for tag_subset in tag_set:
        text = text.replace(tag_subset, ' ')

    for messy_subset in messy_set:
        text = text.replace(messy_subset, ' ')

    c_splite = set(text)

    if not len(c_splite) == 1 and not (len(c_splite) == 2 and ' ' in c_splite):

        if not text.endswith('\n'):
            text = text + '\n'
            cleaned_file.write(text)

        cleaned_file.write(text)


if __name__=='__main__':
    main()