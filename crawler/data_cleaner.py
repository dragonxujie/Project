'''
created by Chi Zhang
date: 25/7/2017
functions:
1. clean the data file from 4 vms
2. generate the class for pipeline using
3. save in mongodb
'''
from bs4 import BeautifulSoup
import os

class DataCleaner():

    #manual_clean-->read metadata from a list of company and clean data for these companies
    #Using for a bunch of raw data
    def manual_clean(self, path):
        if os.path.isdir(path):
            for company in os.listdir(path):
                inner = os.listdir(path + company)
                emp_quan = 0
                if len(inner) == 0:
                    # print 'This company is empty!!!'
                    pass
                else:
                    print 'This company has:' + str(len(inner)) + ' pages'
                    count = 1
                    for page in os.listdir(path + company):
                        try:
                            html = open(path + company + '/' + page)
                            legal, quan = self.par_data(html, count,company)
                            if legal:
                                emp_quan += quan
                                count += 1
                            #!!currently, give '' to no legal page company. will be improved
                            else:
                                emp_quan += quan
                                count += 1

                        except IOError:
                            print 'Failling to open file'

                    print company + ' has: ' + str(emp_quan) + 'employees.'
                    return emp_quan

        # elif os.path.isfile(path):
        #     html = open(path)
        #     emp_quan, comp = self.par_data(html,1)
        #     return emp_quan
        else:
            print 'The path: '+path+' is not correct.'

    #auto_clean-->read metadata from one company and clean data for just one company
    #Using for one company
    def auto_clean(self, path, comp):
        count = 1
        emp_quan = 0
        for page in os.listdir(path):
            try:
                html = open(path + page)
                legal, quan = self.par_data(html, count,comp)
                if legal:
                    emp_quan += quan
                    count += 1
                # !!currently, give '' to no legal page company. will be improved
                else:
                    emp_quan += quan
                    count += 1

            except IOError:
                print 'Failling to open file'

        print comp + ' has: ' + str(emp_quan) + 'employees.'
        return emp_quan

    #1. parsing data, easy cleaning. Just matching the location
    def par_data(self, source, number, comp):
        print 'parsing the '+str(number) +'...'
        soup = BeautifulSoup(source,'html.parser')
        title = soup.title.text
        if title.rstrip() == 'LinkedIn':
            # print "Illegal page"
            return False, 0
        else:
            dict = {comp: 0}
            locations = soup.find_all('p','subline-level-2 Sans-13px-black-55% search-result__truncate')
            for loc in locations:
                loc = loc.text.split()
                if loc == ['Melbourne,','Australia']:
                    dict[comp] += 1
            return True, dict[comp]


# path = 'ssh/res/'
# dc = DataCleaner()
# dc.rmff(path)

