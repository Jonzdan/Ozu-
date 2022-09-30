#name: Jonathan Deng
#id: jdeng2
import random, copy, time, itertools, string, tkinter, sys
from os import path
from cmu_112_graphics import *
from tkinter import *
#methods: redraw, mousemoved, mousepressed, keypressed, timerfired, appstarted,
#this game is heavily inspired by Osu!
#https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
#basic tkinter stuff : https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_polygon.html
def readFile(path):
    with open(path, "rt") as f:
        return f.read()
#https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def writeFile(path, contents):
    with open(path, 'wt') as f:
        f.write(contents)
#https://www.guru99.com/python-check-if-file-exists.html
def findIfHighScoreIsIn(filename):
    if path.exists(filename): #if there is a high score file
        return True
    return False
def findIfDirectoryExists(filename):
    if path.exists(filename):
        return True
    return False
def convertBinarySongIntoBPM(filename, app): #for later maybe
    pass
def loginInfo(app):
    app.__users = {}
    if not findIfDirectoryExists('User.txt'):
        writeFile('User.txt','')
    
    
    app.username = app.getUserInput('Username:')
    if app.username == None:
        exit()
    txt = readFile('User.txt')
    for line in txt.splitlines():
        temp = line.split(' ')
        user = temp[0]
        password = temp[1]
        app.__users[user] = password
    app.username = app.username
    if app.username not in app.__users:
        app.password = app.getUserInput('User not detected: Please register a password - Only numbers')
        if app.password == None:
            exit()
        while not app.password.isnumeric():
            app.getUserInput('Please include a valid password')
        app.__users[app.username] = app.password
    else:
        app.password = app.getUserInput('User detected: Input password')
        tries = 3
        while app.password == None:
            if tries == 0:
                exit()
            app.password = app.getUserInput('Not a valid password: Try Again')
            tries -= 1
        tries = 3
        while app.password != app.__users[app.username]:
            if tries == 0:
                exit()
            app.password = app.getUserInput('Wrong password: Try again \n ' + str(tries) + ' left')
            tries -= 1
    txt = readFile('User.txt')
    if app.username not in txt:
        writeFile('User.txt', txt + app.username.strip() +' ' +  app.password + '\n')
    if not findIfHighScoreIsIn('Highscore.txt'):
        writeFile('Highscore.txt', 'TEMP -1111111111 0.00%')

def appStarted(app):
    mainMenu(app)
    loginInfo(app)
    #credit: https://www.python-course.eu/tkinter_canvas.php
    

def mainMenu(app):
    app.mouseMovedDelay = 1
    restartMap(app)
    app.keyIsPressed = False #this sets the other thing to a 
    app.spacex = app.width/15
    app.password = ''
    #credit : https://i.imgur.com/Ku1vPFa.jpeg 
    #reddit user: https://www.reddit.com/r/osugame/comments/7jzq4b/osuxmas_seasonal_backgrounds/
    #imgur page: https://imgur.com/a/lgpRM
    url = 'https://i.imgur.com/Ku1vPFa.jpeg'
    app.mainImage = app.loadImage(url)
    #https://auth0.com/blog/image-processing-in-python-with-pillow/
    app.mainImage = app.mainImage.resize((1440, 810))
    url = 'https://cdn.wallpapersafari.com/82/11/2Gh1QR.jpg'
    #https://wallpapersafari.com/w/2Gh1QR
    app.scoreImage = app.loadImage(url)
    app.scoreImage = app.scoreImage.resize((1440,810))
    app.spacey = app.height/10
    app.add = 1000
    app.hardmode = False
    app.easymode = False
    app.midmode = False
    app.play = False
    app.instructions = False
    app.calculateGrade = False
def generateNodeBoard(app): #represent 0:nothing 1:circle 2:tracker 3:?

    for row in range(1,8):
        tempList = []
        for col in range(1,15):
            ri = random.randint(1,10)
            tempList.append([0, app.outline, ri])  #ri is the edge weight
        app.nodeBoard.append(tempList)

