#!/bin/sh

if [ $# -lt 2 ];
then
echo "usage:
./$0 team1folder team2folder <serverHost>=localhost"
exit 1
fi
halfTime=355

CUR_DIR="$( cd "$( dirname "$0" )" && pwd )"
# start rcssserver3d and block output
startServer()
{
    rcssserver3d --script-path ${CUR_DIR} --init-script-prefix /usr/local/share/rcssserver3d 1>/dev/null 2>/dev/null &
}

halfMatch()
{
    cd $CUR_DIR
    startServer
    sleep 3
    cd $1
    ./start.sh $3
    sleep 3
    cd $CUR_DIR
    cd $2
    ./start.sh $3
    sleep 3
    cd $CUR_DIR
    # kick off
    perl kickoff.pl
    
    PLAYMODE=""
    # half match completed
    while [ ! "$PLAYMODE" = "BeforeKickOff" ]
    do
      sleep 5
      PLAYMODE=$(./infoParser.py sparkmonitor.log playmode)
    done
    # kill all agents
    cd $1
    ./kill.sh
    cd $CUR_DIR
    cd $2
    ./kill.sh
    killall -9 rcssserver3d
    return 0
}

#source match-script.sh
# set server host
if [ "$3" = "" ]
then
serverHost=localhost
else
serverHost=$3
fi

# start match and save log file
halfMatch $1 $2 $serverHost
mv $CUR_DIR/sparkmonitor.log $CUR_DIR/$1-vs-$2-first-half$4.log

halfMatch $2 $1 $serverHost
mv $CUR_DIR/sparkmonitor.log $CUR_DIR/$1-vs-$2-second-half$4.log
