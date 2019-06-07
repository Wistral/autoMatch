#!/home/robocup3d/anaconda3/bin/python
import os
import random
# get field info during gaming with `getInfo`
from infoParser import getInfo
from display import db, history

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
    serverHost = 'localhost'


def match():
    for oppo in oppo_teams:
        print('==============================================')
        print('running task: ' + ourTeam + ' vs ' + oppo + '......')
        uuid = os.popen('cat /proc/sys/kernel/random/uuid')
        os.system('./full-match.sh {} {} {} {} >/dev/null 2>&1'.format(ourTeam, oppo, serverHost, uuid))
        first_half_scores, second_half_scores = \
            getInfo(uuid+'.log'.format(ourTeam, oppo, uuid), 'score'),\
            getInfo(uuid+'.log'.format(ourTeam, oppo, uuid), 'score')
        left_score, right_score = first_half_scores[0] + second_half_scores[1], \
                                  first_half_scores[1] + second_half_scores[0]
        history.execute(
            """ insert into `matchHistory`values (now(),'{}',{},{});""".format(oppo, left_score, right_score, uuid))
        print('Finished, result is {} : {}'.format(left_score, right_score))
        db.commit()
        print('Match history updated!')


if __name__ == '__main__':
    try:
        while True:
            match()
    except Exception as e:
        print('Exception:', e)
        exit(1)
