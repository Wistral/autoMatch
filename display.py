#!/home/robocup3d/anaconda3/bin/python
import pymysql

# connect to mysql service
try:
    db = pymysql.connect(
        '192.168.1.145',
        'root',
        'robocup3d',
        'robocup3d',
        charset='utf8mb4', port=3306
    )
    history = db.cursor()
except Exception as e:
    print('ERROR when connect to SQL server!')
    exit(1)


def raw_data():
    try:
        history.execute("""select * from matchHistory;""")
        res = history.fetchall()
        history.execute("""select distinct opp_teamname from matchHistory;""")
        teams = history.fetchall()
        # print(res)
    except Exception as e:
        print(e)
        pass
    finally:
        db.close()
        return res, teams


if __name__ == '__main__':
    # TODO: UPDATE DATA PROCESS METHOD
    history, teams = raw_data()
    # print(history)
    # print(teams)
    data = {
        # "team-name": 'our-total-goals', 'oppo-total-goal', win', 'lose', 'draw'
        _[0]: [0, 0, 0, 0, 0] for _ in teams
    }

    for p in history:
        team = data[p[1]]
        if p[2] > p[3]:
            team[2] += 1
        elif p[2] < p[3]:
            team[3] += 1
        else:
            team[4] += 1
        team[0] += p[2]
        team[1] += p[3]
    data = [
        [k, *v] for k, v in data.items()
    ]

    print("team-name", 'our-total-goals', 'oppo-total-goal',
          '\twin(rate)', 'lose(rate)', 'draw(rate)', sep='\t')
    for piece in data:
        # team name
        total = sum(piece[-3:])
        if total:
            print("{:20}\t{}\t\t{}\t\t{}({:5.2f}%)\t{}({:5.2f}%)\t{}({:5.2f}%)".format(
                piece[0],
                piece[1], piece[2],
                piece[3], piece[3] / total * 100,
                piece[4], piece[4] / total * 100,
                piece[5], piece[5] / total * 100,
            ))
        else:
            print("{:20}\t{}\t\t{}\t\t{}({:5.2f}%)\t{}({:5.2f}%)\t{}({:5.2f}%)".format(
                piece[0],
                piece[1], piece[2],
                piece[3], 0,
                piece[4], 0,
                piece[5], 0,
            ))
