from copy import deepcopy
from Scraper.handbookscraper import scraper

"""
Data
subjects  = ['MTH2010','ASP2011','MTH2032']
prereqs   = [[['MTH1020']],[''],['']]
semesters = []
"""

flags = []
strnumset = {'0','1','2','3','4','5','6','7','8','9'}

def flag_handler(flag_message,flag_type):
    for i in flags:
        if flag_type in flags[i]:
            flags[i][1] += 1
            flags[i].append(flag_message)
        else:
            newflagindex = len(flags)
            flags.append([flag_type])
            flags[newflagindex].append(1)
            flags[newflagindex].append(flag_message)


def is_unit(string,substring = '',location = 0, proceded_by_space = False, exactly = False):
    if proceded_by_space:
        unitstart = location + len(substring)+1
    else:
        unitstart = location + len(substring)
    if exactly:
        return (len(string) == 7 or string[unitstart+7] == ' ') and string[unitstart:unitstart+3].isalpha() and string[unitstart+3:unitstart+7].isnumeric()
    else:
        return string[unitstart:unitstart+3].isalpha() and string[unitstart+3:unitstart+7].isnumeric()


def filter_req(req):
    if is_unit(req):
        return req[:7]
    elif is_unit(req,'',len(req)-7):
        return req[len(req)-7:]
    elif req[0].isnumeric():
        return req
    else:
        return ''
    

