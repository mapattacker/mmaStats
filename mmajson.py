import sqlite3

conn = sqlite3.connect('MMA.sqlite')
cur = conn.cursor()

print 'Generating JSON data for D3 adjacient matrix visualization...'
counter = int(raw_input('how many figher? '))

cur.execute('''SELECT totalFights, id, name
                FROM fighter
                WHERE scanned IS NOT NULL AND totalFights IS NOT 0''')

##############extract nodes based on no. specified by you
nodes = []
for row in cur:
    nodes.append(row)
    if len(nodes) == counter:
        break

#make json data
fileHandler = open('mma.js', 'w')

#############create nodes into json
#note grouping is not specified
fileHandler.write('{"nodes":[\n')
fighterID = []
fighterCount = {}
count = 0
for row in nodes:
    if count > 0: fileHandler.write(',\n')
    fighterID.append(row[1])
    fighterCount[row[1]] = count
    fileHandler.write('{'+'"name": "'+str(row[2])+
                        '", "group":'+str(0)+
                        '}')
    count += 1
fileHandler.write('],\n')

###########create links between nodes into json
#note value is redundant

#only extract from sqlite the number of fighters u specified
inStatement = str(fighterID).replace('[','').replace(']','')
SQL = 'SELECT DISTINCT from_id, to_id, totalFights FROM relation JOIN fighter ON fighter.id = relation.from_id WHERE from_id IN ({}) AND to_id IN ({})'.format(inStatement, inStatement)
cur.execute(SQL)

fileHandler.write('"links":[\n')
count = 0
for row in cur:
    if count > 0: fileHandler.write(',\n')
    fileHandler.write('{"source":'+str(fighterCount[row[0]])+
                        ',"target":'+str(fighterCount[row[1]])+
                        ',"value":'+str(1)+'}')
    count += 1
fileHandler.write(']}')
fileHandler.close()
cur.close()

print 'JSON created.'
