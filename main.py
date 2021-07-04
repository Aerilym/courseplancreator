from enum import auto
from os import lseek
from flask import Flask, jsonify, render_template, url_for
from flask import request
from flask.templating import render_template_string
from unitmanager import import_subjects, prereq_order, is_unit, pointhandle
from Scraper.handbookscraper import scraper
from Scraper.scrapeparser import scrape_parse
import sqlite3 
from unitdbhandle import table_exists, insert_unit, get_units, get_unit, update_unit, delete_unit, insert_scraped, dblist_unpacker, dblist_unpacker_shallow
from copy import copy
from planformat import planformathtml, planformatcsv
import csv
from datetime import date
from changelog import changelog
from logging.config import dictConfig
import sys


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)
hostip = '127.0.0.1'
#hostip = '192.168.1.100'

global unitslst
global autogen
global autogenstatus
global order
global unitslstcomp
global unitslstexh
global semlst
global namelst
global yearstart
global semstart
global otherslst
global CPgoal
otherslst = []
currentdate = date.today()
yearstart = currentdate.year
currentmonth = currentdate.month
if currentmonth > 4 and currentmonth <10:
    semstart = 2
else:
    semstart = 1
namelst = [[],[]]
unitslst = []
unitslstcomp = []
unitslstexh = []
semlst = []
order = ''
autogen = 0
autogenstatus = 'OFF'
CPgoal = 144
f = open('static/plans/plan.csv', 'w')
writer = csv.writer(f)
writer.writerow('')
f.close


@app.route("/", methods = ['POST', 'GET'])
def index():
    if request.method == 'GET':
        global unitslst
        global autogen
        global autogenstatus
        global order
        global unitslstcomp
        global unitslstexh
        global semlst
        global namelst
        global yearstart
        global semstart
        global otherslst
        global CPgoal
        otherslst = []
        currentdate = date.today()
        yearstart = currentdate.year
        currentmonth = currentdate.month
        if currentmonth > 4 and currentmonth <10:
            semstart = 2
        else:
            semstart = 1
        namelst = [[],[]]
        unitslst = []
        unitslstcomp = []
        unitslstexh = []
        semlst = []
        order = ''
        autogen = 0
        f = open('static/plans/plan.csv', 'w')
        writer = csv.writer(f)
        writer.writerow('')
        f.close
        autogenstatus = 'Off'
    elif request.method == 'POST':
        print(otherslst)
        if request.form['submit_button'] == 'Add Unit/s':
            newunits = request.form['units'].upper().replace(' ', '')
            unitlisthandler(newunits, unitslst)
        elif request.form['submit_button'] == 'Add Completed Unit/s':
            newunits = request.form['completedunits'].upper().replace(' ', '')
            unitlisthandler(newunits, unitslstcomp)
        elif request.form['submit_button'] == 'Add Exempt Unit/s':
            newunits = request.form['exemptunits'].upper().replace(' ', '')
            unitlisthandler(newunits, unitslstexh)
        elif request.form['submit_button'] == 'Generate order':
            makepage(1)
        elif request.form['submit_button'] == 'Toggle Autogen':
            autogen = 1 if not autogen else 0
            autogenstatus = 'ON' if autogen else 'OFF'
        elif request.form['submit_button'] == 'Set Year':
            yearstartinput = request.form['yearstart']
            if yearstartinput != '' and yearstartinput.isnumeric():
                yearstartinput = int(yearstartinput)
                yearstart = yearstartinput
        elif request.form['submit_button'] == 'Toggle Semester':
            semstart = 1 if semstart == 2 else 2
        elif request.form['submit_button'] == 'RESET':
            namelst = [[],[]]
            unitslst = []
            unitslstcomp = []
            unitslstexh = []
            semlst = []
            order = ''
            autogenstatus = 'OFF'
            autogen = 0
            CPgoal = 144
        elif request.form['submit_button'] == 'Set Credit Point Goal':
            CPgoal = int(request.form['CPGOAL'])
        elif request.form['submit_button'] == 'DEVTEST':
            unitslst = []
            unitslstcomp = []
            unitslstexh = []
            unitlisthandler('MTH2010, MTH2032, PHS2062, FIT1049, FIT2094, FIT2081, FIT2001, FIT3175, ASP3051, PHS3201, FIT2002, ASP3012, PHS3000, FIT3047, FIT3077, PHS3101, ASP3231, FIT3048, FIT2099, FIT3146, ASP3162'.upper().replace(' ', ''), unitslst)
            unitlisthandler('ASP1010, FIT1050, MTH1030, PHS1001, ASP2062, PHS2061,MTH1020,FIT1045, FIT1047, ASP2011'.upper().replace(' ', ''), unitslstcomp)
            unitlisthandler('PHS1002'.upper().replace(' ', ''), unitslstexh)
            autogenstatus = 'ON'
            autogen = 1
        else:
            for unit in unitslst:
               if request.form['submit_button'] == 'popunit'+unit:
                    unitslst.pop(unitslst.index(unit))
            for unit in unitslstcomp:
               if request.form['submit_button'] == 'popunit'+unit:
                    unitslstcomp.pop(unitslstcomp.index(unit))
            for unit in unitslstexh:
               if request.form['submit_button'] == 'popunit'+unit:
                    unitslstexh.pop(unitslstexh.index(unit))
            for unit in otherslst:
                if request.form['submit_button'] == 'addunit'+unit:
                    unitlisthandler(unit, unitslst)
        return makepage(0)
    else:
        pass
    return makepage(0)

