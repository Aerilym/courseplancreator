from copy import deepcopy, copy

def scrape_parse(scrapeddata):
    units = scrapeddata[0]
    data = scrapeddata[1]
    sems = scrapeddata[2]
    unitnames = scrapeddata[3]
    phrases = {'Rules Expand allEnrolment Rule', '&nbsp','RequisitesExpand all'}
    spacereplace = {'arrow_forward', 'keyboard_arrow_down', ';', '6 CP', '\n'}
    overview = scrapeddata[4]
    for i in range(len(overview)):
        cleanoverview = ''
        for char in overview[i]:
            if char.isalnum() or char == ' ':
                cleanoverview += char
        overview[i] = cleanoverview
            

    
    for i in range(len(data)):
        for phrase in phrases:
            data[i] = data[i].replace(phrase,'')
        for phrase in spacereplace:
            data[i] = data[i].replace(phrase,' ')
            data[i] = data[i].replace('   ',' ')
            data[i] = data[i].replace('  ',' ')
        data[i] = data[i].upper()
        prereqwords = {'PREREQUISITE','PREREQUISITES'}
        coreqwords = {'COREQUISITE', 'COREQUISITES'}
        prohibwords = {'PROHIBITION', 'PROHIBITIONS'}
        prereq_i = []
        coreq_i = []
        prohib_i = []
        for word in prereqwords:
            if word in data[i]:
                prereq_i.append(data[i].index(word))
        
        for word in coreqwords:
            if word in data[i]:
                coreq_i.append(data[i].index(word))
        
        for word in prohibwords:
            if word in data[i]:
                prohib_i.append(data[i].index(word))
        
        mixed_i = []
        if prereq_i != []:
            prereq_i = min(prereq_i)
            mixed_i.append(prereq_i)
        if coreq_i != []:
            coreq_i = min(coreq_i)
            mixed_i.append(coreq_i)
        if prohib_i != []:
            prohib_i = min(prohib_i)
            mixed_i.append(prohib_i)

        splits = []

        if prereq_i != [] and prohib_i == [] and coreq_i == []:
            splits.append(data[i][prereq_i:])
        elif prereq_i == [] and prohib_i != [] and coreq_i == []:
            splits.append(data[i][prohib_i:])
        elif prereq_i == [] and prohib_i == [] and coreq_i != []:
            splits.append(data[i][coreq_i:])
        elif prereq_i != [] and prohib_i != [] and prereq_i < prohib_i and coreq_i == []:
            splits.append(data[i][prereq_i:prohib_i])
            splits.append(data[i][prohib_i:])
        elif prereq_i != [] and prohib_i != [] and prereq_i > prohib_i and coreq_i == []:
            splits.append(data[i][prohib_i:prereq_i])
            splits.append(data[i][prereq_i:])
        elif prereq_i != [] and coreq_i != [] and prereq_i < coreq_i and prohib_i == []:
            splits.append(data[i][prereq_i:coreq_i])
            splits.append(data[i][coreq_i:])
        elif prereq_i != [] and coreq_i != [] and prereq_i > coreq_i and prohib_i == []:
            splits.append(data[i][coreq_i:prereq_i])
            splits.append(data[i][prereq_i:])
        elif prohib_i != [] and coreq_i != [] and prohib_i < coreq_i and prereq_i == []:
            splits.append(data[i][prohib_i:coreq_i])
            splits.append(data[i][coreq_i:])
        elif prohib_i != [] and coreq_i != [] and prohib_i > coreq_i and prereq_i == []:
            splits.append(data[i][coreq_i:prohib_i])
            splits.append(data[i][prohib_i:])
        elif prohib_i != [] and coreq_i != [] and prereq_i != []:
            if prereq_i < coreq_i < prohib_i:
                splits.append(data[i][prereq_i:coreq_i])
                splits.append(data[i][coreq_i:prohib_i])
                splits.append(data[i][prohib_i:])
            elif coreq_i < prereq_i < prohib_i:
                splits.append(data[i][coreq_i:prereq_i])
                splits.append(data[i][prereq_i:prohib_i])
                splits.append(data[i][prohib_i:])
            elif coreq_i < prohib_i < prereq_i:
                splits.append(data[i][coreq_i:prohib_i])
                splits.append(data[i][coreq_i:prereq_i])
                splits.append(data[i][prereq_i:])
            elif prohib_i < coreq_i < prereq_i:
                splits.append(data[i][prohib_i:coreq_i])
                splits.append(data[i][coreq_i:prereq_i])
                splits.append(data[i][prereq_i:])
            elif prohib_i < prereq_i < coreq_i:
                splits.append(data[i][prohib_i:prereq_i])
                splits.append(data[i][prereq_i:coreq_i])
                splits.append(data[i][coreq_i:])
        
        for l in range(len(splits)):
            splits[l] = splits[l].replace('PREREQUISITES','PREREQUISITE')
            if 'PREREQUISITE' in splits[l]:
                if splits[l][splits[l].index('PREREQUISITE')+12] != ':':
                    splits[l] = splits[l].replace('PREREQUISITE','PREREQUISITE:')
            if 'PROHIBITION' in splits[l]:
                splits[l] = splits[l].replace('PROHIBITIONS','PROHIBITION')
                if splits[l][splits[l].index('PROHIBITION')+11] != ':':
                    splits[l] = splits[l].replace('PROHIBITION','PROHIBITION:')
            if 'COREQUISITE' in splits[l]:
                splits[l] = splits[l].replace('COREQUISITES','COREQUISITE')
                if splits[l][splits[l].index('COREQUISITE')+11] != ':':
                    splits[l] = splits[l].replace('COREQUISITE','COREQUISITE:')
        data[i] = splits

    semphrases = {'Offerings Expand all',''}
    #semspacereplace = {''}
    for i in range(len(sems)):
        if sems[i] == 'NA':
            continue
        for phrase in semphrases:
            sems[i] = sems[i].replace(phrase,'')
        #for phrase in semspacereplace:
            #sems[i] = sems[i].replace(phrase,' ')
            #sems[i] = sems[i].replace('   ',' ')
            #sems[i] = sems[i].replace('  ',' ')
        sems[i] = sems[i].split('keyboard_arrow_down')
        semsclean = []
        for k in range(len(sems[i])):
            if sems[i][k].count(':') > 0:
                while sems[i][k].count(':') > 1:
                    sems[i][k] = sems[i][k].replace(':','',1)
                sems[i][k] = sems[i][k][sems[i][k].index(':')+10:]
            if 'ON-CAMPUS' in sems[i][k]:
                sems[i][k] = sems[i][k].replace(' ','')
                semsclean.append(sems[i][k])
        sems[i] = semsclean
        


