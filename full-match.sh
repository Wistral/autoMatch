#!/bin/bash

if [[ $# -lt 2 ]];
then
echo "usage:
$0 codes_folder team1-folder-name team2-folder-name <serverHost>=localhost log-file-uuid"
exit 1
fi
halfTime=355

CUR_DIR="$( cd "$( dirname "$0" )" && pwd )"
CODE_DIR="$( cd $1 && pwd )"
echo $CODE_DIR
TEAM1_DIR="${CODE_DIR}/$2"
TEAM2_DIR="${CODE_DIR}/$3"
echo "team1 ${TEAM1_DIR}"
echo "team2 ${TEAM2_DIR}"
# start rcssserver3d and block output
startServer()
{
    killall -9 rcssserver3d
    rm sparkmonitor.log
# --script-path ${CUR_DIR}/ --init-script-prefix /usr/local/share/rcssserver3d
    rcssserver3d --script-path ./rcssserver3d.rb >/dev/null 2>/dev/null &
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
if [[ "$4" = "" ]]
then
serverHost='localhost'
else
serverHost=$4
fi

#startServer
# start match and save log file
halfMatch ${TEAM1_DIR} ${TEAM2_DIR} ${serverHost}
mv ${CUR_DIR}/sparkmonitor.log ${CUR_DIR}/$5-first.log

halfMatch ${TEAM2_DIR} ${TEAM1_DIR} ${serverHost}
mv ${CUR_DIR}/sparkmonitor.log ${CUR_DIR}/$5-second.log
