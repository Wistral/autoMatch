from autoPlay import db, cursor


try:
    cursor.execute("""select * from automatch;""")
    res = cursor.fetchall()
    print(res)
    print("teamname", 'our-total-goals', 'oppo-total-goal',
          'win(rate)', 'lose(rate)', 'draw(rate)', sep='\t')
    for piece in res:
        total = sum(piece[-3:])
        if total:
            print("{:20}\t{}\t\t{}\t\t\t{}({}%)\t\t{}({}%)\t\t{}({}%)".format(
                piece[0],
                piece[1], piece[2],
                piece[3], piece[3]/total*100,
                piece[4], piece[4] / total * 100,
                piece[5], piece[5] / total * 100,
        ))
        else:
            print("{:20}\t{}\t\t{}\t\t\t{}({}%)\t\t{}({}%)\t\t{}({}%)".format(
                piece[0],
                piece[1], piece[2],
                piece[3], 0,
                piece[4], 0,
                piece[5], 0,
            ))
except Exception as e:
    print(e)
    pass
finally:
    db.close()