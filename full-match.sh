#!/bin/sh

if [[ $# -lt 2 ]];
then
echo "usage:
$0 team1folder team2folder <serverHost>=localhost log-file-uuid"
exit 1
fi
halfTime=355

CUR_DIR="$( cd "$( dirname "$0" )" && pwd )"
TEAM1_DIR="$( cd "$( dirname "$1" )" && pwd )"
TEAM2_DIR="$( cd "$( dirname "$2" )" && pwd )"

# start rcssserver3d and block output
startServer()
{
# --script-path ${CUR_DIR}/ --init-script-prefix /usr/local/share/rcssserver3d
    rcssserver3d >/dev/null 2>/dev/null &
}

halfMatch()
{
    cd ${CUR_DIR}
    startServer
    sleep 3
    cd ${TEAM1_DIR}
    ./start.sh $3
    sleep 3
    cd ${CUR_DIR}
    cd ${TEAM2_DIR}
    ./start.sh $3
    sleep 3
    cd ${CUR_DIR}
    # kick off
    perl kickoff.pl
    
    PLAY_MODE=""
    # half match completed
    while [[ ! "$PLAY_MODE" = "BeforeKickOff" ]]
    do
      sleep 5
      PLAY_MODE=$(./infoParser.py sparkmonitor.log playmode)
    done
    # kill all agents
    cd $1
    ./kill.sh
    cd ${CUR_DIR}
    cd $2
    ./kill.sh
    killall -9 rcssserver3d
    return 0
}

#source match-script.sh
# set server host
if [[ "$3" = "" ]]
then
serverHost='localhost'
else
serverHost=$3
fi

#startServer
# start match and save log file
halfMatch $1 $2 ${serverHost}
mv ${CUR_DIR}/sparkmonitor.log ${CUR_DIR}/$4.log

halfMatch $2 $1 ${serverHost}
mv ${CUR_DIR}/sparkmonitor.log ${CUR_DIR}/$4.log
