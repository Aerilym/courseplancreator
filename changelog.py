import csv

def changelog():
    #categories = ['Quality of Life', 'Course Plan Creation', 'Front End', 'Back End', 'Uncategorised']
    #changetypes = ['Added', 'Changed']
    #versions = ['0.1.0-a','*']

    #Each item is [version, category, changetype, weight, description]
    changelogitems = []
    f = open('clog.csv', 'r', newline='')
    reader = csv.reader(f)
    for line in reader:
        changelogitems.append(line)
    versions = changelogitems[1][0].split(',')
    categories = changelogitems[1][1].split(',')
    changetypes = changelogitems[1][2].split(',')
    changelogitems = changelogitems[2:]
    currentversion = versions[0]

    #print(versions)
    #print(categories)
    #print(changetypes)
    #print(changelogitems)

    outlst = []
    for i in range(len(versions)):
        outlst.append([])
        for j in range(len(changetypes)):
            outlst[i].append([])
            for k in range(len(categories)):
                outlst[i][j].append([])
    outstr = ''

    for it in range(len(changelogitems)):
        item = changelogitems[it]
        version = item[0]
        category = item[1]
        if category not in categories:
            category = 'Uncategorised'
        changetype = item[2]
        weight = item[3]
        description = item[4]
        for i in range(len(outlst)):
            for j in range(len(changetypes)):
                for k in range(len(categories)):
                    if version == versions[i] and changetype == changetypes[j] and category == categories[k]:
                        if weight == 'Major':
                            outlst[i][j][k].insert(0,description)
                        elif weight == 'Minor':
                            outlst[i][j][k].append(description)


    for i in range(len(outlst)):
        if versions[i] == '*':
            outstr += f'<h3>Upcoming:</h3>'
        else:
            outstr += f'<h3>{versions[i]}:</h3>'
        outstr += '<ul>'
        for j in range(len(outlst[i])):
            if outlst[i][j] != [[]]*len(categories):
                changetxt = changetypes[j]
                if versions[i] == '*':
                    if changetypes[j] == 'Added':
                        changetxt = 'Adding'
                    elif changetypes[j] == 'Changed':
                        changetxt = 'Changing'
                else:
                    changetxt = changetypes[j]
                outstr += f'<li><h4>{changetxt}</h4></li>'
                outstr += '<ul>'
                for k in range(len(outlst[i][j])):
                    if outlst[i][j][k] != []:
                        outstr += f'<li>{categories[k]}</li>'
                        outstr += '<ul>'
                        for l in range(len(outlst[i][j][k])):
                            outstr += f'<li>{outlst[i][j][k][l]}</li>'
                        outstr += '</ul>'
                outstr += '</ul>'
        outstr += '</ul>'
    return outstr, currentversion


#changelog()