def makepage(mangen):
    global semlst
    global namelst
    creditpoints = 0
    if len(unitslst)>0 and (mangen or autogen):
        semlst, namelst, other, othertiers, unitmodalinfo, unitmodalinfoadd, creditpoints= mainapp(unitslst, unitslstcomp, unitslstexh)
        
        f = open('othertiers.txt', 'w')
        f.write(str(othertiers))
        f.close
        for i in range(len(semlst)):
            for j in range(len(semlst[i])):
                if semlst[i][j][:8] == 'Semester' or semlst[i][j] == '':
                    semlst[i][j] = [semlst[i][j]]
                else:
                    semlst[i][j] = [semlst[i][j],namelst[1][namelst[0].index(semlst[i][j])]]
    else:
        other = ''
        unitmodalinfo = [['']*15]
        unitmodalinfoadd = [['']*15]
    changelogstr, currentversion = changelog()
    creditpercent = int((creditpoints/CPgoal)*100)
    return (render_template('index.html', yearstart = yearstart, currentversion = currentversion) 
    + render_template('unitmodals.html', unitmodalinfo = unitmodalinfo) 
    + render_template('unitmodals.html', unitmodalinfo = unitmodalinfoadd) 
    + render_template('topsec.html',completedunits = unitslstcomp, exemptunits = unitslstexh, autogenstatus = autogenstatus, semstart = semstart) 
    + render_template('unitadding.html', units = unitslst, completedunits = unitslstcomp, exemptunits = unitslstexh) 
    + render_template('topsecright.html')
    + render_template('mainsec.html', semstart = semstart, yearstart = yearstart) 
    + render_template('plangen2.html', semlst = semlst, credits = creditpoints, creditpointgoal = str(CPgoal), creditpercent = creditpercent) 
    + render_template('mainsecright.html')
    + render_template_string(other) 
    + render_template('clogmid.html') 
    + render_template_string(changelogstr) 
    + render_template('end.html'))


def unitlisthandler(listofunits, globalunitlist):
    if listofunits != '':
        while len(listofunits)>7 and not listofunits[-1].isnumeric():
            listofunits = listofunits[:-1]
        if len(listofunits)>6:
            if ',' in listofunits:
                listofunits = listofunits.split(',')
            else:
                listofunits = [listofunits]
            for unit in listofunits:
                if unit not in globalunitlist and is_unit(unit, exactly=True):
                    globalunitlist.append(unit)

