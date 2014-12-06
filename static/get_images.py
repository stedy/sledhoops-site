import csv
import urllib2

ids = []
with open('../lookups.txt', 'rb') as lt:
    ltreader = csv.reader(lt, delimiter=',', quotechar='"')
    for row in ltreader:
        ids.append(row[0])

for id in ids:
    id = id.lstrip("0")
    url = "http://hosted.stats.com/cbk/logos/cbk_50x33/" + id + ".png"
    print url
    newfile = id + ".png"
    f = open(newfile, 'wb')
    try:
        f.write(urllib2.urlopen(url).read())
        f.close()
    except IOError:
        pass
