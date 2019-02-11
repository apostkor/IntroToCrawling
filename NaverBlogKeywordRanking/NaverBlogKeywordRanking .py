import time
import requests
from bs4 import BeautifulSoup
import lxml
import pandas as pd
import numpy as np
from pandas import ExcelWriter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

def Naver_Blog_Keyword_ranking(keyword):
    naver_id_list = []
    me_id_list = []



    # 페이지가 1, 11, 21 식으로 10씩 더해줘야함
    for page in range(1, 11, 10):
        url = 'https://search.naver.com/search.naver?date_from=&date_option=0&date_to=&dup_remove=1&nso=&post_blogurl=&post_blogurl_without=&query={}&sm=tab_pge&srchby=all&st=sim&where=post&start={}'.format(keyword, page)
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')

        for title in soup.findAll("div", {"class": "thumb thumb-rollover"}):
            title = str(title)
        
            if('blog.naver' in title):
                url_first = title.find('href=')
                url_last = title.find('?Redirect')
                title = title[url_first+6:url_last]
            
                id_index = title.find('com/')
                naver_id = title[id_index+4:]
                # 중복처리
                if(naver_id in naver_id_list):
                    continue
                
                naver_id_list.append(naver_id)
            
            
            if('blog.me' in title):
                url_first = title.find('https://')
                url_last = title.find('.blog.me')
                title = title[url_first+8:url_last]
            
            
                # 중복처리
                if(title in naver_id_list):
                    continue
                
                naver_id_list.append(title)
    
    print('페이지 추출 완료')
    print(len(naver_id_list))



    NaverID = []
    TodayVisit = []
    TotalVisit = []
    Neighbor = []

    driver = webdriver.Chrome('/home/apostcto/ITDA/chromedriver')

    
    for naver_url in naver_id_list:
    
        url = 'https://m.blog.naver.com/{}'.format(naver_url)

        driver.get(url)
    
        text = driver.find_element_by_class_name('count')
        text2 = driver.find_element_by_class_name('count_buddy')
    
        today = text.text
        today_last_index = today.find(' ·')
    
        today = today[3:today_last_index]
    
    
    
        total = text.text
        total_last_index = total.find('전체')
        total = total[total_last_index+3:]
    
        neighbor = text2.text
        neighbor_last_index = neighbor.find('명')
        neighbor = neighbor[:neighbor_last_index]
    
        NaverID.append(naver_url)
        TodayVisit.append(today)
        TotalVisit.append(total)
        Neighbor.append(neighbor) 
    
        time.sleep(0.5)

        
    temp_id = NaverID
    temp_today = TodayVisit
    temp_visit = TotalVisit
    temp_neighbor = Neighbor

    temp_today_total = []
    temp_visit_total = []
    temp_neighbor_total = []
    final_today_total = []
    final_visit_total = []
    final_neighbor_total = []

    for today in temp_today:
        if(len(today)==0):
            today = '0'
            temp_today_total.append(today)
        else:
            temp_today_total.append(today)
        
    for visit in temp_visit:
        if(len(visit)==0):
            visit = '0'
            temp_visit_total.append(visit)
        else:
            temp_visit_total.append(visit)
        
    for neighbor in temp_neighbor:
        if(len(neighbor)==0):
            neighbor = '0'
            temp_neighbor_total.append(neighbor)
        else:
            temp_neighbor_total.append(neighbor)

    for today in temp_today_total:
        if(',' in today):
            today = int(today.replace(',',''))
            final_today_total.append(today)
        else:
            final_today_total.append(int(today))
        
    for visit in temp_visit_total:
        if(',' in visit):
            visit = int(visit.replace(',',''))
            final_visit_total.append(visit)
        else:
            final_visit_total.append(int(visit))
        
    for neighbor in temp_neighbor_total:
        if(',' in neighbor):
            neighbor = int(neighbor.replace(',',''))
            final_neighbor_total.append(neighbor)
        else:
            final_neighbor_total.append(int(neighbor))

        

    keyword_dataframe = pd.DataFrame({'네이버ID':NaverID,
                                      '누적 방문자 수':final_visit_total,
                                      '오늘의 방문자 수':final_today_total,
                                      '연결된 이웃 수':final_neighbor_total})

    keyword_dataframe = keyword_dataframe.sort_values('누적 방문자 수', ascending=False)
    keyword_dataframe.index = np.arange(1,len(keyword_dataframe)+1)
    

    
    keyword_dataframe.to_excel("Naver_Blog_Ranking.xlsx")
    print(keyword_dataframe.head(20))


if __name__ == "__main__":
    
    keyword = input('블로그 검색 키워드를 입력하세요 ')
    Naver_Blog_Keyword_ranking(keyword)