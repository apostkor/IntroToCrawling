#본 모듈은 파이썬3 기반으로 작성되었습니다.
#실행전 필요한 모듈들과 Chromedriver를 꼭 설치해 주세요.
#물론 xlsx파일이나 csv파일을 실행하기 위해 엑셀또한 필요합니다 ;)
#필요한 모듈 리스트는 아래에서 참고하시기 바랍니다.
#터미널에서 Pip install <모듈명>이나 인터넷에서 설치방법을 검색하여 모듈을 설치해 주시기 바랍니다.

#먼저 모듈들을 불러옵니다.
import time
import requests
from bs4 import BeautifulSoup
import lxml
import pandas as pd
import numpy as np
from pandas import ExcelWriter
#네이버의 밴을 피하기 위한 모듈들입니다.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

#Naver와 Me의 아이디를 보관하기 위한 플레이스홀더입니다.
def Naver_Blog_Keyword_ranking(keyword):
    naver_id_list = []
    me_id_list = []



    # 블로그 페이지의 주소명의 페이지는 각 페이지별로 1, 11, 21 식으로 10씩 더해줘야 합니다.
    # range를 수정하여 추출하고자 하는 블로그의 수를 설정하여 주세요.
    # 현재 네이버가 제공하는 최대수치로 검색량이 설정되어 있습니다.
    for page in range(1, 1010, 10):
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
                # 중복되는 네이버 아이디를 제외합니다.
                if(naver_id in naver_id_list):
                    continue
                
                naver_id_list.append(naver_id)
            
            
            if('blog.me' in title):
                url_first = title.find('https://')
                url_last = title.find('.blog.me')
                title = title[url_first+8:url_last]
            
            
                # 중복되는 me 아이디를 처리합니다.
                if(title in naver_id_list):
                    continue
                
                naver_id_list.append(title)
    
    print('페이지 추출 완료')
    print(len(naver_id_list))


    #각각 ID, 오늘방문자수, 총방문자수, 이웃수를 저장하기 위한 플레이스홀더입니다.
    NaverID = []
    TodayVisit = []
    TotalVisit = []
    Neighbor = []
    
    #작업을 실행하기 위해 크롬드라이버를 실행합니다. ()부분에 경로는 사용자별로 상이할 수 있습니다.
    driver = webdriver.Chrome('/home/aposty/Downloads/chromedriver')

    #방문자수, 총방문자수, 이웃수를 좀더 쉽게 얻기 위해 네이버 아이디 리스트로 모바일 블로그 화면으로 들어갑니다.
    for naver_url in naver_id_list:
        #위에서 확보한 네이버 아이디를 {}안에 넣어 모바일 네이버블로그 화면으로 들어갑니다.
        url = 'https://m.blog.naver.com/{}'.format(naver_url)

        driver.get(url)
        #'count' 요소가 오늘/총방문자수의 텍스트
        text = driver.find_element_by_class_name('count')
        #'count_buddy'는 이웃수의 텍스트입니다. 각각 가져옵니다.
        text2 = driver.find_element_by_class_name('count_buddy')

        #'count'요소에서 text 리스트로 옮겨진 오늘방문자수와 총방문자수를 구분해 줍니다.
        today = text.text
        today_last_index = today.find(' ·')
        today = today[3:today_last_index]
    
    
        total = text.text
        total_last_index = total.find('전체')
        total = total[total_last_index+3:]
       
        neighbor = text2.text
        neighbor_last_index = neighbor.find('명')
        neighbor = neighbor[:neighbor_last_index]
        
        #위 작업을 자동화 하고 리스트에 추가합니다.
        NaverID.append(naver_url)
        TodayVisit.append(today)
        TotalVisit.append(total)
        Neighbor.append(neighbor) 
        
        #네이버의 밴을 피하기 위해 각 요청간 텀을 줍니다.
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
    
    #오늘방문자가 없는 경우 제외합니다.
    for today in temp_today:
        if(len(today)==0):
            today = '0'
            temp_today_total.append(today)
        else:
            temp_today_total.append(today)
    #총방문자가 없는 경우 리스트에서 제외합니다.    
    for visit in temp_visit:
        if(len(visit)==0):
            visit = '0'
            temp_visit_total.append(visit)
        else:
            temp_visit_total.append(visit)
    #이웃수가 없는 경우 리스트에서 제외합니다.    
    for neighbor in temp_neighbor:
        if(len(neighbor)==0):
            neighbor = '0'
            temp_neighbor_total.append(neighbor)
        else:
            temp_neighbor_total.append(neighbor)
    #내용의 전처리를 진행합니다.
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

        
    #각 리스트 별로 테이블로 변환할 키워드를 생성합니다.
    keyword_dataframe = pd.DataFrame({'네이버ID':NaverID,
                                      '연결된 이웃 수':final_neighbor_total,
                                      '오늘의 방문자 수':final_today_total,
                                      '누적 방문자 수':final_visit_total})
    #연결된 이웃 수로 정렬합니다.
    keyword_dataframe = keyword_dataframe.sort_values('누적 방문자 수', ascending=False)
    keyword_dataframe.index = np.arange(1,len(keyword_dataframe)+1)
    
    #CSV파일로 출력합니다.
    keyword_dataframe.to_csv('NaverBlogRanking_RESULT.csv', index=False)
    
    #xlsx로 생성할시 다음 코드를 활성화 해주세요.
    #이름을 지정하고 파일을 생성합니다. 
    #keyword_dataframe.to_excel("Naver_Blog_Ranking.xlsx")
    #print(keyword_dataframe.head(20))

#터미널에서 py파일을 실행시 출력될 메세지입니다.
if __name__ == "__main__":
    
    keyword = input('NAVER BLOG KEYWORD RANKER입니다! 블로그 검색 키워드를 입력하세요 ')
    Naver_Blog_Keyword_ranking(keyword)
