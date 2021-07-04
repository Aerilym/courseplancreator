from logging import debug
from os import dup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import selenium
import time
import sqlite3
from copy import copy

def remove_html(text):
    if not type(text) is str:
        raise TypeError("Only strings are allowed")
    try:
        while '<' in text:
            tagsnip = text[text.index('<'):text.index('>')+1]
            text = text.replace(tagsnip,'')
    except:
        pass
    return text

def scraper(units, implicit_wait_time = 5):
    data = []
    semdata = []
    namedata = []
    debug = [[]]

    # specify the url
    urlpage = 'https://handbook.monash.edu/current/units/'
    print(urlpage)
    print(units)
    num_units = len(units)
    counter = 0
    options = Options()
    options.headless = True
    overview, creditpoints, faculty, school, rawsemester, RAWprerequisites, RAWcorequisites, RAWprohibitions, RAWrecommendations, scaband, eftsl, studylevel, opentoexchange = [],[],[],[],[],[],[],[],[],[],[],[],[]

    # use firefox as a headless browser
    driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
    driver.implicitly_wait(implicit_wait_time)
    time_launch = time.perf_counter()
    for unit in units:
        if unit != '':
            time_unit = time.perf_counter()
            counter += 1
            attempts = 0
            while attempts < 2:
                restxt = ''
                try:
                    print('Scraping for ' + unit + ' (' + str(counter) + '/' + str(num_units) + ')')
                    # get web page
                    driver.get(urlpage + unit)
                    try:
                        checktimeout = driver.find_element_by_tag_name('h1')
                        if checktimeout.text == '403 Forbidden':
                            print('403 Forbidden DETECTED ... waiting for 30 seconds ...')
                            time.sleep(30)
                            driver.get(urlpage + unit)
                    except:
                        pass
                    # sleep for 5s
                    time.sleep(5)
                    # find elements by xpath
                    try:
                        #element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'Rules')))
                        result = driver.find_element_by_id('Rules')
                        restxt += result.get_attribute('innerHTML')
                    except:
                        pass
                    try:
                        #driver.find_elements_by_xpath('//*[@id="requisites_expandAll"]/button')[0].click()
                        #time.sleep(5)
                        #result = driver.find_element_by_id('7cc63ea11b9ee850f1eca68b274bcb88')
                        #element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'Requisites')))
                        result = driver.find_element_by_id('Requisites')
                        restxt += result.get_attribute('innerHTML')
                    except:
                        pass
                    finally:
                        try:
                            sems = driver.find_element_by_id('Offerings')
                            semstxt = sems.get_attribute('innerHTML')
                            semstxt = remove_html(semstxt)
                        except:
                            semstxt = 'NA'
                        unitname = driver.find_elements_by_tag_name('h2')[0].text
                        unitname = unitname[10:]
                        print(unitname)
                        if unitname == 'ound':
                            break
                        restxt = remove_html(restxt)
                        sidebar = driver.find_elements_by_class_name('css-z2gihx-AttrBody')
                        sidebarinfo = []
                        for res in sidebar:
                            sidebarinfo.append(res.text)
                        overviewscrape = driver.find_element_by_class_name('OverviewInner')
                        overviewres = overviewscrape.text
                        break
                except selenium.common.exceptions.StaleElementReferenceException:
                    driver.quit()
                    driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
                    driver.implicitly_wait(implicit_wait_time)
                    restxt = 'ERROR stale'
                    semstxt = 'ERROR stale'
                    unitname = 'ERROR stale'
                    attempts += 1
                except selenium.common.exceptions.NoSuchElementException:
                    driver.quit()
                    driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
                    driver.implicitly_wait(implicit_wait_time)
                    restxt = 'ERROR stale'
                    semstxt = 'ERROR stale'
                    unitname = 'ERROR stale'
                    attempts += 1
                except:
                    driver.quit()
                    driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
                    driver.implicitly_wait(implicit_wait_time)
                    restxt = 'ERROR stale'
                    semstxt = 'ERROR stale'
                    unitname = 'ERROR stale'
                    attempts += 1
            time_unit_done = time.perf_counter()
            print(f'Done in {time_unit_done-time_unit:0.2f}s')
            debug[0].append(time_unit_done-time_unit)
        else:
            restxt = ''
            semstxt = ''
            sidebarinfo = ['']*7
        data.append(restxt)
        semdata.append(semstxt)
        namedata.append(unitname)
        faculty.append(sidebarinfo[0])
        school.append(sidebarinfo[1])
        studylevel.append(sidebarinfo[2])
        scaband.append(sidebarinfo[3])
        eftsl.append(sidebarinfo[4])
        creditpoints.append(sidebarinfo[5])
        opentoexchange.append(sidebarinfo[6])
        overview.append(overviewres)

    # close driver 
    driver.quit()
    time_done = time.perf_counter()
    debug.append(time_done-time_launch)
    print(f'Scraping of {num_units} units was completed in {time_done-time_launch:0.2f}s')
    return [units,data,semdata,namedata,overview, creditpoints, faculty, school, scaband, eftsl, studylevel, opentoexchange]

