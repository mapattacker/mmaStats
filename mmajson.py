import sqlite3

conn = sqlite3.connect('MMA.sqlite')
cur = conn.cursor()

print 'Generating JSON data for D3 visualization...'
counter = int(raw_input('how many figher nodes? '))

cur.execute('''SELECT totalFights, id, url
                FROM fighter
                WHERE scanned IS NOT NULL AND totalFights IS NOT 0''')

#extract nodes based on no. specified by you
nodes = []
for row in cur:
    nodes.append(row)
    if len(nodes) == counter:
        break

#make json data
fileHandler = open('mma.js', 'w')

#create nodes into json
fileHandler.write('mmaJson = {"nodes":[\n')
count = 0
for row in nodes:
    if count > 0: fileHandler.write(',\n')
    fileHandler.write('{'+'"weight":'+str(0)+
                        ', "rank":'+str(row[0])+
                        ', "id":'+str(row[1])+
                        ', "url":"'+str('http://sherdog.com{}'.format(row[2]))+'"}')
    count += 1
fileHandler.write('],\n')

#create links between nodes into json
cur.execute('''SELECT DISTINCT from_id, to_id FROM relation''')
fileHandler.write('"links":[\n')
count = 0
for row in cur:
    if count > 0: fileHandler.write(',\n')
    fileHandler.write('{"source":'+str(row[0])+
                        ',"target":'+str(row[1])+
                        ',"value":3}')
    count += 1
fileHandler.write(']};')
fileHandler.close()
cur.close()

print 'Open force.html to view visualization'
