import sqlite3
from unitdbhandle import insert_scraped
from Scraper.handbookscraper import scraper
from Scraper.scrapeparser import scrape_parse
from unitmanager import import_subjects
import time

def get_handbook_units():
    conn = sqlite3.connect(f'handbookunits.db')
    c = conn.cursor()
    c.execute("SELECT * FROM handbookunits")
    handbookunitsdb = c.fetchall()

    allunits = []
    for unit in handbookunitsdb:
        if unit[2] == 'UnitUndergraduate':
            allunits.append(unit[0])
    return allunits

def get_db_units():
    conn = sqlite3.connect(f'handbook.db')
    c = conn.cursor()
    c.execute("SELECT * FROM handbook")
    units = [] 
    for row in c.fetchall():
        units.append(row[0]) 
    return units

def get_new_units(handbookunits, dbunits):
    newunits = []
    for unit in handbookunits:
        if unit not in dbunits:
            newunits.append(unit)
    return newunits

def split_unit_list(units, n):
    return [units[i:i + n] for i in range(0, len(units), n)] 

def update_unit_db(newunits):
    conn = sqlite3.connect(f'handbook.db')
    c = conn.cursor()
    c.execute("SELECT * FROM handbook")

    dataset = scraper(newunits)

    removeunitlist = []
    for i in range(len(dataset[3])):
        if dataset[3][i] == 'ound':
            removeunitlist.append(i)

    if removeunitlist != []:
        removeunitlist.reverse()
        deletecodes = []
        conn2 = sqlite3.connect(f'handbookunits.db')
        c2 = conn2.cursor()
        c2.execute("SELECT * FROM handbookunits")
        for n in removeunitlist:
            deletecodes.append(dataset[0][n])
            dataset[0].pop(n)
            dataset[1].pop(n)
            dataset[2].pop(n)
            dataset[3].pop(n)
            dataset[4].pop(n)
            dataset[5].pop(n)
            dataset[6].pop(n)
            dataset[7].pop(n)
            dataset[8].pop(n)
            dataset[9].pop(n)
            dataset[10].pop(n)
            dataset[11].pop(n)
        for unitcode in deletecodes:
            c2.execute('''DELETE FROM handbookunits WHERE unitcodes = {}'''.format(f'"{unitcode}"'))
            conn2.commit() 

    scrape_parse(dataset)

    scrapedunits, scrapedprereqs, scrapedcoreqs, scrapedprohibs, scrapedrecom, scrapedsems, scrapednamedata, scrapedoverview, scrapedcreditpoints, scrapedfaculty, scrapedschool, scrapedrawsemester, scrapedRAWprerequisites, scrapedRAWcorequisites, scrapedRAWprohibitions, scrapedRAWrecommendations, scrapedscaband, scrapedeftsl, scrapedstudylevel, scrapedopentoexchange = import_subjects(dataset)

    insert_scraped(c, conn, scrapedunits, scrapednamedata, scrapedprereqs, scrapedcoreqs, scrapedprohibs, scrapedrecom, scrapedsems, scrapedoverview, scrapedcreditpoints, scrapedfaculty, scrapedschool, scrapedrawsemester, scrapedRAWprerequisites, scrapedRAWcorequisites, scrapedRAWprohibitions, scrapedRAWrecommendations, scrapedscaband, scrapedeftsl, scrapedstudylevel, scrapedopentoexchange)


handbookunits = get_handbook_units()
dbunits = get_db_units()

newunits = get_new_units(handbookunits, dbunits)

splitunitlist = split_unit_list(newunits,10)
groupcount = 1
numgroups = len(splitunitlist)


print(f'Scraping for {len(newunits)} units in {numgroups} groups...')
for subunitlist in splitunitlist:
    print(f'Scraping group {groupcount}/{numgroups}')
    update_unit_db(subunitlist)
    groupcount += 1
    time.sleep(5)
