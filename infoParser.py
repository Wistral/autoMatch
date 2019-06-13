#!/usr/bin/python3

# Script for restoring RoboCup 3D sim game from logfile
# Written by Patrick MacAlpine (patmac@cs.utexas.edu)
# Usage: ./restore.py <logFile> [host] [port]

import os
import sys
import math
import struct
import socket
import time

# Flag for killing agents if they are not in logfile
fKillMissingAgents = True


# -- Start global variables for data --
global ballPath
global ballPos

global agentPath
global agentPos

ballPath = None
ballPos = None
fieldLength = 0
fieldWidth = 0
fieldHeight = None
ballRadius = None
goalWidth = None
agentPath = []
agentPos = []
for i in range(11):
    agentPath.append([None, None])
    agentPos.append([None, None])

serverTime = None
playModes = []
playMode = None
# -- End global variables for data --


# Create and return tree from s-expression
def createTreeFromSExpr(sExpr):
    tree = []
    stack = tree
    current = tree
    tokens = sExpr.split()

    nodes = []
    symbol = ""

    # Concatenate 'nd' node labels with types to preserve structure
    # between RSG and RDS formats
    for i in range(len(tokens)):
        symbol = symbol + tokens[i]
        if not symbol.endswith("(nd"):
            nodes.append(symbol)
            symbol = ""

    symbol = ""
    for n in nodes:
        if symbol != "":
            current.append(symbol)
        symbol = ""
        for i in range(len(n)):
            if '(' == n[i]:
                if symbol != "":
                    current.append(symbol)
                empty = []
                if len(current) == 1 and isinstance(current[0],str) and current[0].startswith("nd") and i < len(n)-2 and (n[i+1] != 'n' or n[i+2] != 'd'):
                    # Overwrite current node label with data to preserve structure
                    # between RSG and RDS formats
                    current[0] = empty
                else:
                    current.append(empty)
                stack.append(current)
                current = empty
                symbol = ""
            elif ')' == n[i]:
                if symbol != "":
                    current.append(symbol)
                current = stack.pop()
                symbol = ""
            else:
                symbol = symbol + n[i]


    return tree


# Find and return the path to a token in the tree and return None if token
# isn't found  
def getPathToToken(token, tree):
    for i in range(len(tree)):
        if isinstance(tree[i], list):
            if token == str(tree[i]):
                return [i]
            ret = getPathToToken(token, tree[i])
            if ret != None:
                path = [i]
                path.extend(ret)
                return path
        elif token == tree[i]:
            return [i]

    return None

# Get value in tree at the end of the given path and return None if path
# doesn't exist
def getTreeValFromPath(path, tree):
    val = tree
    for i in path:
        if i >= len(val):
            return None
        val = val[i]

    return val

# Get time value in tree and return None if time isn't found 
def getTime(tree):
    path = getPathToToken("time", tree)
    if path != None:
        path[-1] = path[-1]+1
        serverTime = float(getTreeValFromPath(path, tree))
        return serverTime
    return None

# Get playmode value in tree and return None if playmode isn't found 
def getPlayMode(tree):
    path = getPathToToken("play_mode", tree)
    if path != None:
        path[-1] = path[-1]+1
        playModeNum = int(getTreeValFromPath(path, tree))
        playMode = playModes[playModeNum]
        return playMode
    return None

# Get left score in tree and return None if playmode isn't found 
def getScoreLeft(tree):
    path = getPathToToken("score_left", tree)
    if path != None:
        path[-1] = path[-1]+1
        score_left = int(getTreeValFromPath(path, tree))
        # playMode = playModes[playModeNum]
        return score_left
    else:
        print('not found ')
    return None

# Get right score in tree and return None if playmode isn't found 
def getScoreRight(tree):
    path = getPathToToken("score_right", tree)
    if path != None:
        path[-1] = path[-1]+1
        score_right = int(getTreeValFromPath(path, tree))
        # playMode = playModes[playModeNum]
        return score_right
    return None

# Parse location of ball from value
def parseBallVal(val):
    if len(val) != 17:
        return None
    # val[-4] = Px, val[-3] = Py, val[-2] = Pz
    return [val[-4],val[-3],val[-2]]

# Get location of ball from path and reurn None if path doesn't exist
def getBallFromPath(path, tree):
    if path != None:
        val = getTreeValFromPath(path, tree)
        if val != None:
            return parseBallVal(val)
    return None

