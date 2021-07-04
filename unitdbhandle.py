import sqlite3
import json

def table_exists(c, table_name): 
    c.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = '{}' '''.format(table_name)) 
    if c.fetchone()[0] == 1: 
        return True 
    return False

def insert_unit(c, conn, unit_id, name, semester, prerequisites, corequisites, prohibitions, recommendations, overview, creditpoints, faculty, school, rawsemester, RAWprerequisites, RAWcorequisites, RAWprohibitions, RAWrecommendations, scaband, eftsl, studylevel, opentoexchange): 
    c.execute(''' INSERT INTO handbook (unit_id, name, semester, prerequisites, corequisites, prohibitions, recommendations, overview, creditpoints, faculty, school, rawsemester, RAWprerequisites, RAWcorequisites, RAWprohibitions, RAWrecommendations, scaband, eftsl, studylevel, opentoexchange) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''', (unit_id, name, semester, prerequisites, corequisites, prohibitions, recommendations, overview, creditpoints, faculty, school, rawsemester, RAWprerequisites, RAWcorequisites, RAWprohibitions, RAWrecommendations, scaband, eftsl, studylevel, opentoexchange)) 
    conn.commit()



def get_units(c): 
    c.execute('''SELECT * FROM handbook''') 
    data = [] 
    for row in c.fetchall(): 
        data.append(row) 
    return data

def get_unit(c, unit_id): 
    c.execute('''SELECT * FROM handbook WHERE unit_id = {}'''.format(unit_id)) 
    data = [] 
    for row in c.fetchall():  
        data.append(row) 
    return data

def update_unit(c, conn, unit_id, update_dict): 
    valid_keys = ['name', 'semester', 'prerequisites', 'corequisites', 'prohibitions', 'recommendations'] 
    for key in update_dict.keys():  
        if key not in valid_keys: 
            raise Exception('Invalid field name!') 
    for key in update_dict.keys(): 
        if type(update_dict[key]) == str: 
            stmt = '''UPDATE handbook SET {} = '{}' WHERE unit_id = {}'''.format(key, update_dict[key], unit_id) 
        else: 
            stmt = '''UPDATE handbook SET {} = '{}' WHERE unit_id = {}'''.format(key, update_dict[key], unit_id) 
        c.execute(stmt) 
    conn.commit()

def delete_unit(c, conn, unit_id): 
    c.execute('''DELETE FROM handbook WHERE unit_id = {}'''.format(unit_id)) 
    conn.commit()

def insert_scraped(c, conn, units, namedata, prereqs, coreqs, prohibs, recom, sems, overview, creditpoints, faculty, school, rawsemester, RAWprerequisites, RAWcorequisites, RAWprohibitions, RAWrecommendations, scaband, eftsl, studylevel, opentoexchange):
    for i in range(len(units)):
        if units[i] != '':
            insert_unit(c, conn, str(units[i]), str(namedata[i]), str(sems[i]), dblist_packer(prereqs[i]), dblist_packer(coreqs[i]), dblist_packer(prohibs[i]), str(recom[i]), str(overview[i]), str(creditpoints[i]), str(faculty[i]), str(school[i]), dblist_packer_shallow(rawsemester[i]), str(RAWprerequisites[i]), str(RAWcorequisites[i]), str(RAWprohibitions[i]), str(RAWrecommendations[i]), str(scaband[i]), str(eftsl[i]), str(studylevel[i]), str(opentoexchange[i]))


def dblist_packer(lst):
    parentlst = [[]]*len(lst)
    packedlst = ''
    for i in range(len(lst)):
        try:
            parentlst[i] = '#'.join(lst[i])
        except:
            pass
    packedlst = '&'.join(parentlst)
    return packedlst

def dblist_unpacker(packedlst):
    parentlst = packedlst.split('&')
    lst = [[]]*len(parentlst)
    for i in range(len(parentlst)):
        try:
            lst[i] = parentlst[i].split('#')
        except:
            pass
    return lst

def dblist_packer_shallow(lst):
    return '#'.join(lst)

def dblist_unpacker_shallow(packedlst):
    return packedlst.split('#')

