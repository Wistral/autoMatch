#!/home/robocup3d/anaconda3/bin/python
import pymysql

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


def fetch():
    try:
        cursor.execute("""select * from automatch;""")
        res = cursor.fetchall()
        # print(res)
    except Exception as e:
        print(e)
        pass
    finally:
        db.close()
        return res


if __name__ == '__main__':
    data = fetch()
    print("team-name", 'our-total-goals', 'oppo-total-goal',
          '\twin(rate)', 'lose(rate)', 'draw(rate)', sep='\t')
    for piece in data:
        # team name
        total = sum(piece[-3:])
        if total:
            print("{:20}\t{}\t\t{}\t\t{}({:5}%)\t{}({:5}%)\t{}({:5}%)".format(
                piece[0],
                piece[1], piece[2],
                piece[3], piece[3] / total * 100,
                piece[4], piece[4] / total * 100,
                piece[5], piece[5] / total * 100,
            ))
        else:
            print("{:20}\t{}\t\t{}\t\t{}({:5}%)\t{}({:5}%)\t{}({:5}%)".format(
                piece[0],
                piece[1], piece[2],
                piece[3], 0,
                piece[4], 0,
                piece[5], 0,
            ))
