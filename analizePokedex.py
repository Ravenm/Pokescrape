import datetime

with open("SeenList" + str(datetime.datetime.today().day) + "-" + str(datetime.datetime.today().month) + ".txt") as f:
        content = f.readlines()

markerlist = {"SEU Dorm": {}, "SEU Pika Lot": {}, "Casino": {}, "Travel Plaza Lot": {}, "1ST and Main": {}}

for line in content:
    line.replace("\n", '')
    temp = line.split(",")
    # print temp
    foo = temp.pop(1).strip()
    boo = temp.pop(0).strip()
    markerlist[foo].setdefault(boo, []).append(temp)

for key in markerlist:
    print key
    for pokemon in markerlist[key]:
        print "\t found:  " + str(len(markerlist[key][pokemon])) + "  " + pokemon
