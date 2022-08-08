# %%
# -*- coding: UTF-8 -*-
import pptx
from pptx import Presentation

# %%
prs=Presentation('raw.pptx')
slides=prs.slides
len(slides)


# %%
import datetime

# %%
paragraph_list=[]
chart_list=[]
table_list=[]
for slide in slides:
    #print('slide id:'+str(slide.slide_id))
    for shape in slide.shapes:
        
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
               
                paragraph_list.append(para)
        elif shape.has_chart:
            chart_list.append(shape.chart)
        elif shape.has_table:
            #r,c=len(shape.table.rows),len(shape.table.columns)
            #content=shape.table.rows[1].cells[0].text
            table_list.append(shape.table)

# %%
#chart=chart_list[0]



# %%
#chart.chart_title.text_frame.text

# %%
date=datetime.date.today().__format__('%Y-%m-%d')

# %%

for table in table_list:
            row,col=len(table.rows),len(table.columns)
            content=table.rows[1].cells[0].text
            for  r in range(row):
                for c in range(col):
                    #print(table.cell(r,c).text)
                    pass

# %%
d = {
    'code':
    '600123.SH',
    'name':
    '兰花科创',
    'author':
    'ppt xiaodi',
    'date':
    date,
    'summary':
    '兰花科创是一家以炼焦煤（无烟煤）的开采、销售为主，尿素，二甲醚等化肥，化工产品为辅的综合公司。',
    'industry':
    '所属产业链：煤炭',
    'raw':
    '上游原材料：甲醇/纯苯/液氨/液氮/二氧化碳',
    'downstream':
    '下游应用：农作物/复合肥',
    'product': [{
        'product_name': '炼焦煤',
        'product_summary': '据公司煤矿矿种披露，公司售卖无烟煤、动力煤、焦煤。',
        'sale_ratio': '58.14%',
        'gross_profit': '58.2%',
        'sale_value': '30.60 亿人民币',
        'sale_pattern': ' 公司煤炭销售以化工煤（无烟煤）为主，自销',
        'product_pattern': '自产',
        'more_info':'现有各类矿井 14 个，年设计能力 2020 万吨。其中生产矿井 8 个(新建玉溪煤矿 240 万吨/年矿 井于 2021 年 1 月取得安全生产许可证，2021 年 3 月完成生产要素公告，正式转入生产矿井，望云、伯方、唐安、大阳、宝欣、口前、永胜)，年煤炭生产能力 1200 万吨;参股 41%的亚美大宁年生产能力 400 万吨;在建资源整合 矿井 5 个，设计年生产能力 420 万吨。'


    }, {
        'product_name': '尿素',
        'product_summary': '氮肥',
        'sale_ratio': '25.29%',
        'gross_profit': '27%',
        'sale_value': '9.05 亿人民币',
        'sale_pattern': '-',
        'product_pattern': '-',
        'more_info':'现有尿素生产企业 3 个(含煤化工公司、田悦分公司、化工分公司;阳化分公司已整体关停)，年尿素产能约 100 万吨。'
    }]
}


# %%
import copy
from pptx.table import _Cell
table=table_list[0]
copy_idx=1
insert_idx=2
new_row = copy.deepcopy(table._tbl.tr_lst[copy_idx])
for tc in new_row.tc_lst:
    cell = _Cell(tc, new_row.tc_lst)
    cell.text = ''
table._tbl.append(new_row)
len(table.rows)

# %%

