#!/home/robocup3d/anaconda3/bin/python
import os
import random
# get field info during gaming with `getInfo`
from infoParser import getInfo
from display import db, history

if __name__ == '__main__':
    print('connect to SQL server successfully!')
    ourTeam = 'hfut3d_code'
    codeDir = '/home/robocup3d/2019'
    oppo_teams = os.popen(f'ls -d {codeDir}/*/')
    oppo_teams = [_.strip('/\n')[len(codeDir):] for _ in oppo_teams]
    print(oppo_teams)
    if '__pycache__' in oppo_teams:
        oppo_teams.remove('__pycache__')
    if ourTeam in oppo_teams:
        oppo_teams.remove(ourTeam)
    random.shuffle(oppo_teams)
    serverHost = 'localhost'


def match():
    for oppo in oppo_teams:
        print('==============================================')
        print('running task: ' + ourTeam + ' vs ' + oppo + '......')
        for uuid in os.popen('cat /proc/sys/kernel/random/uuid'):
            uuid = uuid[:-1]
            try:
                # TODO: REPLACE OS.SYSTEM WITH OS.Popen OBJECT
                os.system('./full-match.sh {} {} {} {} {} 1>/dev/null'.format(codeDir, ourTeam, oppo, serverHost, uuid))
                first_half_scores, second_half_scores = \
                    getInfo('log/'+uuid+'-first.log'.format(ourTeam, oppo, uuid), 'score'),\
                    getInfo('log/'+uuid+'-second.log'.format(ourTeam, oppo, uuid), 'score')
                left_score, right_score = first_half_scores[0] + second_half_scores[0], \
                                          first_half_scores[1] + second_half_scores[1]
                os.system(f'cat *.log > log/{uuid}.log && rm *.log')
                history.execute(
                    f" insert into `matchHistory`values (now(),'{oppo}',{left_score},{right_score},'{uuid}');")
                print('Finished, result is {} : {}'.format(left_score, right_score))
                db.commit()
                print('Match history updated!')
            except KeyboardInterrupt as e:
                exit(1)


if __name__ == '__main__':
    try:
        # while True:
        match()
    except Exception as e:
        print('Exception:', e)
        exit(1)