def restartMap(app):
    app.letter = ''
    app.outline = 100
    app.multiplier = 1
    app.iterativeNode = 0
    app.numCircle = 1
    app.order = 1
    app.hits = 1
    app.h300 = 0
    app.h100 = 0
    app.totalhits = 1    
    app.time = 0
    app.pause = False
    app.dots = [] #list of all the circles coming up
    app.r = 30
    app.gameOver = False
    app.timerDelay = 1 
    app.score = '0000001000'
    app.lives = 100 #-10 per second depending on difficulty
    app.livesLost = 10
    app.timer = 18000
    app.mousex, app.mousey = 0,0
    app.mcxy = []
    app.esc = False
    app.miss = False
    app.endNode = None
    app.trackerStart = None
    app.nodeBoard = []
    app.trackerList = []
    app.path = [] #stored in (drownode, dcolnode()
    app.visited = []
    app.cheat = None
    app.notVisited = []
    app.distance = {}
    app.prev = {}
    app.missedInfo = []
    app.bombList = []
    app.previousHitCircle = (-100,-100)
    app.loseLives = True

    generateNodeBoard(app)
    #] #list of all options, combined into one
    app.actualMap = []

def mouseMoved(app, event):
    app.mousex, app.mousey = event.x, event.y
    if not app.miss:
        while len(app.mcxy) > 0:
            app.mcxy.pop(0)
        app.mcxy.append((event.x, event.y))
    #we can declare our endnode here, finding the closest node
    findClosestNodeToMousePointer(app)