#dataset = [['MTH2010', 'FIT1045', 'FIT2094', 'ASP2062'], ['Rules Expand allEnrolment Rulekeyboard_arrow_downPREREQUISITE:&nbsp;Students must have passed MTH1030, MTH1035, or MTH1040 with a mark of at least 60. Exceptions for students who passed these units with a mark in the range of 50 to 59 can be made with permission from the unit co-coordinator based on a diagnostic test. PROHIBITION:&nbsp;ENG2005, ENG2091, MTH2015 ', 'Rules Expand allEnrolment Rulekeyboard_arrow_downPrerequisite: VCE Mathematics Methods or Specialist Mathematics units 3 &amp; 4 with a study&nbsp;score of 25 or MTH1010.Prohibitions:&nbsp;FIT1029, FIT1053 ', 'Rules Expand allEnrolment Rulekeyboard_arrow_downPrerequisites:&nbsp;One of FIT1040, FIT1045, FIT1048, FIT1051, FIT1053 or equivalent introductory programming unit Prohibition:&nbsp;FIT1004, FIT3171, FZA2094 ', 'Rules Expand allEnrolment Rulekeyboard_arrow_downCOREQUISITE: Recommended: (MTH2010&nbsp;or MTH2015&nbsp;or&nbsp;ENG2005) and (MTH2032 or MTH2040)\nNote: supporting mathematics studies are required for progression towards the Astrophysics and Physics majors PREREQUISITE: One unit (six credit points) of physics at first-year level, and MTH1030&nbsp;or MTH1035 or&nbsp;ENG1005&nbsp;or equivalent '], ['Offerings Expand allS1-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:First semester Attendance mode:On-campus S2-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:Second semester Attendance mode:On-campus ', 'Offerings Expand allOCT-MY-01-MALAYSIA-ON-CAMPUSkeyboard_arrow_downLocation:Malaysia Teaching period:October intake teaching period, Malaysia campus Attendance mode:On-campus OCT12-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:October 12 week teaching period Attendance mode:On-campus S1-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:First semester Attendance mode:On-campus S1-01-MALAYSIA-ON-CAMPUSkeyboard_arrow_downLocation:Malaysia Teaching period:First semester Attendance mode:On-campus S2-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:Second semester Attendance mode:On-campus S2-01-MALAYSIA-ON-CAMPUSkeyboard_arrow_downLocation:Malaysia Teaching period:Second semester Attendance mode:On-campus ', 'Offerings Expand allS1-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:First semester Attendance mode:On-campus S1-01-MALAYSIA-ON-CAMPUSkeyboard_arrow_downLocation:Malaysia Teaching period:First semester Attendance mode:On-campus S2-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:Second semester Attendance mode:On-campus S2-01-MALAYSIA-ON-CAMPUSkeyboard_arrow_downLocation:Malaysia Teaching period:Second semester Attendance mode:On-campus SSB-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:Summer semester B Attendance mode:On-campus ', 'Offerings Expand allS2-01-CLAYTON-ON-CAMPUSkeyboard_arrow_downLocation:Clayton Teaching period:Second semester Attendance mode:On-campus '], ['Multivariable calculus', 'Algorithms and programming fundamentals in python', 'Databases', 'Introduction to astrophysics'], ['Functions of several variables, partial derivatives, extreme values, Lagrange multipliers. Multiple integrals, line integrals, surface integrals. Vector differential calculus; grad, div and curl. Integral theorems of Gauss and Stokes. ', 'This unit introduces programming fundamentals and the Python language to students. The unit provides a foundational understanding of program design and implementation of algorithms to solve simple problems. Fundamental programming control structures, built in and complex datatypes and mechanisms for modularity will be presented in Python. Topics covered will include � For more content click the Read more button below.\nThis unit introduces programming fundamentals and the Python language to students. The unit provides a foundational understanding of program design and implementation of algorithms to solve simple problems. Fundamental programming control structures, built in and complex datatypes and mechanisms for modularity will be presented in Python.\nTopics covered will include basic input and output, program control structures, basic data structures and modular program structure. Problem-solving strategies and techniques for algorithm development, iteration and recursion, algorithm efficiency and the limitations of algorithms will be introduced.\nRead more', 'This unit will provide an introduction to the concepts of database design and usage and the related issues of data management. Students will develop skills in planning, designing, and implementing a data model using an enterprise-scale relational database system (Oracle). Methods and techniques will also be presented to populate, retrieve, � For more content click the Read more button below.\nThis unit will provide an introduction to the concepts of database design and usage and the related issues of data management. Students will develop skills in planning, designing, and implementing a data model using an enterprise-scale relational database system (Oracle). Methods and techniques will also be presented to populate, retrieve, update and implement integrity features on data in the implemented database system.\nRead more', 'An introduction to contemporary astrophysics, with a focus on the range of physical processes which shape the universe and the objects within. You will study the generation, propagation and absorption of radiation; star and planet formation; celestial mechanics; accretion disks; interiors of stars and nucleosynthesis; post main sequence evolution; compact � For more content click the Read more button below.\nAn introduction to contemporary astrophysics, with a focus on the range of physical processes which shape the universe and the objects within. You will study the generation, propagation and absorption of radiation; star and planet formation; celestial mechanics; accretion disks; interiors of stars and nucleosynthesis; post main sequence evolution; compact objects and black holes; the Milky Way; galaxies and cosmology.  Laboratory work will include analytic and computer-based exercises, involving research-grade data and numerical codes.\nRead more'], ['6', '6', '6', '6'], ['Faculty of Science', 'Faculty of Information Technology', 'Faculty of Information Technology', 'Faculty of Science'], ['School of Mathematics', 'Faculty of Information Technology', 'Faculty of Information Technology', 'School of Physics and Astronomy'], [], [], [], [], [], ['1', '2', '2', '2'], ['0.125', '0.125', '0.125', '0.125'], ['Undergraduate', 'Undergraduate', 'Undergraduate', 'Undergraduate'], ['Yes', 'Yes', 'Yes', 'Yes']]

#x = scrape_parse(dataset)
#print(x)
#print(dataset)