for table in table_list:
            row,col=len(table.rows),len(table.columns)
            content=table.rows[1].cells[0].text
            for  r in range(row):
                for c in range(col):
                    if 'product_name' in table.cell(r,c).text:
                        table.cell(r,c).text=d['product'][0]['product_name']
                    elif 'product_summary' in table.cell(r,c).text:
                        table.cell(r,c).text=d['product'][0]['product_summary']
                    elif 'sale_ratio' in table.cell(r,c).text:
                        table.cell(r,c).text=d['product'][0]['sale_ratio']
                    elif 'gross_profit' in table.cell(r,c).text:
                        table.cell(r,c).text=d['product'][0]['gross_profit']
                    elif 'sale_value' in table.cell(r,c).text:
                        table.cell(r,c).text=d['product'][0]['sale_value']
                    elif 'sale_pattern' in table.cell(r,c).text:
                        table.cell(r,c).text=d['product'][0]['sale_pattern']
                    elif 'product_pattern' in table.cell(r,c).text:
                        table.cell(r,c).text=d['product'][0]['product_pattern']
                    elif 'growth' in table.cell(r,c).text:
                        table.cell(r,c).text='not found!'
                    elif r==2:
                        if c==0:
                            table.cell(r,c).text=d['product'][1]['product_name']
                        elif c==1:
                            table.cell(r,c).text='not found!'
                        elif c==2:
                            table.cell(r,c).text=d['product'][1]['product_summary']  
                        elif c==3:
                            table.cell(r,c).text=d['product'][1]['sale_ratio']
                        elif c==4:
                            table.cell(r,c).text=d['product'][1]['gross_profit']
                        elif c==5:
                            table.cell(r,c).text=d['product'][1]['sale_value']
                        elif c==6:
                            table.cell(r,c).text=d['product'][1]['sale_pattern']
                        elif c==7:
                            table.cell(r,c).text=d['product'][1]['product_pattern']
                    '''else:
                        table.cell(r,c).text='not Found!' '''

# %%
for para in paragraph_list:
    if 'name code' in para.text:
        para.text=d['code']+'-'+d['name']
    elif 'Author' in para.text:
        para.text=d['author']
    elif 'Date' in para.text:
        para.text=d['date']
    elif 'summary' in para.text:
        para.text=d['summary']
    elif 'industry' in para.text:
        para.text=d['industry']
    elif 'raw_material' in para.text:
        para.text=d['raw']
        #print('raw')
    elif 'downstream' in para.text:
        para.text=d['downstream']
    '''else:
        para.text='not found! '''
    


# %%
shape=slides[4].shapes[2]
for shape in slides[4].shapes:
    if shape.has_text_frame:
        if 'image' in shape.text:
            shape.text=''
            #print('delete')

# %%
from pptx import Presentation
from pptx.chart.data import ChartData,XyChartData,BubbleChartData,CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE,XL_LABEL_POSITION,XL_LEGEND_POSITION
from pptx.util import Inches
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE,MSO_VERTICAL_ANCHOR,PP_PARAGRAPH_ALIGNMENT,PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.shapes import MSO_SHAPE_TYPE,MSO_SHAPE
from pptx.util import Pt,Cm
slide=slides[4]
left = top = Cm(3)
pic = slide.shapes.add_picture('industry.jpg',left,top,height=Cm(15))




# %%
new_slide1=slides.add_slide(slides[4].slide_layout)
new_slide2=slides.add_slide(slides[4].slide_layout)

# %%
new_slide1.shapes[0].text='产品产能信息1-'+d['product'][0]['product_name']
new_slide1.shapes[1].text=d['product'][0]['more_info']
new_slide2.shapes[0].text='产品产能信息2-'+d['product'][1]['product_name']
new_slide2.shapes[1].text=d['product'][1]['more_info']

# %%
def move_slide(presentation, old_index, new_index):
        xml_slides = presentation.slides._sldIdLst  # pylint: disable=W0212
        slides = list(xml_slides)
        xml_slides.remove(slides[old_index])
        xml_slides.insert(new_index, slides[old_index])

def delete_slide(presentation,  index):
        xml_slides = presentation.slides._sldIdLst  # pylint: disable=W0212
        slides = list(xml_slides)
        xml_slides.remove(slides[index])

# %%
move_slide(prs,7,6)
move_slide(prs,8,7)

# %%
'''for slide in slides:
    print(slide.slide_id)'''

file_name=d['code']+' '+d['name']+' '+d['date']
# %%
prs.save('E:\wangzhilin\QuantumGalaxy\opt\yanbaoxiaodi\\%s.pptx'%file_name)
print('Finished processing raw ppt to file:　%s'%file_name)