def scraper_aos(name, aostype, implicit_wait_time = 5):
    data = []
    debug = [[]]
    # specify the url
    urlpage = 'https://handbook.monash.edu/search'
    print(urlpage)
    counter = 0
    options = Options()
    options.headless = True
    restxt = ''
    aostype = aostype.replace(' ','').upper()
    if aostype == 'MAJOR':
        aostype = 'Major'
    elif aostype == 'EXTENDED MAJOR':
        aostype = 'Extended Major'
    elif aostype == 'MINOR':
        aostype = 'Minor'

    # use firefox as a headless browser
    driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
    driver.implicitly_wait(implicit_wait_time)
    time_launch = time.perf_counter()
    if name != '' and aostype != '':
        time_unit = time.perf_counter()
        counter += 1
        attempts = 0
        #while attempts < 3:
        print('Scraping for ' + name + ' ' + aostype)
        driver.get(urlpage)
        searchfield = driver.find_element_by_id('miniSearchInput')
        searchfield.send_keys('physics')
        searchfield.send_keys(Keys.ENTER)
        AOSbutton = driver.find_element_by_id('react-tabs-4').click()
        time.sleep(3)
        selecteaos = driver.find_element_by_partial_link_text(aostype).click()
        result = driver.find_element_by_xpath('//*[@id="intro-container"]//h2').text
        #restxt = result.text()
        #restxt = remove_html(restxt)
        reqitems = driver.find_elements_by_xpath('//*[@id="curriculumStructure"]//h4')
        reqinners = driver.find_element_by_id('Requirements')
        reqitemheaders = []
        reqinners = reqinners.get_attribute('innerHTML')
        count = 0
        begin = 0
        while reqinners.count('#') < reqinners.count('<h4'):
            h4in = begin + reqinners[begin:].index('<h4')
            reqinners = reqinners[:h4in] + reqinners[h4in:].replace('<h4','#<h4',1)
            begin = h4in + 4

        reqinners = remove_html(reqinners)
        for item in reqitems:
            reqitemheaders.append(item.text)

        """except selenium.common.exceptions.StaleElementReferenceException:
            driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
            driver.implicitly_wait(implicit_wait_time)
            restxt = 'ERROR stale'
            attempts += 1
        except selenium.common.exceptions.NoSuchElementException:
            driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
            driver.implicitly_wait(implicit_wait_time)
            restxt = 'ERROR stale'
            attempts += 1
        except:
            driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
            driver.implicitly_wait(implicit_wait_time)
            restxt = 'ERROR stale'
            attempts += 1"""
        time_unit_done = time.perf_counter()
        print(f'Done in {time_unit_done-time_unit:0.2f}s')
        debug[0].append(time_unit_done-time_unit)
    else:
        restxt = ''
        semstxt = ''
    # close driver 
    driver.quit()
    time_done = time.perf_counter()
    debug.append(time_done-time_launch)
    print(f'Scraping of {name} {aostype} was completed in {time_done-time_launch:0.2f}s')
    return result, reqitemheaders, reqinners


