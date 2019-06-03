#!/home/robocup3d/anaconda3/bin/python
import os
import random
import pymysql
# get field info during gaming with `getInfo`
from infoParser import getInfo

# connect to mysql service
db = pymysql.connect(
    'localhost',
    'root',
    'robocup3d',
    'robocup3d',
    charset='utf8mb4'
).cursor()
# db = pymysql.connect(
#     'localhost',
#     'root',
#     'touhou',
#     'school',
#     charset='utf8mb4'
# ).cursor()
ourTeam = 'HfutEngine2019'
#oppoteams = []
# get team names
oppoteams = os.popen('ls -d */')
oppoteams = [_[:-2] for _ in oppoteams]
oppoteams.remove('__pycache__')
random.shuffle(oppoteams)
print('There are', len(oppoteams), 'teams')
print(*oppoteams, sep='\n')
result = {
    # teamname: times, win, lose, draw
    k: [0, 0, 0, 0] for k in oppoteams
}
serverHost = 'localhost'

# db.execute("insert into student values(95002, '張三', '男', 20, 'CS')")
# print(*db.fetchall())


def match():
    for oppo in oppoteams:
        print('running task: '+ourTeam+' vs '+oppo+'......')
        os.system('./full-match.sh {} {} {} {} >/dev/null 2>&1'.format(
            ourTeam,
            oppo,
            serverHost,
            result[oppo][0]
        ))
        scores1, scores2 = getInfo('{}-vs-{}-first-half{}.log'.format(
            ourTeam,
            oppo,
            result[oppo][0]
        )), getInfo('{}-vs-{}-second-half{}.log'.format(
            ourTeam,
            oppo,
            result[oppo][0]
        ))
        result[oppo][0] += 1
        lscore, rscore = scores1[0]+scores2[1], scores1[1]+scores2[0]
        if lscore < rscore:
            result[oppo][1] += 1
        elif lscore > rscore:
            result[oppo][2] += 1
        else:
            result[oppo][3] += 1
        print('finished, result is {} : {}'.format(lscore, rscore))

        # TODO: ADD SQL SENTENCES HERE
        db.execute("update automatch ")

        with open('result.txt', 'w') as f:
            for k, v in enumerate(result):
                print(k, *v, file=f)
