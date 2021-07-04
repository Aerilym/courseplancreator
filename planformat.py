import csv
import time

def planformat(order, semstart = 1, yearstart = 1):
    semesters = len(order)
    string = ''
    sem = semstart
    year = yearstart
    semdone = 0
    string += f'\n           +================COURSE====PLAN=================+'
    string += f'\n           |           |           |           |           |\n'
    for semlst in order:
        semdone += 1
        string += f'Semester {sem} |'
        for i in [0,1,2,3]:
            if len(semlst) == 4:
                unit = semlst[i]
                string +=  f'  {unit}  |'
            else:
                if i >= len(semlst):
                    unit = '       '
                else:
                    unit = semlst[i]
                string +=  f'  {unit}  |'
        if sem == 1:
            sem = 2
            string += f'\n           |           |           |           |           |'
            string += f'\n           |-----------+-----------+-----------+-----------|'
            if semdone < semesters:
                string += f'\n           |           |           |           |           |\n'
        elif sem == 2:
            sem = 1
            year += 1
            string += f'\n           |           |           |           |           |'
            string += f'\n    Year {year} |===============================================|'
            if semdone < semesters:
                string += f'\n           |           |           |           |           |\n'
    return string

def planformathtml(order, semstart = 1, yearstart = 1):
    semesters = len(order)
    string = ''
    sem = semstart
    year = yearstart
    semdone = 0
    string += f'<br>           +====================COURSE====PLAN=====================+'
    string += f'<br>           |         <sup> </sup>   |      <sup> </sup>      |     <sup> </sup>       |        <sup> </sup>    |<br>'
    for semlst in order:
        semdone += 1
        string += f'Semester {sem} |'
        for i in [0,1,2,3]:
            if len(semlst) == 4:
                unit = semlst[i]
                string +=  f'   <form!action=""!method="POST"!style="display:!inline;!margin:0px;!padding:0px;!width:0"><a!href="https://handbook.monash.edu/current/units/{unit}"!target="_blank">{unit}</a><a!href="#"!onclick="this.parentNode.submit();!return!false;"!style="color:!red;"><sup>x</sup></a><input!type="hidden"!name="submit_button"!id="unitform{unit}"!value="popunit{unit}"></form>  |'
            else:
                if i >= len(semlst):
                    string +=  f'       <sup> </sup>     |'
                else:
                    unit = semlst[i]
                    string += f'   <form!action=""!method="POST"!style="display:!inline;!margin:0px;!padding:0px;!width:0"><a!href="https://handbook.monash.edu/current/units/{unit}"!target="_blank">{unit}</a><a!href="#"!onclick="this.parentNode.submit();!return!false;"!style="color:!red;"><sup>x</sup></a><input!type="hidden"!name="submit_button"!id="unitform{unit}"!value="popunit{unit}"></form>  |'
        if sem == 1:
            sem = 2
            string += f'<br>           |    <sup> </sup>        |   <sup> </sup>         |       <sup> </sup>     |        <sup> </sup>    |'
            string += f'<br>           |-------------------------------------------------------|'
            if semdone < semesters:
                string += f'<br>           |    <sup> </sup>        |     <sup> </sup>       |      <sup> </sup>      |       <sup> </sup>     |<br>'
        elif sem == 2:
            sem = 1
            year += 1
            string += f'<br>           |         <sup> </sup>   |     <sup> </sup>       |      <sup> </sup>      |       <sup> </sup>     |'
            string += f'<br>    Year {year} |=======================================================|'
            if semdone < semesters:
                string += f'<br>           |       <sup> </sup>     |       <sup> </sup>     |       <sup> </sup>     |      <sup> </sup>      |<br>'
    string = string.replace(' ', '&nbsp')
    string = string.replace('!', ' ')
    return string

def planformatcsv(order, semstart = 1, yearstart = 2021):
    semesters = len(order)
    string = ''
    sem = semstart
    year = yearstart
    semdone = 0
    currentsem = semstart
    currentyear = yearstart
    table = []
    while order[-1] == [[], [], [], []]:
        order.pop()
    f = open('static/plans/plan.csv', 'w', newline='')
    writer = csv.writer(f)
    for sem in order:
        row = []
        if len(sem) < 4:
            while len(sem) < 4:
                sem.append('')
        row.append(f'Semester {currentsem}, {currentyear}')
        for i in range(len(sem)):
            row.append(sem[i])
        table.append(row)
        row = []
        if currentsem == 2:
            currentyear += 1
        currentsem = 1 if currentsem == 2 else 2
    writer.writerows(table)
    f.close()
    return table


#order = [['MTH2010', 'MTH2032', 'FIT1049', 'FIT2094'], ['FIT2081', 'FIT2001', 'FIT3175', 'ASP3051'], ['PHS2062', 'FIT2002', 'ASP3012', 'FIT2099'], ['PHS3201', 'PHS3000', 'FIT3047', 'FIT3077'], ['FIT3048', 'FIT3146', 'ASP3162'], ['PHS3101', 'ASP3231']]

#print(planformatcsv(order,semstart=2))