from Scraper.handbookscraper import getallunits, scraper
from unitdbhandle import dblist_packer, dblist_packer_shallow, dblist_unpacker, dblist_unpacker_shallow

#scraper(['MTH2010'],2)
#print(scraper(['MTH2010'],5))
#x = [['S1-01-CLAYTON-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS'], ['OCT-MY-01-MALAYSIA-ON-CAMPUS', 'OCT12-CLAYTON-ON-CAMPUS', 'S1-01-CLAYTON-ON-CAMPUS', 'S1-01-MALAYSIA-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS', 'S2-01-MALAYSIA-ON-CAMPUS'], ['S1-01-CLAYTON-ON-CAMPUS', 'S1-01-MALAYSIA-ON-CAMPUS', 'S2-01-CLAYTON-ON-CAMPUS', 'S2-01-MALAYSIA-ON-CAMPUS', 'SSB-01-CLAYTON-ON-CAMPUS'], ['S2-01-CLAYTON-ON-CAMPUS']]

#y=x[0]

#print(y)
#pack = dblist_packer_shallow(y)
#print(pack)
#unpack = dblist_unpacker_shallow(pack)
#print(unpack)

getallunits()