def import_subjects(data):
    #and -> +
    #or -> , 
    #kill -> 'one of' ' ' 'completion of' 'at least' 'of study' '(' ')'
    units = data[0]
    reqdata = data[1]
    semdata = data[2]
    namedata = data[3]

    """print(units)
    print(reqdata)
    print(semdata)
    print(namedata)
    staleones = []
    for i in range(len(namedata)):
        if namedata[i] == 'ERROR stale':
            staleones.insert(0,i)
    for index_stale in staleones:
        units.pop(index_stale)
        reqdata.pop(index_stale)
        semdata.pop(index_stale)
        namedata.pop(index_stale)"""

    datalen = len(reqdata)
    prereqs = ['']*datalen
    coreqs = ['']*datalen
    prohibs = ['']*datalen
    recom = ['']*datalen
    sems = ['']*datalen

    for h in range(len(reqdata)):
        for bit in reqdata[h]:
            if 'PREREQUISITE:' in bit:
                prereqs[h] = bit.replace('PREREQUISITE:', '')
                if 'PREREQUISITE' in prereqs[h]:
                    prereqs[h] = prereqs[h].replace('PREREQUISITE', 'AND')
            elif 'COREQUISITE:' in bit:
                coreqs[h] = bit.replace('COREQUISITE:', '')
            elif 'PROHIBITION:' in bit:
                prohibs[h] = bit.replace('PROHIBITION:', '')
            else:
                raise Exception('Label not found in data for ' + units[h] + 'See ->' + bit)
    reqlst = [prereqs,coreqs,prohibs]
    reqindex = -1
    for innerlst in reqlst:
        for j in range(len(innerlst)):
            req = innerlst[j]
            reqindex += 1
            req = req.upper()
            if 'RECOMMENDED' in req:
                reco_i = req.index('RECOMMENDED')
                if recom [j] == '':
                    recom[j] = req[reco_i:]
                else:
                    recom[j] += req[reco_i:]
                req = req[:reco_i]
            phrases = {'ONE OF', 'COMPLETION OF', 'AT LEAST', 'OF STUDY', 'INCLUDING', 'UNITS', '.', 'FOR', 'COORDINATOR', 'BACHELOR',':', 'PLUS'}
            orrep = {'OR'}
            #check for nested and
            if '(' in req and ')' in req:
                while req.count('(') > 0:
                    nestedandsnip = req[req.index('(')+1:req.index(')')]
                    if ('AND' in nestedandsnip):
                        flag_handler('Check "'+units[reqindex]+'" prerequisites for possible conflict as "' + nestedandsnip +'" had to be ignored.', 'Manual Prerequisite Checks Required')
                        req = req.replace(nestedandsnip,'')
                    req = req.replace('(','',1)
                    req = req.replace(')','',1)
            if ')' in req:
                req = req.replace(')','')
            #end nested and check
            for phrase in phrases:
                req = req.replace(phrase,'')
            req = req.replace('POINTS OF', 'POINTS')
            req = req.replace('AT LEVEL', 'L')
            #'PREREQUISITE: FIT1045 ALGORITHMS AND PROGRAMMING FUNDAMENTALS IN PYTHONOR FIT1048 FUNDAMENTALS OF C++OR FIT1051 PROGRAMMING FUNDAMENTALS IN JAVAOR FIT1053 ALGORITHMS AND PROGRAMMING IN PYTHON ADVANCED'
            conflictphrases = ['OR', 'AND']
            req = req.replace(' ','')
            for phrase in conflictphrases:
                phraselen = len(phrase)
                replacedphrase = ' '*phraselen
                checkstart = 0
                while req[checkstart:].count(phrase) > 0 and checkstart < len(req)-phraselen:
                    loc = req[checkstart:].index(phrase)
                    if loc+phraselen < len(req):
                        if not (is_unit(req[checkstart:], phrase, loc) or (req[checkstart+loc+phraselen].isnumeric() or (checkstart-loc>0 and req[checkstart-loc].isnumeric() and (not req[checkstart-loc-1].isnumeric())))):
                            req = req[:checkstart] + req[checkstart:].replace(phrase, replacedphrase, 1)
                    checkstart += (loc + phraselen)
            req = req.replace(' ','')
            if 'POINTS' in req:
                for _ in range(req.count('POINTS')): #check for numbe of occurances of 'POINTS'
                    if 'L1,2' in req:
                        req = req.replace('L1,2','L1/2')
                    elif 'L1OR2' in req:
                        req = req.replace('L1OR2','L1/2')
                    elif 'L2,3' in req:
                        req = req.replace('L2,3','L2/3')
                    elif 'L2OR3' in req:
                        req = req.replace('L2OR3','L2/3')
                    i_points = req.index('POINTS')
                    ie_points = i_points + 6
                    if ie_points == len(req):                           #total if end
                        req = req.replace('POINTS','TOTAL',1)
                    elif req[ie_points].isalpha():                     #department specific (unit)
                        ie_unit = ie_points + 3 #index after unit code
                        if ie_unit == len(req) or req[ie_unit:ie_unit+2] == 'OR' or req[ie_unit] == ',' or req[ie_unit:ie_unit+3] == 'AND':#end check and delim check
                            req = req.replace('POINTS','TO',1)
                            if 'TOANY' in req:
                                req = req.replace('TOANY','TOTAL',1)
                        elif req[ie_unit] == 'L':#unit and level
                            ie_lvl = ie_unit + 2
                            if ie_lvl == len(req) or req[ie_lvl:ie_lvl+2] == 'OR' or req[ie_lvl] == ',' or req[ie_lvl:ie_lvl+3] == 'AND': #check if single level
                                req = req.replace('POINTS','',1)
                            elif req[ie_lvl] == '/': #if multi lvl included (currently same as single)
                                req = req.replace('POINTS','',1)
                    elif req[ie_points] == ',' or req[ie_points:ie_points+3] == 'AND':  #total end with delim or number
                        req = req.replace('POINTS','TOTAL',1)
            req = req.replace('OR',',')
            req = req.split('AND')
            if ',,' in req:
                req = req.replace(',,',',')
            reqclean = []
            for i in range(len(req)):
                req[i] = req[i].split(',')
                while req[i].count('') > 0:
                    req[i].pop(req[i].index(''))
                for l in range(len(req[i])):
                    req[i][l] = filter_req(req[i][l])
                if req[i] != ['']:
                    reqclean.append(req[i])
            req = reqclean
            innerlst[j] = req
    for i in range(len(semdata)):
        semlst = semdata[i]
        for j in range(len(semlst)):
            if 'CLAYTON'in semlst[j] or 'CAULFIELD' in semlst[j]:
                if 'S1-01' in semlst[j]:
                    semlst[j] = 1
                elif 'S2-01' in semlst[j]:
                    semlst[j] = 2
                else:
                    semlst[j] = ''
            else:
                semlst[j] = ''
        while semlst.count('') > 0:
            semlst.pop(semlst.index(''))
        if len(semlst) == 1:
            semlst = semlst[0]
        else:
            if (semlst[0] == 1 and semlst[1] == 2) or (semlst[0] == 2 and semlst[1] == 1):
                semlst = '*'
        sems[i] = semlst

    return units, prereqs, coreqs, prohibs, recom, sems, namedata
    


