from selenium import webdriver
import urlparse
import os
import math
from slacker import Slacker
import datetime
import time
import sys


# 7/23/16 Nash


def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)


class Marker(object):
    def __init__(self, name, sitemap, location, screamer=False):
        self.name = name
        self.location = location
        self.map = sitemap
        self.screamer = screamer


class Pokemon(object):
    def __init__(self, location, name, markerdist, marker):
        self.location = location
        self.name = name
        self.distance = int(distance(self.location, markerdist))
        self.marker = marker

    def __cmp__(self, other):
        if hasattr(other, 'distance'):
            return self.distance.__cmp__(other.distance)


def setmarkers():
    # give a friendly name and the end of the url for location ie
    # https://pokevision.com/#/@34.00715285207903,-96.3775634765625 leave third value black and if you have slack
    # enabled add true to post to slack chat
    templist = (Marker("SEU Dorm", '@34.0061355,-96.37591119999999', "", True),
                Marker("SEU Pika Lot", '@34.0075886500593,-96.37261748313904', "", True),
                Marker("Casino", '@33.952295614343264,-96.41379475593567', ""),
                Marker("Travel Plaza Lot", '@33.95312327314485,-96.41885876655579', ""),
                Marker("1ST and Main", '@33.99229880851611,-96.37717723846436', "")
                )

    return templist


# add a slack api token here or set to none to disable
apitoken = None  # 
# list of pokenumbers you want to ignore see pokemon.txt for list, based off of line number ie line 1 is bulbasaur
ignoreList = (10, 11, 13, 14, 16, 17, 18, 19, 20, 46, 47, 48, 84, 85, 127)
base = "https://pokevision.com/#/"


def doit():
    fname = 'pokemon.txt'
    markerList = setmarkers()
    recentlist = []
    with open(fname) as f:
        content = f.readlines()

    with open("SeenList" + str(datetime.datetime.today().day) + "-" +
              str(datetime.datetime.today().month) + ".txt") as file:
        seenlist = file.readlines()

    for item in seenlist:
        itemlist = item.split(",")
        if itemlist[3].strip() > str(datetime.datetime.now() - datetime.timedelta(minutes=30)):
            recentlist.append(item)
            # print str(datetime.datetime.now() - datetime.timedelta(minutes=30))
    print recentlist
    if apitoken is not None:
        slack = Slacker(apitoken)
    pokemonlist = []
    # for location in latlonlist:
    #     browser.get(base+location)
    for marker in markerList:
        try:
            browser = webdriver.PhantomJS('E:/phantomjs-2.1.1-windows/bin/phantomjs.exe')
            browser.set_window_size(1024, 768)
            browser.implicitly_wait(5)
            browser.set_page_load_timeout(40)
            browser.get(base + marker.map)
            if 'maintenance' in browser.title.lower():
                raise Warning('Page is down')
            browser.find_element_by_class_name('home-map-scan').click()
            foo = browser.find_elements_by_class_name('leaflet-marker-icon')
            print marker.name
            for fee in foo:
                flag = False
                boo = fee.get_attribute('src')
                if 'marker-icon.png' in boo:
                    marker.location = (int(fee.location['y']), int(fee.location['x']))
                else:
                    path = urlparse.urlparse(boo).path
                    key = [x.split('.') for x in os.path.split(path)]

                    temp = Pokemon((fee.location['y'], fee.location['x']), content[int(key[1][0]) - 1],
                                   marker.location, marker.name)

                    datenow = str(datetime.datetime.now())

                    for item in recentlist:
                        splititem = item.split(",")
                        if temp.name.replace("\n", "") == splititem[0] and \
                                str(temp.distance).replace("\n", "") == splititem[2]:
                            flag = True
                            print True
                    if not flag:
                        # writes to a file so you can see historical data
                        with open("SeenList" + str(datetime.datetime.today().day) +
                                  "-" + str(datetime.datetime.today().month) + ".txt", "a") as myfile:
                            writestring = (temp.name + ", " + temp.marker + ", " + str(temp.distance) +
                                           ", " + datenow).replace("\n", "")
                            myfile.write(writestring + "\n")
                    if int(key[1][0]) not in ignoreList:
                        pokemonlist.append(temp)

            for pokemon in sorted(pokemonlist):
                # this distance sets how close a pokemon is note that this is based on screen size and not miles
                if pokemon.distance < 300:
                    msg = (pokemon.name + " " + str(math.floor(pokemon.distance))).replace("\n", "")
                    print pokemon.name + " " + str(math.floor(pokemon.distance))
                    if marker.screamer and apitoken is not None:
                        slack.chat.post_message('#pokebot', marker.name + " :: " + msg)
            del pokemonlist[:]
            browser.quit()
        except Exception, e:
            print marker.name + "  " + str(e)
            browser.quit()


if __name__ == "__main__":
    for i in range(24):
        doit()
        time.sleep(300)  # 600 every ten minutes
    sys.exit(0)