def unitfinder(listofunits):
    units = listofunits[:]
    conn = sqlite3.connect('handbook.db') 
    c = conn.cursor()
    if not table_exists(c, 'handbook'): 
        c.execute(''' 
            CREATE TABLE handbook( 
                unit_id TEXT PRIMARY KEY, 
                name TEXT, 
                semester INTEGER,
                prerequisites TEXT,
                corequisites TEXT,
                prohibitions TEXT,
                recommendations TEXT,
                overview TEXT,
                creditpoints TEXT,
                faculty TEXT,
                school TEXT,
                rawsemester TEXT,
                RAWprerequisites TEXT,
                RAWcorequisites TEXT,
                RAWprohibitions TEXT,
                RAWrecommendations TEXT,
                scaband TEXT,
                eftsl TEXT,
                studylevel TEXT,
                opentoexchange TEXT
            ) 
        ''')
    for i in range(len(units)):
        if not is_unit(units[i], exactly=True):
            units[i] == ''
    if units != ['']:
        numunits = len(units)
        toscrape = copy(units)
        unitnames = ['']*numunits
        prereqs = ['']*numunits
        coreqs = ['']*numunits
        prohibs = ['']*numunits
        recom = ['']*numunits
        sems = ['']*numunits
        overview = ['']*numunits
        creditpoints = ['']*numunits
        faculty = ['']*numunits
        school = ['']*numunits
        rawsemester = ['']*numunits
        RAWprerequisites = ['']*numunits
        RAWcorequisites = ['']*numunits
        RAWprohibitions = ['']*numunits
        RAWrecommendations = ['']*numunits
        scaband = ['']*numunits
        eftsl = ['']*numunits
        studylevel = ['']*numunits
        opentoexchange = ['']*numunits
        scrapeunits = []
    for i in range(len(listofunits)):
        try:
            dbunit_id, dbname, dbsemester, dbprerequisites, dbcorequisites, dbprohibitions, dbrecommendations, dboverview, dbcreditpoints, dbfaculty, dbschool, dbrawsemester, dbRAWprerequisites, dbRAWcorequisites, dbRAWprohibitions, dbRAWrecommendations, dbscaband, dbeftsl, dbstudylevel, dbopentoexchange= get_unit(c, "'"+units[i]+"'")[0] #unit_id, name, semester, prerequisites, corequisites, prohibitions, recommendations
            if dbunit_id != '':
                toscrape[i] = ''
                sems[i] = dbsemester
                unitnames[i] = dbname
                prereqs[i] = dblist_unpacker(dbprerequisites)
                coreqs[i] = dblist_unpacker(dbcorequisites)
                prohibs[i] = dblist_unpacker(dbprohibitions)
                recom[i] = dbrecommendations
                overview[i] = dboverview
                creditpoints[i] = dbcreditpoints
                faculty[i] = dbfaculty
                school[i] = dbschool
                rawsemester[i] = dblist_unpacker_shallow(dbrawsemester)
                RAWprerequisites[i] = dbRAWprerequisites
                RAWcorequisites[i] = dbRAWcorequisites
                RAWprohibitions[i] = dbRAWprohibitions
                RAWrecommendations[i] = dbRAWrecommendations
                scaband[i] = dbscaband
                eftsl[i] = dbeftsl
                studylevel[i] = dbstudylevel
                opentoexchange[i] = dbopentoexchange
        except:
            pass
        finally:
            if toscrape[i] != '':
                scrapeunits.append(toscrape[i])
    if scrapeunits != []:
        dataset = scraper(scrapeunits)
        scrape_parse(dataset)
        scrapedunits, scrapedprereqs, scrapedcoreqs, scrapedprohibs, scrapedrecom, scrapedsems, scrapednamedata, scrapedoverview, scrapedcreditpoints, scrapedfaculty, scrapedschool, scrapedrawsemester, scrapedRAWprerequisites, scrapedRAWcorequisites, scrapedRAWprohibitions, scrapedRAWrecommendations, scrapedscaband, scrapedeftsl, scrapedstudylevel, scrapedopentoexchange = import_subjects(dataset)
        try: 
            insert_scraped(c, conn, scrapedunits, scrapednamedata, scrapedprereqs, scrapedcoreqs, scrapedprohibs, scrapedrecom, scrapedsems, scrapedoverview, scrapedcreditpoints, scrapedfaculty, scrapedschool, scrapedrawsemester, scrapedRAWprerequisites, scrapedRAWcorequisites, scrapedRAWprohibitions, scrapedRAWrecommendations, scrapedscaband, scrapedeftsl, scrapedstudylevel, scrapedopentoexchange)
        except:
            pass
        for i in range(len(scrapeunits)):
            unit_i = units.index(scrapedunits[i])
            unitnames[unit_i] = scrapednamedata[i]
            sems[unit_i] = scrapedsems[i]
            prereqs[unit_i] = scrapedprereqs[i]
            coreqs[unit_i] = scrapedcoreqs[i]
            prohibs[unit_i] = scrapedprohibs[i]
            recom[unit_i] = scrapedrecom[i]
            overview[i] = scrapedoverview[i]
            creditpoints[i] = scrapedcreditpoints[i]
            faculty[i] = scrapedfaculty[i]
            school[i] = scrapedschool[i]
            rawsemester[i] = scrapedrawsemester[i]
            RAWprerequisites[i] = scrapedRAWprerequisites[i]
            RAWcorequisites[i] = scrapedRAWcorequisites[i]
            RAWprohibitions[i] = scrapedRAWprohibitions[i]
            RAWrecommendations[i] = scrapedRAWrecommendations[i]
            scaband[i] = scrapedscaband[i]
            eftsl[i] = scrapedeftsl[i]
            studylevel[i] = scrapedstudylevel[i]
            opentoexchange[i] = scrapedopentoexchange[i]

    return units, prereqs, coreqs, prohibs, recom, sems, unitnames, overview, creditpoints, faculty, school, rawsemester, RAWprerequisites, RAWcorequisites, RAWprohibitions, RAWrecommendations, scaband, eftsl, studylevel, opentoexchange