def prereq_error_handle(subjects,prereqs):
    unmetreqs = []
    unmetsubjects = []
    for i in range(len(prereqs)):
        if prereqs[i] != 'Met':
            for j in range(len(prereqs[i])):
                if prereqs[i][j] != 'Met':
                    for k in range(len(prereqs[i][j])):
                        if prereqs[i][j][k] != 'Met':
                            unmetreqs.append(prereqs[i][j][k])
    for subject in subjects:
        if subject != '':
            unmetsubjects.append(subject)
    return unmetreqs, unmetsubjects


def prereq_check(prereqs,addedlst,done,points):
    for i in range(len(prereqs)):
        for j in range(len(prereqs[i])):
            for k in range(len(prereqs[i][j])):
                req = prereqs[i][j][k]
                if req == '':
                    prereqs[i][j][k] = 'Met'
                elif req in addedlst:
                    prereqs[i][j][k] = 'Met'
                elif req in done:
                    prereqs[i][j][k] = 'Met'
                elif req[0] in strnumset:
                    #expects in form '24toFIT' or '6L1FIT' or '36total'
                    pointreq = req[0]
                    l=1
                    while req[l] in strnumset:
                        pointreq += req[l]
                        l += 1
                    if len(req) > l+5 and req[l+5] == '/':
                        pointscurrent = points[points.index(req[len(pointreq):len(pointreq)+5])+1] + points[points.index(req[len(pointreq):len(pointreq)+4]+req[len(pointreq)+6])+1]
                    else:
                        pointscurrent  = points[points.index(req[len(pointreq):len(pointreq)+5])+1]
                    if int(pointreq) <= pointscurrent:
                        prereqs[i][j][k] = 'Met'

def coreq_check(coreqs,addedlst,done):
    for i in range(len(coreqs)):
        for j in range(len(coreqs[i])):
            if coreqs[i][j] == []:
                    coreqs[i][j] = 'Met'
            for k in range(len(coreqs[i][j])):
                coreq = coreqs[i][j][k]
                if coreq in addedlst:
                    coreqs[i][j][k] = 'Met'
                elif coreq in done:
                    coreqs[i][j][k] = 'Met'
    
def coreq_simp(coreqs):
    for i in range(len(coreqs)):
        if coreqs[i] == [[]]:
            coreqs[i] = 'Met'
        for j in range(len(coreqs[i])):
            if coreqs[i][j] == ['Met' for _ in range(len(coreqs[i][j]))]:
                coreqs[i][j] = 'Met'
            elif 'Met' in coreqs[i][j]:
                coreqs[i][j] = 'Met'
        if coreqs[i] == ['Met' for _ in range(len(coreqs[i]))]:
            coreqs[i] = 'Met'


def prereq_simp(prereqs):
    for i in range(len(prereqs)):
        for j in range(len(prereqs[i])):
            if prereqs[i][j] == ['Met' for _ in range(len(prereqs[i][j]))]:
                prereqs[i][j] = 'Met'
            elif 'Met' in prereqs[i][j]:
                prereqs[i][j] = 'Met'
        if prereqs[i] == ['Met' for _ in range(len(prereqs[i]))]:
            prereqs[i] = 'Met'


def pointhandle(sub,points):
    points[1] += 6
    #toLx
    if sub[3] == '1':
        points[7] += 6
    elif sub[3] == '2':
        points[9] += 6
    elif sub[3] == '3':
        points[11] += 6
    #toDEP and LxDEP
    if sub[:3] == 'FIT':
        points[3] += 6
        if sub[3] == '1':
            points[13] += 6
        elif sub[3] == '2':
            points[15] += 6
        elif sub[3] == '3':
            points[17] += 6
    elif sub[:3] == 'SCI':
        points[3] += 6
        if sub[3] == '1':
            points[19] += 6
        elif sub[3] == '2':
            points[21] += 6
        elif sub[3] == '3':
            points[23] += 6
    

