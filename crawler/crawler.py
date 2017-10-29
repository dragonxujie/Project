from selenium.webdriver.common.keys import Keys
import time
import os
from bs4 import BeautifulSoup
import re
from data_cleaner import DataCleaner
from random import randint
import httplib

mini_time_login = 10
max_time_login = 25

mini_time_other = 10
max_time_other = 25

class Crawler():

    def login(self, driver, email, password):
        login_url = "https://www.linkedin.com/"
        print '*************Logging LinkedIn******************'
        driver.get(login_url)
        user_email = driver.find_element_by_class_name('login-email')
        user_email.clear()
        user_password = driver.find_element_by_class_name('login-password')
        user_password.clear()
        user_email.send_keys(email)
        user_password.send_keys(password)
        user_password.send_keys(Keys.RETURN)
        sleep_time = randint(mini_time_login,max_time_login)
        body = driver.page_source
        soup = BeautifulSoup(body, 'html.parser')
        title = soup.title.string
        print title
        time.sleep(sleep_time)
        print '****************Finished logged in*****************'
        return driver

    # this function will integrate the crawling, parsing as well as data saving
    def crawler_integ(self, path, company_name):
        dc = DataCleaner()
        emp_quan = dc.auto_clean(path,company_name)
        return emp_quan

    # this function only using for crawling data
    def crawler_seper(self, driver, company_name, save_root='/mnt/company/'):
        exist = False
        #do some modification
        company = company_name.lower()
        company = re.sub(r'\s+\(.+\)\s+', r' ', company)
        company = re.sub(r'pty ltd|pty. ltd.| pty limited| pty. limited| limited| ltd.', r'', company)
        company = re.sub(r'&', r'%26', company)
        search = company + ' melbourne'
        page = 1
        emp_quan = 0
        try:
            print company_name + ' folder is creating...'
            os.makedirs(save_root + company_name)
            # parsing 50 pages
            # testing phase just download 50 pages
            init_page = 50

            while page <= init_page:
                sleep_time = randint(mini_time_other,max_time_other)
                time.sleep(sleep_time)
                company_page = 'https://www.linkedin.com/search/results/people/?keywords=' + '%20'.join(
                    search.split(' ')) + '&origin=GLOBAL_SEARCH_HEADER&page=' + str(page)
                print company_page
                try:
                    driver.get(company_page)
                    time.sleep(6)
                    body = driver.page_source
                    soup = BeautifulSoup(body, 'html.parser')
                    title = soup.title.string
                    print soup.title.string
                    if title == 'LinkedIn':
                        print "**************ERROR**************"
                        break
                    h3Flag = False
                    results = []
                    if soup.find('h3') != None:
                        h3Flag = True
                        results = soup.find('h3').get_text()
                        results = results.split()
                    print results
                    # initializing the crawling page quantity
                    if page == 1 and h3Flag and results[0] == 'Showing':
                        # handle '1,000'etc.
                        quantity = results[1].split(',')
                        quantity = int(''.join(quantity))
                        init_page = quantity / 10 + 1
                        if init_page > 50:
                            init_page = 50
                            print 'special company!!!'
                    # ('h1') == None and soup.find('h1').get_text() == 'No results found.' mean no result
                    if soup.find('h1') == None and results != ['Showing', '0', 'results']:
                        print '***************loading page ' + str(page) + '**************'
                        with open(save_root + company_name + '/' + str(page) + '.html', 'w+') as f:
                            print '*************saving html***************'
                            f.write(body.encode('utf-8'))
                    elif results == ['Showing', '0', 'results'] or soup.find('h1').get_text() == 'No results found.':
                        break
                    page += 1

                except httplib.BadStatusLine:
                    pass
            path = save_root + company_name + '/'
            emp_quan = self.crawler_integ(path,company_name)

            return emp_quan, exist

        except OSError:
            exist = True
            print company_name + ' is existed!!!'
            return emp_quan, exist
