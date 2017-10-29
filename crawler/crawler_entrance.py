from crawler import Crawler
from pymongo import MongoClient
from selenium import webdriver
import os
from random import randint
import time
import socket

# set time slots
MINI_TIME = 5
MAX_TIME = 15
CRAWL_TIME = 4*3600

class Crawler_entrance():

    def __init__(self):
        # connect mongodb
        # ABN
        # read in database
        self.client_read = MongoClient('localhost',27017)
        self.abr_db = self.client_read.Melbourne_ABR
        self.coll_read = self.abr_db.city_area
        # write in database
        self.client_write = MongoClient('localhost',27017)
        self.comp_detail = self.client_write.CompanyDetailTest
        self.coll_write = self.comp_detail.company_employee
        # account database
        self.linkedin_client = MongoClient('localhost',27017)
        self.linkedin_db = self.linkedin_client.email_account
        self.linkedin_coll = self.linkedin_db.linkedin_account
        self.amount = self.linkedin_coll.count()
        # cache
        self.vm = MongoClient('localhost',27017)
        self.cache_db = self.vm.cache
        self.cache_col = self.cache_db.document_cache
        # email
        self.email = ''
        # password
        self.password = ''
        # driver
        self.driver = webdriver.PhantomJS(desired_capabilities={'page.zoomFactor': 0.25})
        self.driver.set_window_size('1080', '1920')
        # crawling amount
        self.overall_comp_count = 1
        self.acc_comp_count = 0
        # current time
        self.current_time = 0

    def crawl_by_account(self):
        try:
            os.mkdir('/mnt/company')
        except OSError:
            print 'folder has existed'
        if self.linkedin_coll.count() > 0:
            acc = self.linkedin_coll.find()[0]
            self.linkedin_coll.remove(acc)
            print "This is account: " + acc["email"]
            # updated new crawler object
            self.email = acc['email']
            self.password = acc['password']
            cr = Crawler()
            login_driver = cr.login(self.driver, self.email, self.password)
            self.current_time = time.time()
            cache_document = []
            for i in self.coll_read.find():
                # crawl the company missed by last account
                if cache_document != []:
                    self.crawl_comp(cache_document[0],login_driver,cr)

                if time.time() - self.current_time <= CRAWL_TIME:
                    self.crawl_comp(i,login_driver,cr)
                else:
                    amount = self.linkedin_coll.count()
                    if amount > 0 :
                        acc = self.linkedin_coll.find()[0]
                        print "This is account: " + acc["email"]
                        # updated new crawler object
                        self.email = acc['email']
                        self.password = acc['password']
                        cr = Crawler()
                        # update the driver
                        login_driver = cr.login(self.driver, self.email, self.password)
                        # update the current time
                        self.current_time = time.time()
                        # set 0 for new account
                        self.acc_comp_count = 0
                        # add the neglected company into a cache
                        cache_document.append(i)
                    else:
                        break
        else:
            print '!!!!!Accounts have used up, please add new account!!!!!'

    # the main function for crawling the data
    def crawl_comp(self,comp,login_driver,crawler_object):
        company = comp['properties']['entity_organisation_name']
        if company is None:
            print 'This is the' + str(self.overall_comp_count) + 'th company'
            print '#####Did not find company name#####'
            self.overall_comp_count += 1
        else:
            out_put_db_exist = self.coll_write.find({'comp_name': company}).count()
            cache_exist = self.cache_col.find({'_id': company}).count()
            # check the name if existed in the cache db or output db
            if out_put_db_exist > 0 or cache_exist > 0:
                print 'This is the' + str(self.overall_comp_count) + 'th company'
                print '*****' + company + ' has existed*****'
                self.overall_comp_count += 1
            else:
                cache = {'_id': company, 'machine': socket.gethostname(), 'time': time.strftime("%c"),'acc':self.email,'pass':self.password}
                self.cache_col.insert_one(cache)
                employee_quan = 0
                address_one = comp['properties']['bus_address_line_1']
                address_two = comp['properties']['bus_address_line_2']
                category = comp['properties']['category']
                abn = comp['properties']['abn']
                postcode = comp['properties']['bus_locn_postcode']
                description = comp['properties']['anzsic_description']
                division = comp['properties']['division']
                division_code = comp['properties']['division_code']
                lat = comp['properties']['geocode_lat']
                long = comp['properties']['geocode_lon']
                comp_detail = {'comp_name': company, 'add1': address_one, 'add2': address_two, 'category': category,
                               'ABN': abn,
                               'postcode': postcode, 'description': description, 'division': division,
                               'division_code': division_code,
                               'latitude': lat, 'longtitude': long, 'employee_quantity': employee_quan}
                employee_quan, exist = crawler_object.crawler_seper(login_driver, company)

                if exist == False:
                    self.acc_comp_count += 1
                    comp_detail['employee_quantity'] = employee_quan
                    self.coll_write.insert_one(comp_detail)
                    sleep_time = randint(MINI_TIME, MAX_TIME)
                    time.sleep(sleep_time)
                else:
                    print 'Company data has existed in database'


if __name__ == '__main__':
    crl = Crawler_entrance()
    crl.crawl_by_account()