def prereq_order(subjects, prereqs, coreqs, prohibs, recom, sems, done = [], semstart = 1):
    semester = semstart
    order = []
    tier = []
    addedlst = []
    addedlstTMP = []
    length = len(subjects)
    emptylst = ['' for i in range(length)]
    count = 0
    other = []
    points = ['TOTAL',0,'TOFIT',0,'TOSCI',0,'TOTL1',0,'TOTL2',0,'TOTL3',0,'FITL1',0,'FITL2',0,'FITL3',0,'SCIL1',0,'SCIL2',0,'SCIL3',0]
    if done != []:
        points[1] = 6*len(done)
        for sub in done:
            pointhandle(sub,points)

    def eligible(i,tier,subjects,points,addedlstTMP):
            tier.append(subjects[i])
            addedlstTMP.append(subjects[i])
            pointhandle(subjects[i],points)
            subjects[i] = ''

    empcount = 0
    while subjects != emptylst and count < length**2:
        count += 1
        prereq_check(prereqs,addedlst,done,points)
        prereq_simp(prereqs)
        for i in range(len(subjects)):
            if len(tier) == 4:
                break
            if subjects[i] != '' and (prereqs[i] == 'Met' or prereqs[i] == '') and (sems[i] == '*' or sems[i] == semester) and (coreqs[i] == 'Met' or coreqs[i] == [[]] or coreqs[i] == [['']]):
                eligible(i,tier,subjects,points,addedlst)
                coreq_check(coreqs,addedlst,done)
                coreq_simp(coreqs)
        if not tier:
            empcount += 1
            if empcount > 10:
                unmetreqs, unmetsubjects = prereq_error_handle(subjects,prereqs)
                other.append('Error: Prereqs not met')
                other.append([unmetreqs,unmetsubjects])
                allunits = addedlst + done
                return order, semstart, flags, allunits, other
        if tier:
            order.append(tier)
        tier = []
        for sub in addedlstTMP:
            addedlst.append(sub)
        addedlstTMP = []
        if semester == 1:
            semester = 2
        else:
            semester = 1
    if count == length**2:
        other.append('Error: over count')
    allunits = addedlst + done
    return order, semstart, flags, allunits, other


def subject_order(order):
    subject_list = deepcopy(order)
    sem = []
    final = []
    while subject_list != []:
        while len(sem) < 4:
            if subject_list[0] == []:
                sem.append('')
            else:
                sem.append(subject_list[0][0])
                subject_list[0].pop(0)
        if subject_list[0] == []:
            subject_list.pop(0)
        final.append(sem)
        sem = []
    return final




