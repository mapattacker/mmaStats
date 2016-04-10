from bs4 import BeautifulSoup
from urlparse import urlparse
import urllib, sqlite3, time, traceback

#############ENTER VARIABLES#####################
sleepTime = 1   #change sleep time per webpage query (in sec)
#################################################

start = time.time()
conn = sqlite3.connect('MMA.sqlite')
cur = conn.cursor()

#if database is empty, choose a fighter url link to start
cur.execute("SELECT COUNT(*) FROM fighter")
List1 = cur.fetchone()
for count in List1:
    if count == 0:
        starturl = raw_input("Input your first Sherdog MMA fighter URL: ")
        if starturl.find('http://www.sherdog.com/fighter/') == -1:  #ensure that input data is a valid fighter url
            print 'You did not put in a valid fighter url'
            break
        parse = urlparse(starturl).path
        cur.execute('''INSERT OR IGNORE INTO fighter(url) VALUES (?)''',(parse,))
        conn.commit()

#main code for scraping fighter's statistics
y = 0
counter = raw_input('number of fighters to scrape: ')
stopCounter = int(counter)

while True:
    try:
        #stop counter
        if y == stopCounter:
            print 'NUMBER OF FIGHTERS: ', after
            print 'NUMBERS SCANNED: ', scan, '\n'
            break
        y += 1
        
        #extract a url from databse
        cur.execute("SELECT url, id FROM fighter WHERE scanned IS NULL LIMIT 1")
        row = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM fighter")
        before = cur.fetchone()[0]

        #extract the html and cook it in beautiful soup
        url = 'http://www.sherdog.com{}'.format(row[0])
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')   #cooking the soup

        #find fighter's name
        names = soup.select('.fn')
        for name in names:
            Fname = name.getText()
            cur.execute("UPDATE fighter SET name=? WHERE url=?", (Fname, row[0]))

        #find total wins and losses
        winLost = soup.select('.counter')
        Win = winLost[0].getText()
        cur.execute("UPDATE fighter SET totalWins=? WHERE url=?",(Win, row[0]))
        Loss = winLost[1].getText()
        cur.execute("UPDATE fighter SET totalLosses=? WHERE url=?",(Loss, row[0]))

        #find total draws or no contests
        #4th counter is always a No Contest count
        try:
            NC = winLost[3].getText()
            cur.execute("UPDATE fighter SET totalNC=? WHERE url=?", (NC, row[0]))
        except:
            cur.execute("UPDATE fighter SET totalNC=0 WHERE url=?", (row[0],))

        #3rd counter can be either a Draw or No Contest count
        try:
            drawNC = soup.select('.card')[2]
            if str(drawNC).find('Draws') > 1:   #have to change soup into string in order to use find
                Draw = winLost[2].getText()
                cur.execute("UPDATE fighter SET totalDraws=? WHERE url=?", (Draw, row[0]))
            else:
                cur.execute("UPDATE fighter SET totalNC=? WHERE url=?", (Draw, row[0]))
                cur.execute("UPDATE fighter SET totalDraws=0 WHERE url=?", (row[0],))
        except:
            cur.execute("UPDATE fighter SET totalDraws=0 WHERE url=?", (row[0],))

        #find weight class
        weight = soup.select('h6 strong')
        Fweight = weight[0].getText()
        cur.execute("INSERT OR IGNORE INTO weightClass(weight) VALUES(?)", (Fweight,))
        cur.execute("SELECT id FROM weightClass WHERE weight=?", (Fweight,))
        weight_id = cur.fetchone()[0]
        cur.execute("UPDATE fighter SET weightClass_id=? WHERE url=?", (weight_id, row[0]))

        #find nationality
        try:
            nationality = soup.find(itemprop="nationality").get_text()
            cur.execute("INSERT OR IGNORE INTO nationality(country) VALUES(?)", (nationality,))
            cur.execute("SELECT id FROM nationality WHERE country=?", (nationality,))
            nationality_id = cur.fetchone()[0]
        except:
            cur.execute("INSERT OR IGNORE INTO nationality(country) VALUES('N/A')")
            cur.execute("SELECT id FROM nationality WHERE country='N/A'")
            nationality_id = cur.fetchone()[0]
        cur.execute("UPDATE fighter SET country_id=? WHERE url=?", (nationality_id, row[0]))

        #find birthday
        birthDate = soup.find(itemprop="birthDate").get_text()
        cur.execute("UPDATE fighter SET birthday=? WHERE url=?", (birthDate,row[0]))

        #find 1st fight date
        fightDate = soup.select('.sub_line')
        firstFight = fightDate[-2].get_text()
        FfirstFight = firstFight[-4:]
        cur.execute("UPDATE fighter SET First_Fight=? WHERE url=?", (FfirstFight,row[0]))

        #find last fight date
        lastFight = fightDate[0].get_text()
        FlastFight = lastFight[-4:]
        cur.execute("UPDATE fighter SET Last_Fight=? WHERE url=?", (FlastFight,row[0]))

        #find only url of fighters listed in fight history
        fightHistoryBelow = html.find('<h2>Fight History')
        html2 = html[fightHistoryBelow:] #remove all html above fight history table
        soup2 = BeautifulSoup(html2, 'html.parser')   #cooking the 2nd soup
        soup2 = soup2.select('div td a')  #extract elements <a> within <td> which is within <div>
                                        #which basically retains only fight history table

        for tag in soup2:
            url = str(tag.get('href'))
            if url.find('fighter') > 0 :  #only take fighter url (.../fighter/...)
                #put in fighters' url
                cur.execute("INSERT OR IGNORE INTO fighter(url) VALUES (?)",(url,))
                conn.commit()

                #put in fighter's relationship with others
                cur.execute("SELECT id FROM fighter WHERE url = ? LIMIT 1",(url,))
                toid = cur.fetchone()[0]
                cur.execute('INSERT OR IGNORE INTO relation(from_id, to_id) VALUES (?, ? )', (row[1], toid))

        #indicate that this url has been scraped
        cur.execute("UPDATE fighter SET scanned='S' WHERE url=?", (row[0],))

        #indicate how many new fighters were added
        cur.execute("SELECT COUNT(*) FROM fighter")
        after = cur.fetchone()[0]
        cur.execute("UPDATE fighter SET count_new=? WHERE url=?", ((after-before), row[0]))
        cur.execute("SELECT COUNT(*) FROM fighter WHERE scanned='S'")
        scan = cur.fetchone()[0]
        conn.commit()

        print y, Fname, after-before   #count, fighter name, number of new fighters added

        #sleep to prevent overloading website
        time.sleep(sleepTime)

    #exceptions
    except KeyboardInterrupt:
        print ' Script stopped by you'
        break
    except:
        traceback.print_exc()
        break

#calculate total fights
cur.execute("UPDATE fighter SET totalFights=(totalWins + totalLosses + totalDraws + totalNC)")
conn.commit()


end = time.time()
print 'Script completed in {} min'.format(round((end-start)/60,2))
