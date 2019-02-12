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



    # 페이지가 1, 11, 21 식으로 이어져있으니 10씩 더해줍니다
    # 1페이지가 1, 2페이지가 11, 3페이지가 21, 4페이지가 31 이런식으로
    for page in range(1, 1001, 10):
        url = 'https://search.naver.com/search.naver?date_from=&date_option=0&date_to=&dup_remove=1&nso=&post_blogurl=&post_blogurl_without=&query={}&sm=tab_pge&srchby=all&st=sim&where=post&start={}'.format(keyword, page)
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        
        # title 들어간 부분만 찾습니다
        for title in soup.findAll("div", {"class": "thumb thumb-rollover"}):
            title = str(title)
            
            # 티스토리, 다음 등등을 제외하고 naver 블로그만 추출
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
            
            # me도 네이버 블로그니 추가해줍니다
            if('blog.me' in title):
                url_first = title.find('https://')
                url_last = title.find('.blog.me')
                title = title[url_first+8:url_last]
            
            
                # 중복처리
                if(title in naver_id_list):
                    continue
                    
                # 네이버 아이디랑 me랑 형식이 동일하니 같은 list에 추가해줍니다
                naver_id_list.append(title)
    
    
    print('페이지 추출 완료')
    print('검색을 시작합니다')
    
    NaverID = []
    TodayVisit = []
    TotalVisit = []
    Neighbor = []
    
    # 크롤링에 사용할 웹드라이버를 설정해줍니다
    # Chrom()안에 chromdriver 파일 위치를 지정해줍니다
    driver = webdriver.Chrome('/home/apostcto/ITDA/chromedriver')

    # 위에서 크롤링한 아이디별로 블로그 탐색
    for naver_url in naver_id_list:
    
        url = 'https://m.blog.naver.com/{}'.format(naver_url)
        
        driver.get(url)
        text = driver.find_element_by_class_name('count')
        text2 = driver.find_element_by_class_name('count_buddy')
        
        # 오늘의 방문자수 크롤링
        # ·뒤에 존재하니 위치를 찾아서 슬라이싱
        today = text.text
        today_last_index = today.find(' ·')
        today = today[3:today_last_index]
    
    
        # 누적 방문자수 크롤링
        # '전체'를 찾아 슬라이싱
        total = text.text
        total_last_index = total.find('전체')
        total = total[total_last_index+3:]
        
        # 연결된 이웃 수 크롤링
        neighbor = text2.text
        neighbor_last_index = neighbor.find('명')
        neighbor = neighbor[:neighbor_last_index]
        
        # DataFrame을 만들기 위해 각각 리스트에 넣어줍니다
        NaverID.append(naver_url)
        TodayVisit.append(today)
        TotalVisit.append(total)
        Neighbor.append(neighbor) 
        
        # IP차단 방지를 위해 0.5초씩 sleep
        # 너무 많이 하면 밴당합니다
        time.sleep(0.5)

    today_total = []
    visit_total = []
    neighbor_total = []
    
    
    # 비어있는 칸은 0으로 채워줍니다
    # 각각 비어있는 칸이 다르기 때문에 일관성을 유지하기 위해
    # 크롤링 전에 전처리하지 않고 크롤링 후에 0으로 채워줍니다
    # 숫자들이 모두 숫자가 아니라 문자열로 구성되어있으니 int형식으로 모두 바꿔줍니다
    # 1000이상은 콤마가 붙어있으니 콤마를 제거해줘야 int로 바꿀수있습니다
    for today in TodayVisit:
        # 비어있는곳은 0으로 넣어줍니다
        if(len(today)==0):
            today = '0'
            today_total.append(int(today))
        if(',' in today):
            today = int(today.replace(',',''))
            today_total.append(today)
        else:
            today_total.append(int(today))
        
    for visit in TotalVisit:
        if(len(visit)==0):
            visit = '0'
            visit_total.append(int(visit))
        if(',' in visit):
            visit = int(visit.replace(',',''))
            visit_total.append(visit)
        else:
            visit_total.append(int(visit))
        
    for neighbor in Neighbor:
        if(len(neighbor)==0):
            neighbor = '0'
            neighbor_total.append(int(neighbor))
        if(',' in neighbor):
            neighbor = int(neighbor.replace(',',''))
            neighbor_total.append(neighbor)
        else:
            neighbor_total.append(int(neighbor))
    
    
    keyword_dataframe = pd.DataFrame({'네이버ID':NaverID,
                                      '누적 방문자 수':visit_total,
                                      '오늘의 방문자 수':today_total,
                                      '연결된 이웃 수':neighbor_total})
    # 누적 방문자 순으로 정렬합니다
    keyword_dataframe = keyword_dataframe.sort_values('누적 방문자 수', ascending=False)
    # index가 1부터 시작하게 설정
    keyword_dataframe.index = np.arange(1,len(keyword_dataframe)+1)
    

    # excel파일로 내보냅니다
    keyword_dataframe.to_excel("Naver_Blog_Ranking.xlsx")
    print(keyword_dataframe.head(20))


if __name__ == "__main__":
    
    keyword = input('블로그 검색 키워드를 입력하세요 ')
    Naver_Blog_Keyword_ranking(keyword)