# Parse agent position and orientation from value
def parseAgentPosVal(val):
    if len(val) != 17:
        return None
    # val[1] = nx, val[2] = ny, val[-4] = Px, val[-3] = Py, val[-2] = Pz
    return [val[-4],val[-3],str(max(0.3,float(val[-2]))),str(math.degrees(math.atan2(float(val[2]),float(val[1]))))]

# Get location and orientation of agent from path and reurn None if path 
# doesn't exist
def getAgentPosFromPath(path, tree):
    if path != None:
        val = getTreeValFromPath(path, tree)
        if val != None:
            return parseAgentPosVal(val)
    return None


def correctBallPositionForPlayMode(ballPos, playMode):
    if ballPos == None:
        return
    ballPos[0] = str(min(fieldLength/2.0, max(-fieldLength/2.0, float(ballPos[0]))))
    ballPos[1] = str(min(fieldWidth/2.0, max(-fieldWidth/2.0, float(ballPos[1]))))
    if playMode == "BeforeKickOff" or playMode == "KickOff_Left" or playMode == "KickOff_Right":
        ballPos[0] = str(0)
        ballPos[1] = str(0)
        ballPos[2] = str(ballRadius)
    elif playMode == "goal_kick_left":
        ballPos[0] = str(-fieldLength/2.0+1)
        ballPos[1] = str(0)
        ballPos[2] = str(ballRadius)
    elif playMode == "goal_kick_right":
        ballPos[0] = str(fieldLength/2.0-1)
        ballPos[1] = str(0)
        ballPos[2] = str(ballRadius)
    elif playMode == "corner_kick_left" or playMode == "corner_kick_right":
        if playMode == "corner_kick_left":
            ballPos[0] = str(fieldLength/2.0-ballRadius)
        elif playMode == "corner_kick_right":
            ballPos[0] = str(-fieldLength/2.0+ballRadius)
        cornerKickY = (fieldWidth + goalWidth) / 4.0 - ballRadius
        if float(ballPos[1]) > 0:
            ballPos[1] = str(cornerKickY)
        else:
            ballPos[1] = str(-cornerKickY)
        ballPos[2] = str(ballRadius)
    elif playMode == "KickIn_Left" or playMode == "KickIn_Right":
        if ballPos[1] > 0:
            ballPos[1] = str(fieldWidth/2.0-ballRadius)
        else:
            ballPos[1] = str(-fieldWidth/2.0+ballRadius)
        ballPos[2] = str(ballRadius)

# if len(sys.argv) < 2:
#   print "Usage: " + sys.argv[0] + " <logFile> [host] [port]"
#   sys.exit()

def getInitMessage(ballPos, playMode):
    if ballPos == None:
        return None
    if playMode == "goal_kick_left" or playMode == "goal_kick_right" or playMode == "corner_kick_left" or playMode == "corner_kick_right" or playMode == "KickIn_Left" or playMode == "KickIn_Right":
        return "(playMode PlayOn)(ball (pos " + ballPos[0] + " " + ballPos[1] + " " + str(fieldHeight - 2*ballRadius) + ") (vel 0 0 0))"
    else:
        return None

