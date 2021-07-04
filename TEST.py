strnumset = {'0','1','2','3','4','5','6','7','8','9'}
import csv
def import_subjects(filename):
    #and -> +
    #or -> , 
    #kill -> 'one of' ' ' 'completion of' 'at least' 'of study' '(' ')'
    prereqs = []
    f=[]
    with open(filename, newline = '') as line:               
        lines = csv.reader(line, delimiter='\t')
        for line in lines:
            f.append(line)
    subjects = f[0]
    reqs = f[1]

    for req in reqs:
        req = req.upper()
        phrases = {'ONE OF', 'COMPLETION OF', 'AT LEAST', 'OF STUDY', '(', ')', 'INCLUDING', 'UNITS', '.'}
        orrep = {'OR'}
        for phrase in phrases:
            req = req.replace(phrase,'')
        for phrase in orrep:
            req = req.replace(phrase,',')
        req = req.replace('AND','+')
        req = req.replace('POINTS OF', 'POINTS')
        req = req.replace('AT LEVEL', 'L')
        req = req.replace(' ','')
        if 'POINTS' in req:
            for _ in range(req.count('POINTS')): #check for numbe of occurances of 'POINTS'
                if 'L1,2' in req:
                    req = req.replace('L1,2','L1/2')
                elif 'L2,3' in req:
                    req = req.replace('L2,3','L2/3')
                i_points = req.index('POINTS')
                ie_points = i_points + 6
                if ie_points == len(req):                           #total if end
                    req = req.replace('POINTS','TOTAL',1)
                elif req[ie_points].isalpha():                     #department specific (unit)
                    ie_unit = ie_points + 3 #index after unit code
                    if ie_unit == len(req) or req[ie_unit] == ',' or req[ie_unit] == '+':#end check and delim check
                        req = req.replace('POINTS','TO',1)
                    elif req[ie_unit] == 'L':#unit and level
                        ie_lvl = ie_unit + 2
                        if ie_lvl == len(req) or req[ie_lvl] == ',' or req[ie_lvl] == '+': #check if single level
                            req = req.replace('POINTS','',1)
                        elif req[ie_lvl] == '/': #if multi lvl included (currently same as single)
                            req = req.replace('POINTS','',1)
                elif req[ie_points] == ',' or req[ie_points] == '+':  #total end with delim or number
                    req = req.replace('POINTS','TOTAL',1)
        prereqs.append(req)
    return subjects, prereqs



subjects, prereqs = import_subjects('book.txt')
print(subjects)
print(len(subjects))
print(prereqs)
print(len(prereqs))

