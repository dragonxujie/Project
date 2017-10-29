from crawler import Crawler
from pymongo import MongoClient
from selenium import webdriver
import os
from random import randint
import time

# user name and password
mini_time = 5
max_time = 15
crawl_time = 2*3600
# connect mongodb
# ABN database
client_read = MongoClient()
abr_db = client_read.Melbourne_ABR
coll_read = abr_db.city_area
# my database
client_write = MongoClient()
comp_detail = client_write.CompanyDetailTest
coll_write = comp_detail.company_employee
# account database
linkedin_client = MongoClient()
linkedin_db = linkedin_client.email_account
linkedin_coll = linkedin_db.linkedin_account

amount = linkedin_coll.count()
used = 0
while amount > 0:
    used += 1
    acc = linkedin_coll.find()[0]
    print "This is account: " + str(used) + " "+acc["email"]
    # setup web driver
    driver = webdriver.PhantomJS(desired_capabilities={'page.zoomFactor':0.25})
    driver.set_window_size('1080','1920')

    # new crawler object
    email = acc['email']
    password = acc['password']
    cr = Crawler()
    login_driver = cr.login(driver,email,password)
    try:
        os.mkdir('company')
    except OSError:
        print 'folder has existed'

    comp_count = 0
    history = 0
    # the time start from the first company that this account find
    current_time = time.time()
    for i in coll_read.find():
        if time.time() - current_time < crawl_time:
            comp_count += 1
            print 'This is the '+str(comp_count)+' company....'
            employee_quan = 0
            company = i['properties']['entity_organisation_name']
            address_one = i['properties']['bus_address_line_1']
            address_two = i['properties']['bus_address_line_2']
            category = i['properties']['category']
            abn = i['properties']['abn']
            postcode = i['properties']['bus_locn_postcode']
            description = i['properties']['anzsic_description']
            division = i['properties']['division']
            division_code = i['properties']['division_code']
            lat =  i['properties']['geocode_lat']
            long = i['properties']['geocode_lon']
            comp_detail = {'comp_name':company, 'add1':address_one, 'add2':address_two, 'category':category, 'ABN':abn,
                           'postcode':postcode,'description':description, 'division':division, 'division_code':division_code,
                           'latitude':lat, 'longtitude':long,'employee_quantity':employee_quan}

            if company is not None:
                employee_quan, exist = cr.crawler_seper(login_driver,company)
                if exist == False:
                    history += 1
                    comp_detail['employee_quantity'] = employee_quan
                    coll_write.insert_one(comp_detail)
                    sleep_time = randint(mini_time,max_time)
                    print '***************************************************'
                    print '******This account has crawl '+str(history)+' companies'
                    print '******Sleeping for '+str(sleep_time)+' seconds'
                    print '***************************************************'
                    time.sleep(sleep_time)
                else:
                    print 'Company data has existed in database'
            else:
                print 'Cannot find company name...'
        else:
            break
    # delete the used account when the time reach limitation or all the companies have been crawled
    linkedin_coll.remove(acc)
    amount = linkedin_coll.count()
