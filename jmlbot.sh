#!/bin/bash


###################################### Init ######################################
JAVA=$(which java)
if [ -n "$JAVA" ]; then
  BASE_DIR="$(dirname $(readlink -f $(type -a "$0" |awk '{print $3}'|head -n1)))"
  CONFIG="${BASE_DIR}/jmlbot.conf"
  PIDFILE="${BASE_DIR}/JMLbot.pid"
  NAME=JMLbot
  MEM=16
  cd ${BASE_DIR}/sys/
else
  echo "Java not found! Aborting ..."
  exit 1
fi
#################################### END Init ####################################


case "$1" in
          start)
               echo -n "Starting ${NAME} .."
               java -Xmx${MEM}m -jar jython.jar ${NAME}.py --config "$CONFIG" 2>&1 >/dev/null &
               PID=$!
               echo ".... done. [${PID}]"
               ;;
           stop)
               PID=$(ps ax |grep java |grep ${NAME}.py|grep -v grep |awk '{print $1}')
               if [ -n "$PID" ]; then
                 echo -n "Stoping $NAME ..."
                 kill -9 $PID
                 rm -f $PIDFILE
                 echo "... done"
                 exit 0
               else
                 echo "$NAME is not running."
                 exit 1
               fi
               ;;
        restart)
               ${BASE_DIR}/$(basename $0) stop
               sleep 2
               ${BASE_DIR}/$(basename $0) start
               ;;
              *)
               echo "Usage: $0 <start|stop>"
               ;;
esac