def findClosestNodeToMousePointer(app):
    if 0<=(app.mousex-90)//app.spacex<len(app.nodeBoard[0]) and 0<=(app.mousey-200)//app.spacey<len(app.nodeBoard):
        app.endNode =((app.mousey-200)//app.spacey, (app.mousex-90)//app.spacex) 

def checkIfCollision(app):
    node = None
    #closest node to mouse at the moment
    if 0<=(app.mousex-90)//app.spacex<len(app.nodeBoard[0]) and 0<=(app.mousey-200)//app.spacey<len(app.nodeBoard):
        node = ((app.mousey-200)//app.spacey, (app.mousex-90)//app.spacex) 
    #since our dijskra is at path[0], we then compare
    if len(app.path) > 0 and node == app.path[0]: #same node
        calculateHighscore(app)
        app.gameOver = True

def mousePressed(app, event):
    if app.gameOver == True:
        if app.width-500<=event.x<=app.width-20 and app.height-150<=event.y<=app.height-50:
            mainMenu(app)
    if not app.play: #
        x = event.x
        y = event.y
        if (app.width*2/6 <= x<=app.width*5/6-50 and app.height*1/5<=y<=app.height*2/5) or (app.width*5/6-50<=x<=app.width*5/6 and (app.height*2/5-y) + (app.width*5/6-x) <= 50):
            #first option
            app.play = True
        elif app.width*2/6 <= x <= app.width*5/6 and app.height*2/5+10<= y <=app.height*3/5:
            app.instructions = True
        elif app.width*2/6 <= x <= app.width*5/6 and app.height*3/5+10<=y<=app.height*4/5 or (app.width*5/6-50<=x<=app.width*5/6 and app.height*4/5-10-y + app.width*5/6-x <= 50):
            exit()
    elif app.keyIsPressed == False and not app.esc and app.play:
        if app.width*1.5/7<=event.x<=app.width*5.5/7 and app.height*1.7/8<=event.y<=app.height*3.2/8:
            app.easymode = True 
            app.keyIsPressed = True
        elif app.width*1.5/7<=event.x<=app.width*5.5/7 and app.height*3.7/8<=event.y<=app.height*5.2/8:
            app.midmode = True
            app.keyIsPressed = True
        elif app.width*1.5/7<=event.x<=app.width*5.5/7 and app.height*5.7/8<=event.y<=app.height*7.2/8:
            app.hardmode = True
            app.keyIsPressed = True
    if app.esc:
        if app.width*2/12<=event.x<=app.width*10/12:
            if app.height*2/8<=event.y<=app.height*3/8:
                app.esc = False
                app.keyIsPressed = True
            elif app.height*4/8<=event.y<=app.height*5/8:
                app.keyIsPressed = True
                restartMap(app)
            elif app.height*6/8<=event.y<=app.height*7/8:
                mainMenu(app)
    
            
#
def dist(x0,y0,x1,y1):
    return ((x1-x0)**2+(y1-y0)**2)**0.5 

def changeScore(app, row, col, amount):
    app.nodeBoard[row][col][0] = 0
    loc = findLocation(app)
    #weve gotten the location of the first int
    length = len(app.score)
    tempInt = int(app.score[loc:length])
    tempInt += app.add*(app.multiplier//amount) #maybe create a miss multipler later
    app.score = app.score[:loc] + str(tempInt)
    if len(app.score) > length:
        app.score = app.score[1:]
    if app.lives + 10 > 100:
        app.lives = 100
    else:
        app.lives += 10
    app.multiplier += 1
    app.hits += 1

def keyPressed(app, event):
    if event.key == 'r':
        mainMenu(app)
    if not app.play:
        return
    if event.key == 'Escape':
        app.esc = not app.esc
    if event.key == 'p':
        app.pause = not app.pause
    if event.key == 'l':
        app.loseLives = not app.loseLives
    elif event.key == 's':
        doStep(app)
    if event.key == 'c':
        app.cheat = app.getUserInput('Enter the accuracy (decimals): ')
        if app.cheat != None:
            app.gameOver = True
            calculateGrade(app)
    if event.key == 'z' or event.key == 'x' and app.keyIsPressed:
        temp = copy.deepcopy(app.nodeBoard)    
        app.totalhits += 1
        for row in range(len(app.nodeBoard)):
            for col in range(len(app.nodeBoard[row])):
                x = col * app.spacex + 90
                y = row * app.spacey + 200
                if app.nodeBoard[row][col][0] == 1 and dist(x,y,app.mousex, app.mousey) <= app.r: #so this is a match and a circle
                    #check if the order corresponds to num matbe later
                    if 0<=app.nodeBoard[row][col][1] <=20: #full points
                        changeScore(app, row, col,1)
                        app.h300 += 1
                        app.previousHitCircle = (row,col)
                        app.actualMap.remove((row, col))
                    elif 20<app.nodeBoard[row][col][1] <=40: #earn less
                        changeScore(app, row, col,2)
                        app.h100 += 1
                        app.actualMap.remove((row, col))
                        app.previousHitCircle= (row,col)
                    break
                elif app.nodeBoard[row][col][0] == 2 and x-app.r<=app.mousex<=x+app.r and y-app.r<=app.mousey<=y+app.r: #if the bomb is hit  
                    for i in range(len(app.bombList)):
                        if app.bombList[i] == (row,col):
                            app.bombList.pop(i)
                            break
                    app.lives /= 2
                    app.score = '0000000000'
                    break

        if temp == app.nodeBoard: #is is the same board...
            checkMiss(app)
            app.miss = True
            app.mcxy.append((app.mousex, app.mousey))
            xdist = app.mousex - app.previousHitCircle[1]
            ydist = app.mousey - app.previousHitCircle[0]
            app.missedInfo.append((app.mousex, app.mousey, xdist, ydist))
    if app.gameOver or app.pause:
        return

def findLocation(app):
    loc = - 1
    for i in range(len(app.score)):
        if app.score[i] != '0':
            loc = i
            break
    return loc

def checkMiss(app):
    app.totalhits += 1
    #find location where the first digit of whatever is not a string
    loc = findLocation(app)
    #weve gotten the location of the first int
    length = len(app.score)
    tempInt = int(app.score[loc:length])
    if not int(app.score) - app.add*app.multiplier < 0:
        tempInt -= app.add*app.multiplier #maybe create a miss multipler later
    app.score = app.score[:loc] + str(tempInt)
    if len(app.score) > length:
        app.score = app.score[1:]
    if len(app.score) < length:
        app.score = app.score + '0'
    if app.lives - 10<= 0:
        calculateHighscore(app)
        calculateGrade(app)
        app.gameOver = True
    else:
        app.lives -= 10
    app.multiplier = 1

def doStep(app):
    #the time it takes for each cell to disappear is bound to each cell individually
    if app.keyIsPressed:
        checkIfCollision(app)
        if app.hardmode:
            app.livesLost = 10
            app.r = 30
        elif app.midmode:
            app.livesLost = 20
            app.r = 40
        elif app.easymode:
            app.livesLost = 30
            app.r = 50
        if app.time % 50 == 0:
            app.lives -= 1
        if app.time%200 == 0:
            app.miss = False
        app.time += 1
        if app.loseLives == False:
            app.lives = 100
        #replace this with own method that is called on the list
        if app.livesLost - 1 >= 5:
            app.livesLost -= 1
        app.timer -= app.timerDelay
        #remove lives each second
        if app.time%(app.livesLost//5) == 0: #every .1 s, decrease outline
            i = 0
            while i < len(app.actualMap):    
                row,col = app.actualMap[i]
                if app.nodeBoard[row][col][0] == 1:
                    app.nodeBoard[row][col][1] -= 10
                if app.nodeBoard[row][col][1] <= 0:
                    app.actualMap.pop(i)
                    app.nodeBoard[row][col][0] = 0
                    checkMiss(app)
                    i -= 1
                i+=1
        if app.time%(app.livesLost*10) == 0: #every second, we create a bomb
            while True:
                randx = random.randint(0,13)
                randy = random.randint(0,6)
                if app.nodeBoard[randy][randx][0] == 0:
                    app.nodeBoard[randy][randx][0] = 2 #2 is a bomb
                    app.bombList.append((randy, randx))
                    break
                    #maybe a bomb list
        if len(app.bombList) > 3: #remove a bomb
            app.bombList.pop()
        if app.time%app.livesLost == 0: #every __s, a circle is created at a random node
            oneOrTwo = random.random() #some floating number between 0-1
            missedPercentage = len(app.missedInfo) / 100
            if oneOrTwo > missedPercentage: #so if we don't go with the missed List, and stick to random generation
                while True:
                    randx = random.randint(0,13)
                    randy =  random.randint(0,6)
                    if app.nodeBoard[randy][randx][0] == 0: #empty node
                        app.nodeBoard[randy][randx][0] = 1 #a circle for now
                        app.nodeBoard[randy][randx][1] = app.outline
                        app.actualMap.append((randy, randx))
                        break
            else: 
                #everytime this is called, we want the game to get harder
                #we have the xdist from the previous hit circle, so we can use that to randomly generate something...
                #randomly generate a number based on the size of the list
                rand = random.randint(0, len(app.missedInfo)-1)
                #so as our list grows bigger, if we have similar misses, there is a higher chance of selecting that miss information
                #so it would theoretically get harder
                #so rand is now our index
                #so if to generate the nodes, its row * spacex + margin
                #so -margin then //spacex to find location
                temp = app.missedInfo[rand] #since missedInfo stores a list...
                xloc = (temp[0]-90)//app.spacex 
                yloc = (temp[1]-200)//app.spacey
                xdist = int(temp[2])
                ydist = int(temp[3])
                #now we have our variables
                #find the new location thru a while loop
                #add it
                time = 0
                while True and xdist != 0 and ydist != 0:
                    randx = random.randrange(0, xdist)//app.spacex #so we add nodes
                    randy = random.randrange(0, ydist)//app.spacey
                    rand1 = random.randint(0,1)
                    n = 0
                    if rand1 == 0:
                        n = -1
                    elif rand1 == 1:
                        n = 1
                    newx = int(xloc + randx*n)
                    newy = int(yloc + randy*n)
                    time += 1
                    if 0<=newy<len(app.nodeBoard) and 0<=newx<len(app.nodeBoard[0]):
                        if app.nodeBoard[newy][newx][0] == 0:
                            app.nodeBoard[newy][newx][0] = 1 #a cricle
                            app.nodeBoard[newy][newx][1] = app.outline
                            app.actualMap.append((newy, newx))
                            break
                    if time == 10000:
                            return "ERROR"
#https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/ - i've updated it to fit my program
        if app.time%300 == 0 and len(app.trackerList) > 0: #update dijstrakas algorithim every 3 s (or path)
            app.prev = {}
            app.visited = []
            app.path = []
            #update starting point
            for row in range(len(app.nodeBoard)):
                for col in range(len(app.nodeBoard[0])):
                    if app.nodeBoard[row][col][0] == 0: #if it is empty
                        app.distance[(row,col)] = sys.maxsize
                        app.notVisited.append((row,col))
                    elif app.nodeBoard[row][col][0] == 3: #if it is the tracker
                        app.distance[(row,col)] = 0
                        app.notVisited.append((row,col))
                        app.trackerStart = (row,col)
            dijaskra(app) #this should give us a path in prev
            #now to calculate the shortest path, and stick with it
            findShortest(app)
        if app.time%app.livesLost == 0:
            app.path = app.path[1:]
        if len(app.trackerList) == 0:  #currently, I can only do one tracker
            #the way I store the algorithim's information only supports one
            #change this to replace starting point each time
            while True:
                col = random.randint(0,13)
                row = random.randint(0,6)
                if app.nodeBoard[row][col][0] == 0:
                    app.nodeBoard[row][col][0] = 3 # a tracker
                    app.trackerList.append((row, col))
                    break 

def findShortest(app): #this assumes the prev has been initialized
    #utilize prev's keys which are the new values and values are the previous node
    if len(app.prev) > 0 and app.endNode in app.prev:
        app.path.insert(0, app.endNode)
        previousNode = app.prev[app.endNode]
        while previousNode != app.trackerStart:
            app.path.insert(0,previousNode)
            previousNode = app.prev[previousNode]
        app.path.insert(0, app.trackerStart)
        #once the loop ends, we have our path

#thanks to :https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/
def dijaskra(app):
    if len(app.notVisited) == 0: #base case
        return
    if len(app.notVisited) == 1:
        app.visited = app.notVisited.pop()
    if app.endNode == app.iterativeNode: #we have found the endNode
        return
    else: #recursive case
        minNode = 0
        minEdge = sys.maxsize
        for elem in app.distance:
            if elem in app.notVisited: #if the node isn't visited
                if app.distance[elem] < minEdge:
                    minEdge = app.distance[elem]
                    minNode = elem
        #so now we've found the smallest distance that hasn't been visited
        #have temp list that holds each legal node
        app.iterativeNode = minNode
        try:
            for drow, dcol in [(1,0),(-1,0),(0,1),(0,-1)]:
                row, col = minNode[0],minNode[1]
                #if this new node is a legal node
                if 0<=row+drow<len(app.nodeBoard) and 0<=col+dcol<len(app.nodeBoard[0]) and (row+drow, col+dcol) in app.distance:
                    currentWeight = app.nodeBoard[row+drow][col+dcol][2]
                    neighDist = app.distance[(row+drow, col+dcol)] #neighDist is sys.maxsize if unvisited
                    if neighDist > currentWeight + minEdge: #basically unvisited
                        app.distance[(row+drow, col+dcol)] = currentWeight + minEdge #change sys.maxsize to sum of nodes (the path)
                        app.prev[(row+drow, col+dcol)] = (row, col) #new to old
        except: 
            print('oops')
        app.visited.append((row,col))
        app.notVisited.remove((row,col))
        dijaskra(app)
          
    
#this is where generation of the map happens
def timerFired(app):
    if app.esc:
        app.keyIsPressed = False
        return
    if app.pause:
        return
    if app.gameOver:  
        return
    if app.timer <= 0: #time runs out, ending the game
        app.gameOver = True
    if app.lives <= 0:
        calculateHighscore(app)
        calculateGrade(app)
        app.gameOver = True
    doStep(app)

def calculateHighscore(app):
    txt = readFile('Highscore.txt').splitlines() #get the info in a list of lines
    if len(txt) == 0:
        txt = [txt]
    #add the new info to the list
    difficulty = ''
    if app.hardmode:
        difficulty = '(hard)'
    elif app.easymode:
        difficulty = '(easy)'
    elif app.midmode:
        difficulty = '(medium)'
    txt.insert(0, app.username + difficulty + ' ' + app.score  +  " %.2f"%((app.hits/app.totalhits)*100) + "%")
    #now just selection sort
    for i in range(len(txt)):
        for j in range(i+1, len(txt)):
            score1 = int(txt[i].split(' ')[1])
            score2 = int(txt[j].split(' ')[1])
            if score2 > score1:
                temp = txt[i]
                txt[i] = txt[j]
                txt[j] = temp
    if len(txt) > 10:
        txt.pop()
    bigString = ''
    for i in range(len(txt)):
        
        info = (txt[i]).split(' ')
        bigString += info[0] + ' ' + info[1] + ' ' + info[2] + '\n'
    writeFile('Highscore.txt', bigString)

def calculateGrade(app): #use score and the percentage to calculator letter gradeasdasd
    acc = app.hits/app.totalhits
    if app.cheat != None:
        acc = app.cheat
    if int(acc) == 1:
        app.letter = 'SS'
    elif (acc) > .90 and (app.h100/app.totalhits) < .01:
        app.letter = 'S'
    elif acc > .9:
        app.letter = 'A'
    elif (acc) > .8:
        app.letter = 'B'
    elif (acc) > .6:
        app.letter = 'C'
    else:
        app.letter = 'D'

def startMenu(app, canvas):
    if app.instructions:
        canvas.create_rectangle(app.width*1/6, app.height*1/8-10, app.width*5/6, app.height*7/8+10, fill='gray')
        message = '''Welcome to OZUE! \n The objective of this game is to get as much points as possible in a certain amount of time. 
                    \n To achieve points, press ''z'' or ''x'' when your cursor is on a red circle. 
                    \n However, there will be a white outline that appears around the circle. 
                    \n Pressing the red circle at the right time grants the most points. 
                    \n Your goal is try and hit the red circles when the outline is at its smallest. 
                    \n Otherwise, the amount of points received will be reduced, or you may even lose points if the outline is still massive.
                    \n Beware of bombs! Pressing z or x on them will cause you to lose all your points and half of your hp.
                    \n Although it is red, it is easy to distinguish from other circles
                    \n Additionally, beware of a tracker that appears! If your mouse cursor gets hit by it, it is game over.
                    \n As the game progresses, the game will get harder.
                    \n To go on easy mode, press l for infinite lives.
                    \n Press p to pause. Press s to continue the iteration one time while paused.
                    \n Press r to restart the game.
                    \n Press c to manipulate accuracy and end the game
                    \n Press Esc to pull up the esc menu. '''
        canvas.create_text(app.width/2, app.height/2, text=message, fill='ghost white', font='Times 14 bold')
    elif not app.play:
        canvas.create_polygon(app.width*2/6, app.height*1/5, app.width*5/6 - 50, app.height*1/5+10, app.width*5/6, app.height*2/5, app.width*2/6, app.height*2/5, fill='lightslateblue',outline='gray74',activefill='tomato4')
        canvas.create_polygon(app.width*2/6, app.height*2/5+10, app.width*5/6, app.height*2/5+10, app.width*5/6, app.height*3/5, app.width*2/6, app.height*3/5, fill='lightslateblue',outline='gray75', activefill='tomato4')
        canvas.create_polygon(app.width*2/6, app.height*3/5+10, app.width*5/6, app.height*3/5+10, app.width*5/6-50, app.height*4/5-10, app.width*2/6, app.height*4/5, fill='lightslateblue',outline='gray74',activefill='tomato4')
        canvas.create_oval(app.width*1/6, app.height*1/5, app.width*1/2, app.height*4/5, fill='salmon', outline ='lavender', width=10)
        canvas.create_text(app.width* 2/6, app.height/2, text='OZUE!', font='Times 80 bold', fill='snow')
        canvas.create_text(app.width*3.8/6, app.height*1.5/5, text='Play', fill='snow', font='Times 40 bold')
        canvas.create_text(app.width*3.8/6, app.height*2.5/5, text='Instructions', fill='snow', font='Times 40 bold')
        canvas.create_text(app.width*3.8/6, app.height*3.5/5, text='Exit', fill='snow', font='Times 40 bold')
    
    elif app.play:
        drawOptions(app, canvas)
    
def drawOptions(app, canvas):

    canvas.create_rectangle(app.width*1.5/7, app.height*1.7/8, app.width*5.5/7, app.height*3.2/8, fill='antique white')
    canvas.create_rectangle(app.width*1.5/7, app.height*3.7/8, app.width*5.5/7, app.height*5.2/8, fill='antique white')
    canvas.create_rectangle(app.width*1.5/7, app.height*5.7/8, app.width*5.5/7, app.height*7.2/8, fill='antique white')
    canvas.create_text(app.width/2, app.height*1/8, text='DIFFICULTY LEVELS', fill='snow', font='{Segoe Script} 40 bold')
    canvas.create_text(app.width/2, app.height*2.5/8, text='easy', fill='white', font='{Segoe Script} 28 bold')
    canvas.create_text(app.width/2, app.height*4.5/8, text='medium', fill='white',font='{Segoe Script} 28 bold')
    canvas.create_text(app.width/2, app.height*6.5/8, text='hard', fill='white',font='{Segoe Script} 28 bold')

def redrawAll(app, canvas):
    #from the course website
    #canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.mainImage))
    #maybe create a lingering trail later
    #for row in range(len(app.nodeBoard)): #- #for testing nodes purposes only
    #    for col in range(len(app.nodeBoard[row])):
    #        y = row * app.spacey + 200
    #        x = col * app.spacex + 90
    #        canvas.create_oval(x-5,y-5,x+5,y+5,fill='white')
    
    if app.esc:
        drawPauseScreen(app, canvas)
    elif app.keyIsPressed == False:
        startMenu(app, canvas)
    
    if app.keyIsPressed: 
        canvas.create_rectangle(25, 100, app.width-25, app.height-20, outline='white')
        for row in range(len(app.nodeBoard)):
            for col in range(len(app.nodeBoard[row])):
                x = col * app.spacex + 90
                y = row * app.spacey + 200
                if app.nodeBoard[row][col][0] == 1: #if circle
                    out = app.nodeBoard[row][col][1]
                    canvas.create_oval(x - app.r, y-app.r, x+app.r, y+app.r, fill='red', outline='maroon', width=3)
                    canvas.create_oval(x - app.r - out, y-app.r -out, x + app.r + out, y+app.r + out, outline = 'white', width = 3)
                    #canvas.create_text(x,y,text=num,fill='cyan', font='Times 20 bold') -implement later
                    #canvas.create_line(x,y,x1,y1,fill='white') #change in future maybe                   
        drawTrackerBot(app, canvas) #pathfinds thru the nodes to find the dots (most efficient method), with each step called in timer fired
        drawBomb(app, canvas)
        drawScore(app, canvas) #top right
        drawLife(app, canvas) #top left
        drawMultiplier(app, canvas) #bot left
        drawAccuracy(app, canvas)
        drawMiss(app, canvas)
    canvas.create_oval(app.mousex-10, app.mousey-10, app.mousex+10, app.mousey+10, fill='light blue')
    if app.gameOver:
        #create a new screen
        #canvas.create_image(app.width/2, app.height/2, image = ImageTk.PhotoImage(app.scoreImage))
        canvas.create_rectangle(0,0,app.width, app.height, fill='light cyan', stipple='gray50')
        canvas.create_text(app.width*7/8, app.height*1/10, text='Ranking', font='Times 40 bold', fill='white')
        canvas.create_text(app.width*6.7/8, app.height*3/7, text=app.letter, font='Times 450 bold', fill='white')
        canvas.create_rectangle(20, app.height*1/7, app.width*4/9, app.height*1/7+60, fill='misty rose')
        canvas.create_text(app.width*2/9, app.height*1/7+30, text='Score: ' + app.score, fill='mint cream', font='{Segoe Script} 26 bold')
        canvas.create_rectangle(20, app.height*1/7+60, app.width*4/9, app.height-100, fill='peach puff')
        canvas.create_polygon(app.width*4/9, app.height-100, 20, app.height-100, 20, app.height-300, app.width*4/9, app.height-200, fill='lavender')
        canvas.create_text(app.width*1/4, app.height*2/7, text='Perfect: ' + str(app.h300),fill='snow', font='{Segoe Script} 28 bold')
        canvas.create_text(app.width*1/4, app.height*3/7, text='Good: ' + str(app.h100),fill='snow',font='{Segoe Script} 28 bold')
        canvas.create_text(app.width*1/4, app.height*4/7, text='Missed: ' + str(app.totalhits-app.hits),fill='snow',font='{Segoe Script} 28 bold')
        canvas.create_text(app.width*1/4, app.height*5/7, text='Accuracy: ' + "%" + "%.2f" %((app.hits/app.totalhits) * 100),fill='snow',font='{Segoe Script} 28 bold')
        canvas.create_rectangle(app.width-500, app.height-150, app.width-20, app.height-50, fill='navajo white')
        canvas.create_text(app.width-260, app.height-100, text='Return', font='{Segoe Script} 28 bold', fill='light cyan', )

def drawBomb(app, canvas):
    for bomb in app.bombList:
        x,y = bomb[1], bomb[0]
        x = x * app.spacex + 90
        y = y * app.spacey + 200
        r = app.r
        canvas.create_oval(x-r, y-r, x+r, y+r, fill='red', outline='indigo', width=2)
        canvas.create_text(x,y,text='BOMB', fill='white', font='Times 12 bold')

#store information about the tracker in a list...
def drawTrackerBot(app, canvas):
    if len(app.trackerList)>0:
        x,y = 0,0 
        if len(app.path) > 0:
            y += app.path[0][0]
            x += app.path[0][1]
            x = x * app.spacex + 90
            y = y * app.spacey + 200
            canvas.create_oval(x-(app.r//2), y-(app.r//2), x+(app.r//2), y+(app.r//2), fill='lightcyan')

def drawPauseScreen(app, canvas):  #3 options- continue, start over, exit to menu
    #blank canvas
    canvas.create_rectangle(0,0, app.width, app.height, fill='black')
    canvas.create_rectangle(app.width*2/12, app.height*2/8, app.width*10/12, app.height*3/8, outline='white')
    canvas.create_text(app.width/2, app.height*(2.5)/8, text='Continue', font='Times 30 bold', fill='white')
    canvas.create_rectangle(app.width*2/12, app.height*4/8, app.width*10/12, app.height*5/8, outline='white')
    canvas.create_text(app.width/2, app.height*(4.5)/8, text='Start Over', font='Times 30 bold', fill='white')
    canvas.create_rectangle(app.width*2/12, app.height*6/8, app.width*10/12, app.height*7/8, outline='white')
    canvas.create_text(app.width/2, app.height*(6.5)/8, text='Exit', font='Times 30 bold', fill='white')

def drawMiss(app, canvas):
    if app.miss: #need to also add multiple simultaneous x's at the same time
        for missed in app.mcxy:
            cxMiss = missed[0]
            cyMiss = missed[1]
            canvas.create_polygon(cxMiss-8, cyMiss-10, cxMiss-10, cyMiss-8, cxMiss+8, cyMiss+10, cxMiss+10, cyMiss+10, fill='red')
            canvas.create_polygon(cxMiss+8, cyMiss-10, cxMiss+10, cyMiss-8, cxMiss-8, cyMiss+10, cxMiss-10, cyMiss+8, fill='red')
def drawAccuracy(app, canvas):
    canvas.create_oval(50, 50, 90, 90, fill='white',outline='white')
    if app.timer != 0:
        canvas.create_arc(50,50,90,90, fill='black', outline='white', start=90, extent=-((app.timer-app.time)/app.timer) * 360)
    canvas.create_text(app.width*11.5/12, app.height*1/12 -30, text="%" + "%.2f" %((app.hits/app.totalhits)*100),fill='white', font='Times 18 bold',anchor='e')
def drawScore(app, canvas):
    canvas.create_text(app.width*11/12, app.height *1/12, text= app.score, font='Times 20 bold' ,fill='white')
def drawLife(app, canvas):
    canvas.create_rectangle(app.width*1/12, app.height*.7/12, app.width*10/12, app.height*1.3/12, outline='white') #this is the total bar
    #this is the amount of lives we have
    width = (app.width*10/12) * (app.lives/100)
    if width < app.width * 1/12:
        width = app.width*1/12
    canvas.create_rectangle(app.width*1/12, app.height*.7/12, width, app.height*1.3/12, fill='white')
def drawMultiplier(app, canvas):
    canvas.create_text(app.width*1/12, app.height*11/12, text="x" + str(app.multiplier), font='Times 20 bold', anchor ='e', fill='white')

    
#https://stackoverflow.com/questions/43552320/can-i-open-two-tkinter-windows-at-the-same-time/43552391#43552391
def main():
 
    #this is fake top level - i cant run 2 windows at the same time :(
    runApp(width = 1440, height = 810)
    highscore = Toplevel()
    c = Canvas(highscore, width=300, height=1100)
    c.create_rectangle(0,0, 300, 1000, fill='black')
    c.pack()
    s = readFile('Highscore.txt')
    i = 200
    width = 300
    highscore.title('Highscore')
    c.create_line(0,100,width,100,fill='white')
    c.create_text(width/2, 50, text='HIGH SCORES', fill='ivory', font='Times 20 bold')
    for line in s.splitlines():
        c.create_line(0,i,width,i, fill='white')
        c.create_text(width/2, i - 50, text=line,fill='white', font='Times 10 bold')
        i+=100
    #https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter
    def bye():
        exit()
    highscore.protocol('WM_DELETE_WINDOW', bye)
    highscore.mainloop()
    exit()

if __name__ == '__main__':
    main()