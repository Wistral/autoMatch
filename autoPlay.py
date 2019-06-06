#!/home/robocup3d/anaconda3/bin/python
import os
import random
import pymysql
# get field info during gaming with `getInfo`
from infoParser import getInfo
from display import db, cursor


if __name__ == '__main__':
    print('connect to SQL server successfully!')
    ourTeam = 'HfutEngine2019'
    # oppoteams = []
    # get team names
    oppoteams = os.popen('ls -d */')
    oppoteams = [_[:-2] for _ in oppoteams]
    oppoteams.remove('__pycache__')
    oppoteams.remove('HfutEngine2019')
    random.shuffle(oppoteams)
    # print('There are', len(oppoteams), 'teams')
    # print(*oppoteams, sep='\n')
    cursor.execute("""select * from automatch;""")

    if 'result.txt' in os.listdir('.'):
        f = open('result.txt')
        lines = f.readline()
        f.close()
        result = eval(lines)
    else:
        result = {
            # teamname: times, win, lose, draw
            k: [0, 0, 0, 0] for k in oppoteams
        }

    serverHost = 'localhost'


def match():
    for oppo in oppoteams:
        print('==============================================')
        print('running task: ' + ourTeam + ' vs ' + oppo + '......')
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
        ), 'score'), getInfo('{}-vs-{}-second-half{}.log'.format(
            ourTeam,
            oppo,
            result[oppo][0]
        ), 'score')
        # scores1, scores2 = (1, 2), (2, 0)
        result[oppo][0] += 1
        lscore, rscore = scores1[0] + scores2[1], scores1[1] + scores2[0]
        # todo: Exception: (1054, "Unknown column 'Be' in 'field list'")
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
        print('update database!')
        with open('result.txt', 'w') as f:
            print(repr(result), file=f)


if __name__ == '__main__':
    try:
        while True:
            match()
    except Exception as e:
        print('Exception:', e)
        exit(1)