#dataset = [['MTH2010', 'MTH2032', 'PHS2062', 'FIT1049', 'FIT2094', 'FIT2081', 'FIT2001', 'FIT3175', 'ASP3051', 'PHS3201', 'FIT2002', 'ASP3012', 'PHS3000', 'FIT3047', 'FIT3077', 'PHS3101', 'ASP3231', 'FIT3048', 'FIT2099', 'FIT3146', 'ASP3162'], [['PREREQUISITE: STUDENTS MUST HAVE PASSED MTH1030, MTH1035, OR MTH1040 WITH A MARK OF AT LEAST 60. EXCEPTIONS FOR STUDENTS WHO PASSED THESE UNITS WITH A MARK IN THE RANGE OF 50 TO 59 CAN BE MADE WITH PERMISSION FROM THE UNIT CO-COORDINATOR BASED ON A DIAGNOSTIC TEST. ', 'PROHIBITION: ENG2005, ENG2091, MTH2015 '], ['PROHIBITION: MTH2040 MATHEMATICAL MODELLING', 'PREREQUISITE: MTH1030 TECHNIQUES FOR MODELLINGOR MTH1035 TECHNIQUES FOR MODELLING (ADVANCED)', 'COREQUISITE: MTH2015 MULTIVARIABLE CALCULUS (ADVANCED)OR MTH2010 MULTIVARIABLE CALCULUS'], ['COREQUISITE: RECOMMENDED: MTH2032 OR MTH2040 NOTE: SUPPORTING MATHEMATICS STUDIES ARE REQUIRED FOR PROGRESSION TOWARDS THE ASTROPHYSICS AND PHYSICS MAJORS ', 'PREREQUISITE: ONE OF PHS1022, PHS1002 AND ONE OF MTH2010, MTH2015, ENG2005. ', 'PROHIBITION: PHS2022 '], ['PREREQUISITE: COMPLETION OF 12 POINTS OF FIT UNITS. ', 'PROHIBITION: FIT2003, FZA1049 '], ['PREREQUISITE: ONE OF FIT1040, FIT1045, FIT1048, FIT1051, FIT1053 OR EQUIVALENT INTRODUCTORY PROGRAMMING UNIT ', 'PROHIBITION: FIT1004, FIT3171, FZA2094 '], ['PREREQUISITE: FIT1002, FIT1045, FIT1048, FIT1051, FIT1053, FIT2071 OR EQUIVALENT ', 'PROHIBITION: FZA2081 MOBILE APPLICATION DEVELOPMENT'], ['PREREQUISITE: 24 POINTS OF FIT UNITS ', 'PROHIBITION: BUS2021, CPE2003, CSE1204, CSE1205, FZA2001, GCO1813, GCO2601, GCO2852, GCO2826, IMS1001, IMS1002, IMS1805, IMS2071, IMS9001 '], ['PROHIBITION: FIT3063, FIT2016, FIT3033, FZA3175 ', 'PREREQUISITE: FIT1045 ALGORITHMS AND PROGRAMMING FUNDAMENTALS IN PYTHONOR FIT1048 FUNDAMENTALS OF C++OR FIT1051 PROGRAMMING FUNDAMENTALS IN JAVAOR FIT1053 ALGORITHMS AND PROGRAMMING IN PYTHON (ADVANCED)'], ['PREREQUISITE: ONE OF MTH2010, MTH2015 OR ENG2005 RECOMMENDED UNITS: MTH2032 OR MTH2040, PLUS ONE UNIT (SIX CREDIT POINTS) OF ASTROPHYSICS AT SECOND-YEAR LEVEL OR PHYSICS AT FIRST-YEAR LEVEL '], ['PREREQUISITE: PHS2062 AND ONE OF: MTH2032 OR MTH2040 ', 'PROHIBITION: PHS3131 '], ['PREREQUISITE: COMPLETION OF AT LEAST 36 POINTS OF STUDY, INCLUDING ONE OF (FIT1040, FIT1045, FIT1053, FIT1048, FIT1051, ENG1003) (OR EQUIVALENT). ', 'PROHIBITION: FZA2002 IT PROJECT MANAGEMENT'], ['PREREQUISITE: ASP2062 OR PERMISSION FROM THE UNIT COORDINATOR AND ONE OF MTH2010, MTH2015 OR ENG2005 AND ONE OF MTH2032 OR MTH2040 '], ['PREREQUISITE: PHS2061 AND PHS2062 AND ONE OF MTH2032 OR MTH2040 RECOMMENDED: PHS2081 ', 'PROHIBITION: PHS3031, PHS3051, PHS3042, PHS3062 '], ["PREREQUISITE: FOR STUDENTS IN THE BACHELOR OF INFORMATION TECHNOLOGY (C2000) AND BCIS (4307): (ONE OF FIT1045, FIT1048, FIT1051 OR FIT1053) AND FIT1047 AND FIT1049 AND (ONE OF FIT2001 OR FIT2099) AND FIT2002 AND (ONE OF FIT2094 OR FIT3171) AND (12 POINTS OF FIT UNITS AT LEVEL 1) AND (12 POINTS OF FIT UNITS AT LEVEL 2 OR 3) AND MUST BE CORE IN THE STUDENT'S DEGREE PROGRAM AND COMPLETION OF A TOTAL OF 90 POINTS TOWARDS THE DEGREE. ", 'PROHIBITION: FIT2032, FIT3039, FIT3040, FIT3045, FZA3047 '], ['PREREQUISITE: FIT2099 OR (FIT2001 AND (FIT2004 OR FIT2024 OR FIT2081 OR CSE2304)) ', 'PROHIBITION: FZA3077 SOFTWARE ENGINEERING: ARCHITECTURE AND DESIGN'], ['PREREQUISITE: PHS2061 AND ONE OF MTH2010, MTH2015 OR ENG2005 AND ONE OF MTH2032 OR MTH2040 ', 'PROHIBITION: PHS3142 '], ['PREREQUISITE: ASP2062 INTRODUCTION TO ASTROPHYSICSOR ASP2011 ASTRONOMY'], ['PROHIBITION: CPE3200, CPE3300, CSE3200, CSE3301, FIT2032, FIT3015, FIT3016, FIT3017, FIT3025, FIT3026, FIT3038, FIT3039, FIT3040, FIT3045, FZA3048, GCO3819, GCO3700, GCO3800, GCO3900, GCO3800A, IMS3000, IMS3501, IMS3502 ', 'PREREQUISITE: FIT3047 INDUSTRY EXPERIENCE STUDIO PROJECT 1'], ['PREREQUISITE: (ENG1003 AND ENG1060) OR ONE OF FIT1045, FIT1048, FIT1051, FIT1053, FIT1054, FIT1008 OR FIT2071', 'PROHIBITION: FIT2024 '], ['PREREQUISITE: PLUS 90 POINTS OF ANY UNITS PREREQUISITE FIT1045 ALGORITHMS AND PROGRAMMING FUNDAMENTALS IN PYTHONOR FIT1051 PROGRAMMING FUNDAMENTALS IN JAVAOR ENG1003 ENGINEERING MOBILE APPSOR FIT1048 FUNDAMENTALS OF C++'], ['PREREQUISITE: ASP2062 AND MTH2010 OR MTH2015 OR ENG2005 AND MTH2032 OR MTH2040 ']], [['S1-01-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['S2-01-CLAYTON-ON-CAMPUS'], ['S2-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S1-01-MALAYSIA-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS', 'S2-01-MALAYSIA-ON-CAMPUS', 'SSB-01-CLAYTON-ON-CAMPUS'], ['OCT12-CLAYTON-ON-CAMPUS', 'S1-01-CLAYTON-ON-CAMPUS', 'S1-01-MALAYSIA-ON-CAMPUS'], ['OCT12-CLAYTON-ON-CAMPUS', 'S1-01-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S2-01-MALAYSIA-ON-CAMPUS', 'SSA-02-MALAYSIA-ON-CAMPUS', 'SSB-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS'], ['OCT12-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['S2-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S1-01-MALAYSIA-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S1-01-MALAYSIA-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS', 'S2-01-MALAYSIA-ON-CAMPUS'], ['S2-01-CLAYTON-ON-CAMPUS'], ['S2-01-CLAYTON-ON-CAMPUS']]]

#units, prereqs, coreqs, prohibs, recom, sems = import_subjects(dataset)
#done = ['ASP1010', 'FIT1050', 'MTH1030', 'PHS1001', 'ASP2062', 'PHS2061', 'PHS1002','MTH1020','FIT1045', 'FIT1047', 'ASP2011']
#semesters = []
#print(units, prereqs, coreqs, prohibs, recom, sems)
#print(prereqs)
"""fetches = scraper(subjects)
print(fetches)"""
#print(coreqs)
#units, prereqs, coreqs, prohibs, recom, sems = [['MTH2010', 'MTH2032'], [[['MTH1030', 'MTH1035', 'MTH1040']], [['MTH1030', 'MTH1035']]], [[[]], [['MTH2015', 'MTH2010']]], [[['ENG2005', 'ENG2091', 'MTH2015']], [['MTH2040']]], ['', ''], ['*', 2]]
#order = prereq_order(units, prereqs, coreqs, prohibs, recom, sems, done, 2)[0]
#print(order)
#[['IT'], ['Maths', 'IT2'], ['Maths2', 'Physics', 'Machine'], ['Maths3', 'Astro'], ['Astro2', 'Physics2']]
#print(subject_order(order))
            
    