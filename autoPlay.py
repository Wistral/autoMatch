#!/home/robocup3d/anaconda3/bin/python
import os
import random
import pymysql
# get field info during gaming with `getInfo`
from infoParser import getInfo

# connect to mysql service
try:
    db = pymysql.connect(
        'localhost',
        'root',
        'robocup3d',
        'robocup3d',
        charset='utf8mb4', port=3306
    )
    cursor = db.cursor()
except Exception as e:
    print('ERROR when connect to SQL server!')
    exit(1)

print('connect to sql server successfully!')
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

if 'result.txt' in os.listdir('.'):
    lines = ''.join([_ for _ in open('result.txt')])
    result = eval(lines)
else:
    result = {
    # teamname: times, win, lose, draw
        k: [0, 0, 0, 0] for k in oppoteams
    }

serverHost = 'localhost'

# db.execute("insert into student values(95002, '張三', '男', 20, 'CS')")
# print(*db.fetchall())


def match():
    print('run match')
    for oppo in oppoteams:
        print('running task: '+ourTeam+' vs '+oppo+'......')
        os.system('./full-match.sh {} {} {} {} >/dev/null 2>&1'.format(
            ourTeam,
            oppo,
            serverHost,
            result[oppo][0]
        ))
        print('sss')
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
        cursor.execute(
            """
                update automatch set `our total goal` = `our total goal`+{} where `oppo name` = '{}'
            """.format(lscore, oppo)
        )
        cursor.execute(
            """
                update automatch set `oppo total goal` = `oppo total goal`+{} where `oppo name` = '{}'
            """.format(rscore, oppo)
        )
        if lscore < rscore:
            result[oppo][1] += 1
            cursor.execute(
                """
                    update automatch set `lose` = `lose`+1 where `oppo name` = '{}'
                """.format(oppo)
            )
        elif lscore > rscore:
            result[oppo][2] += 1
            cursor.execute(
                """
                    update automatch set `win` = `win`+1 where `oppo name` = '{}'
                """.format(oppo)
            )
        else:
            result[oppo][3] += 1
            cursor.execute(
                """
                    update automatch set `draw` = `draw`+1 where `oppo name` = '{}'
                """.format(oppo)
            )

        print('finished, result is {} : {}'.format(lscore, rscore))

        db.commit()

        with open('result.txt', 'w') as f:
            print(repr(result), file=f)


if __name__ == '__main__':
    try:
        match()
    except Exception:
        exit(1)