def mainapp(unitslst, unitslstcomp, unitslstexh):
    global semstart
    global yearstart
    global otherslst
    creditpointscount = 0
    units, prereqs, coreqs, prohibs, recom, sems, unitnames, overview, creditpoints, faculty, school, rawsemester, RAWprerequisites, RAWcorequisites, RAWprohibitions, RAWrecommendations, scaband, eftsl, studylevel, opentoexchange = unitfinder(unitslst)
    unitmodalinfo= [[]]*(len(units))
    unitmodalinfocomp= [[]]*(len(unitslstcomp))
    unitmodalinfoexh= [[]]*(len(unitslstexh))
    unitmodalinfoadd = [[]]*len(units)
    for i in range(len(units)):
        unitmodalinfo[i] = [units[i], unitnames[i], overview[i], RAWprerequisites[i], RAWcorequisites[i], RAWprohibitions[i], RAWrecommendations[i], rawsemester[i], creditpoints[i], faculty[i], school[i], scaband[i], eftsl[i], studylevel[i], opentoexchange[i]]
    done = unitslstcomp+unitslstexh
    if units != ['']:
        for i in range(len(unitmodalinfo)):
            creditpointscount += int(unitmodalinfo[i][8])
        order, semstart, allunits, other, othertiers = prereq_order(units, prereqs, coreqs, prohibs, recom, sems, done, semstart)
        other, otherslst = otherhandle(other, allunits)
        if otherslst != []:
            addunits, addprereqs, addcoreqs, addprohibs, addrecom, addsems, addunitnames, addoverview, addcreditpoints, addfaculty, addschool, addrawsemester, addRAWprerequisites, addRAWcorequisites, addRAWprohibitions, addRAWrecommendations, addscaband, addeftsl, addstudylevel, addopentoexchange = unitfinder(otherslst)
            unitmodalinfoadd= [[]]*len(addunits)
            for i in range(len(addunits)):
                unitmodalinfoadd[i] = [addunits[i], addunitnames[i], addoverview[i], addRAWprerequisites[i], addRAWcorequisites[i], addRAWprohibitions[i], addRAWrecommendations[i], addrawsemester[i], addcreditpoints[i], addfaculty[i], addschool[i], addscaband[i], addeftsl[i], addstudylevel[i], addopentoexchange[i]]
        if unitslstcomp != []:
            compunits, compprereqs, compcoreqs, compprohibs, comprecom, compsems, compunitnames, compoverview, compcreditpoints, compfaculty, compschool, comprawsemester, compRAWprerequisites, compRAWcorequisites, compRAWprohibitions, compRAWrecommendations, compscaband, compeftsl, compstudylevel, compopentoexchange = unitfinder(unitslstcomp)
            unitmodalinfocomp= [[]]*len(compunits)
            for i in range(len(compunits)):
                unitmodalinfocomp[i] = [compunits[i], compunitnames[i], compoverview[i], compRAWprerequisites[i], compRAWcorequisites[i], compRAWprohibitions[i], compRAWrecommendations[i], comprawsemester[i], compcreditpoints[i], compfaculty[i], compschool[i], compscaband[i], compeftsl[i], compstudylevel[i], compopentoexchange[i]]
            for i in range(len(unitmodalinfocomp)):
                creditpointscount += int(unitmodalinfocomp[i][8])
        if unitslstexh != []:
            exhunits, exhprereqs, exhcoreqs, exhprohibs, exhrecom, exhsems, exhunitnames, exhoverview, exhcreditpoints, exhfaculty, exhschool, exhrawsemester, exhRAWprerequisites, exhRAWcorequisites, exhRAWprohibitions, exhRAWrecommendations, exhscaband, exheftsl, exhstudylevel, exhopentoexchange = unitfinder(unitslstexh)
            unitmodalinfoexh= [[]]*len(exhunits)
            for i in range(len(exhunits)):
                unitmodalinfoexh[i] = [exhunits[i], exhunitnames[i], exhoverview[i], exhRAWprerequisites[i], exhRAWcorequisites[i], exhRAWprohibitions[i], exhRAWrecommendations[i], exhrawsemester[i], exhcreditpoints[i], exhfaculty[i], exhschool[i], exhscaband[i], exheftsl[i], exhstudylevel[i], exhopentoexchange[i]]
            for i in range(len(unitmodalinfoexh)):
                creditpointscount += int(unitmodalinfoexh[i][8])
        if order != []:
            semlst =  planformatcsv(order,semstart,yearstart)
        else:
            semlst = []
        unitmodalinfoadd = unitmodalinfoadd + unitmodalinfocomp + unitmodalinfoexh
        return semlst, [unitslst,unitnames], other, othertiers, unitmodalinfo, unitmodalinfoadd, creditpointscount
    else:
        return ''
    #except ValueError:
    #    return "invalid input"