def getallunits(implicit_wait_time=5):
    time_startscraper = time.perf_counter()
    debugdata = [['Scrape Time', 'Number of Units Scraped', 'UNITCODES'],[],[],[]]
    def table_exists(c, table_name): 
        c.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = '{}' '''.format(table_name)) 
        if c.fetchone()[0] == 1: 
            return True 
        return False
    def getsearchunits(driver, unitcodes, unitnames, unittypes, debugdata):
        results = driver.find_elements_by_class_name('result-item-title')
        for result in results:
            unitcodes.append(result.text[:7])
            unitnames.append(result.text[8:])
        resulttypes = driver.find_elements_by_class_name('result-item-content1')
        for resulttype in resulttypes:
            unittypes.append(resulttype.text)
        #remove duplicates
        allunitcodes = []
        duplicate_i = []
        debugdata[3].append(copy(unitcodes))
        for i in range(len(unitcodes)):
            if unitcodes[i] not in allunitcodes:
                allunitcodes.append(unitcodes[i])
            else:
                duplicate_i.insert(0,i)
        if duplicate_i != []:
            for i in duplicate_i:
                unitcodes.pop(i)
                unitnames.pop(i)
                unittypes.pop(i)
    def insert_unit(c, conn, unitcodes, unitnames, unittypes): 
        try:
            c.execute(''' INSERT INTO handbookunits (unitcodes, unitnames, unittypes) VALUES(?, ?, ?) ''', (unitcodes, unitnames, unittypes)) 
            conn.commit()
        except:
            print(f'Failed to add {unitcodes}')
            pass
    def insert_scraped_unitlists(c, conn, unitcodes, unitnames, unittypes):
        for i in range(len(unitcodes)):
            if unitcodes[i] != '':
                insert_unit(c, conn, str(unitcodes[i]), str(unitnames[i]), str(unittypes[i]))
    conn = sqlite3.connect('handbookunits.db') 
    c = conn.cursor()
    if not table_exists(c, 'handbookunits'): 
        c.execute(''' 
            CREATE TABLE handbookunits( 
                unitcodes TEXT PRIMARY KEY, 
                unitnames TEXT,
                unittypes TEXT
            ) 
        ''')
    # specify the url
    options = Options()
    options.headless = True
    page = 1
    urlpage = 'https://handbook.monash.edu/search'
    print(f'Establishing connection to {urlpage}...')
    driver = webdriver.Firefox(executable_path = 'Scraper\exes\geckodriver', options=options)
    print(f'Connected')
    driver.implicitly_wait(implicit_wait_time)
    driver.get(urlpage)
    driver.find_element_by_id('react-tabs-6').click()
    driver.find_element_by_xpath('//*[@id="react-tabs-7"]/div/div[2]/div[3]/div/div/div/div/div[2]/div/div/div/div').click()
    driver.find_element_by_xpath('//*[@id="rrs-undefined-menu"]/li[3]').click()
    unitcodes, unitnames, unittypes = [], [], []
    done = False
    while not done:
        time_newpage = time.perf_counter()
        print(f'Scraping Page {page}')
        previous_unitcodes = copy(unitcodes)
        unitcodes, unitnames, unittypes = [], [], []
        getsearchunits(driver, unitcodes, unitnames, unittypes, debugdata)
        insert_scraped_unitlists(c, conn, unitcodes, unitnames, unittypes)
        time_pagedone = time.perf_counter()-time_newpage
        debugdata[1].append(time_pagedone)
        debugdata[2].append(len(unitcodes))
        print(f'Page {page} completed in {time_pagedone:0.2f}s')
        page += 1
        driver.find_element_by_id('pagination-page-next').click()
        time.sleep(0.5)
        conn = sqlite3.connect('handbookunits.db')
        c = conn.cursor()
        if unitcodes == previous_unitcodes:
            print('Done')
            done = True
    try:
        c.execute("SELECT * FROM handbookunits")
        databasefields = len(c.fetchall())
        debugfields = sum(debugdata[2])
        averagepagetime = sum(debugdata[1])/len(debugdata[1])
    except:
        databasefields = 1
        debugfields = 1
    print(f'Scraping of units done in {(time.perf_counter()-time_startscraper)/60:0.2f}m (Average {averagepagetime:0.2f}s/page) | {debugfields} codes found | {databasefields} database entries entered | discrepancy = {(1-(databasefields/debugfields)):.2%} | {debugfields-databasefields} entries invalid')
    f = open('magescrapedebuglog.txt','w')
    f.write(str(debugdata))
    f.close()

#print(scraper_aos('physics', 'major'))

#print(scraper(['MTH2010']))
#print(scraper(['ATS1247']))
#units,data,semdata = scraper(['MTH2010', 'MTH2032', 'PHS2062', 'FIT1049', 'FIT2094', 'FIT2081', 'FIT2001', 'FIT3175', 'ASP3051', 'PHS3201', 'FIT2002', 'ASP3012', 'PHS3000', 'FIT3047', 'FIT3077', 'PHS3101', 'ASP3231', 'FIT3048', 'FIT2099', 'FIT3146', 'ASP3162'])
#print(semdata)
#print(scraper(['MTH2010', 'MTH2032', 'PHS2062', 'FIT1049', 'FIT2094', 'FIT2081', 'FIT2001', 'FIT3175', 'ASP3051', 'PHS3201', 'FIT2002', 'ASP3012', 'PHS3000', 'FIT3047', 'FIT3077', 'PHS3101', 'ASP3231', 'FIT3048', 'FIT2099', 'FIT3146', 'ASP3162']))