def getInfo(fn, info='playmode'):
    logFile = open(fn)

    host = "localhost"
    if len(sys.argv) > 2:
        host = sys.argv[2]


    port = 3200
    if len(sys.argv) > 3:
        port = int(sys.argv[3])

    agentSides = ["matLeft", "matRight"]
    agentStrings = []

    for i in range(11):
        agentStrings.append([])
        for s in agentSides:
            agentStrings[-1].append(str(["resetMaterials", "matNum" + str(i+1), s, "naoblack", "naowhite"]))


    lines = logFile.readlines()

    RDSTrees = []
    for l in reversed(lines):
        tree = createTreeFromSExpr(l)
        RSGPath = getPathToToken(str(["RSG", "0", "1"]), tree)
        if RSGPath != None:
            # Process last RSG frame

            # Get game parameters
            global fieldLength
            global fieldWidth
            global fieldHeight
            global ballRadius
            global goalWidth
            fieldLength = float(getTreeValFromPath(getPathToToken("FieldLength", tree)[:-1], tree)[1])
            fieldWidth = float(getTreeValFromPath(getPathToToken("FieldWidth", tree)[:-1], tree)[1])
            fieldHeight = float(getTreeValFromPath(getPathToToken("FieldHeight", tree)[:-1], tree)[1])
            ballRadius = float(getTreeValFromPath(getPathToToken("BallRadius", tree)[:-1], tree)[1])
            goalWidth = float(getTreeValFromPath(getPathToToken("GoalWidth", tree)[:-1], tree)[1])


            # Get playmode names
            global playModes
            playModes = getTreeValFromPath(getPathToToken("play_modes", tree)[:-1], tree)[1:]

            # Get time
            global serverTime
            serverTime = getTime(tree)
            # print("Time: " + str(serverTime))

            # Get playmode
            global playMode
            playMode = getPlayMode(tree)
            # print("Playmode: " + str(playMode))

            # Get ball
            path = getPathToToken("models/soccerball.obj", tree)
            if path != None:
                path = path[:-2]
                path[-1] = path[-1]-1
                ballPath = path
                val = getTreeValFromPath(path, tree)
                ballPos = parseBallVal(val)
                # print("Ball: " + str(ballPos))

            # Get agents
            for a in range(len(agentStrings)):
                for s in range(len(agentStrings[a])):
                    path = getPathToToken(agentStrings[a][s], tree)
                    if path != None:
                        path = path[:-2]
                        path[-1] = path[-1]-1
                        agentPath[a][s] = path
                        val = getTreeValFromPath(path, tree)
                        agentPos[a][s] = parseAgentPosVal(val)
                        if s == 0:
                            print("Left " + str(a+1) + ": " + str(agentPos[a][s]))
                        else:
                            print("Right " + str(a+1) + ": " + str(agentPos[a][s]))

            break
        else:
            # Save RDS tree to be process later
            RDSTrees.append(tree)

    # Process RDS frames
    for t in reversed(RDSTrees):
        # Get time
        val = getTime(t)
        if val != None:
            serverTime = val
            # print("Time: " + str(serverTime))

        # Get playmode
        val = getPlayMode(t)
        if val != None:
            playMode = val
            # print("Playmode: " + str(playMode))

        # Get ball
        val = getBallFromPath(ballPath, t)
        if val != None:
            ballPos = val
            # print("Ball: " + str(ballPos))

        # get left and right score
        left, right = getScoreLeft(tree), getScoreRight(tree)

        info_dict = {
            'playmode': playMode,
            'time': serverTime,
            'ball': ballPos,
            'score': (left, right)
        }
        return info_dict[info]

        # Get agents
        for a in range(len(agentStrings)):
            for s in range(len(agentStrings[a])):
                val = getAgentPosFromPath(agentPath[a][s], t)
                if val != None:
                    agentPos[a][s] = val
                    if s == 0:
                        print("Left " + str(a+1) + ": " + str(agentPos[a][s]))
                    else:
                        print("Right " + str(a+1) + ": " + str(agentPos[a][s]))


    correctBallPositionForPlayMode(ballPos, playMode)

    # Create messages to send to training command parser

    # Message to initialize ball position if needed for free kick playmodes
    # (this message will breifly put the ball at the top of the ceiling of the
    # field and set the playmode to PlayOn so that the transition into the next
    # playmode will be correct
    initMsg = getInitMessage(ballPos, playMode)
    msg = ""

    if playMode != None:
        msg = msg + "(playMode " + playMode + ")"
    if ballPos != None:
        msg = msg + "(ball (pos " + ballPos[0] + " " + ballPos[1] + " " + ballPos[2] + ") (vel 0 0 0))"

    for i in range(11):
        if agentPos[i][0] != None:
            msg = msg + "(agent (unum " + str(i+1) + ") (team Left) (move " + agentPos[i][0][0] + " " + agentPos[i][0][1] + " " + agentPos[i][0][2] + " " + agentPos[i][0][3] + "))"
        elif fKillMissingAgents == True:
            # Kill agent as it was not found
            msg = msg + "(kill (unum " + str(i+1) + ") (team Left))"
        if agentPos[i][1] != None:
            msg = msg + "(agent (unum " + str(i+1) + ") (team Right) (move " + agentPos[i][1][0] + " " + agentPos[i][1][1] + " " + agentPos[i][1][2] + " " + agentPos[i][1][3] + "))"
        elif fKillMissingAgents == True:
            # Kill agent as it was not found:
            msg = msg + "(kill (unum " + str(i+1) + ") (team Right))"


if __name__ == '__main__':
    print(getInfo(sys.argv[1],sys.argv[2]))

#  print(getInfo('ahu3dfirst-vs-HfutEngine2019-first-half.log', 'score'))
