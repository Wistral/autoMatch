#!/home/robocup3d/anaconda3/bin/python
import os
import random
# get field info during gaming with `getInfo`
from infoParser import getInfo
from display import db, history, fetch


if __name__ == '__main__':
    print('connect to SQL server successfully!')
    ourTeam = 'HfutEngine2019'
    # oppo_teams = []
    # get team names
    oppo_teams = os.popen('ls -d */')
    oppo_teams = [_[:-2] for _ in oppo_teams]
    oppo_teams.remove('__pycache__')
    oppo_teams.remove('HfutEngine2019')
    random.shuffle(oppo_teams)
    # print('There are', len(oppo_teams), 'teams')
    # print(*oppo_teams, sep='\n')
    # cursor.execute("""select * from automatch;""")
    # data = fetch()
    # result = {
    #     meta[0]: meta[1:]
    #     for meta in data
    # }

    # if 'result.txt' in os.listdir('.'):
    #     f = open('result.txt')
    #     lines = f.readline()
    #     f.close()
    #     result = eval(lines)
    # else:
    #     result = {
    #         # teamname: times, win, lose, draw
    #         k: [0, 0, 0, 0] for k in oppo_teams
    #     }

    serverHost = 'localhost'


def match():
    for oppo in oppo_teams:
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
        left_score, right_score = scores1[0] + scores2[1], scores1[1] + scores2[0]
        history.execute(""" insert into `matchHistory`
        values (now(),'{}',{},{});""".format(oppo, left_score, right_score))

        print('Finished, result is {} : {}'.format(left_score, right_score))

        db.commit()
        print('Match history updated!')
        # with open('result.txt', 'w') as f:
        #     print(repr(result), file=f)


if __name__ == '__main__':
    try:
        while True:
            match()
    except Exception as e:
        print('Exception:', e)
        exit(1)