def otherhandle(others, allunits):
    otherslst = []
    unmet = ''
    reqmanagermodals = ''
    if 'Error: Prereqs not met' in others:
        unmet = ['Prerequisites unmet for:<br>']
        unmethandle_i = others.index('Error: Prereqs not met')+1
        unmetsubjects = others[unmethandle_i][1]
        unmetreqs = ['']*len(unmetsubjects)
        unmetcoreqs = ['']*len(unmetsubjects)
        for i in range(len(unmetsubjects)):
            unmet.append(unmetsubjects[i])
        conn = sqlite3.connect('handbook.db') 
        c = conn.cursor()
        for i in range(len(unmetsubjects)):
            dbunit_id, dbname, dbsemester, dbprerequisites, dbcorequisites, dbprohibitions, dbrecommendations, dboverview, dbcreditpoints, dbfaculty, dbschool, dbrawsemester, dbRAWprerequisites, dbRAWcorequisites, dbRAWprohibitions, dbRAWrecommendations, dbscaband, dbeftsl, dbstudylevel, dbopentoexchange = get_unit(c, "'"+unmetsubjects[i]+"'")[0] #unit_id, name, semester, prerequisites, corequisites, prohibitions, recommendations
            if dbunit_id != '':
                unmetreq = dblist_unpacker(dbprerequisites)
                unmetcoreq = dblist_unpacker(dbcorequisites)
                hascoreq = unmetcoreq != [['']]

                def reqsplitandformat(ureq):
                    print(ureq, file=sys.stderr)
                    for j in range(len(ureq)):
                        for k in range(len(ureq[j])):
                            if ureq[j][k] in allunits:
                                ureq[j][k] = f'<button type="button" class="btn btn-success btn-sm btn-unit" data-toggle="modal" data-target="#{ureq[j][k]}unitmodal"><a class="metreqinunmet">{ureq[j][k]}</a></button>'
                            else:
                                otherslst.append(ureq[j][k])
                                ureq[j][k] = f'{reqmanagermodals}<button type="button" class="btn btn-secondary btn-sm btn-unit" data-toggle="modal" data-target="#{ureq[j][k]}unitmodal"><a>{ureq[j][k]}</a></button>'
                        ureq[j] = ' OR '.join(ureq[j])
                        if 'metreqinunmet' in ureq[j]:
                            ureq[j] = '<div class="reqorline reqlinemet">' + ureq[j] + '</div>'
                        else:
                            ureq[j] = '<div class="reqorline">' + ureq[j] + '</div>'

                reqsplitandformat(unmetreq)
                unmetreqs[i] = ' <div class="reqand">AND</div> '.join(unmetreq)
                reqsplitandformat(unmetcoreq)
                unmetcoreqs[i] = ' <<div class="reqand">AND</div> '.join(unmetcoreq)
                if hascoreq:
                    unmetcoreqs[i] = f'<div style="text-align: center;">Corequisites unmet</div>{unmetcoreqs[i]}'
                else:
                     unmetcoreqs[i] = f''
                #unmet[i+1] = f'<li><a href="https://handbook.monash.edu/current/units/{unmet[i+1]}" target="_blank">{unmet[i+1]}</a>: {unmetreqs[i]}{unmetcoreqs[i]}</li>'
                unmet[i+1] = f'<div class="reqcontainer"><button type="button" class="btn btn-primary btn-sm btn-unit" style="width:100%;" data-toggle="modal" data-target="#{unmet[i+1]}unitmodal"><a>{unmet[i+1]}</a></button><div>{unmetreqs[i]}{unmetcoreqs[i]}</div></div><br>'
    return reqmanagermodals + ''.join(unmet), otherslst


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == "__main__":
    app.run(host=hostip, port=8080, debug=True)

