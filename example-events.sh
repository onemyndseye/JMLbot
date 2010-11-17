#!/bin/bash
##
## This is a very bare example of a event handler for jmlbot
##

###############################################################################
################################### INIT ######################################
BASE_DIR="$(dirname $(readlink -f $(type -a "$0" |awk '{print $3}'|head -n1)))"

if [ "$1" ]; then
  TMP="$(echo $1 |grep "@")"
  if [ -n "$TMP" ]; then
    EVENT_NICK="$1"
    shift 1
    EVENT_CONTENT="${@}"
  else
    # Incorrect args passed to the handler. Should be
    # <contact@email.com> <message content>
    exit 100
  fi
else
  # No args passed to event handler
  exit 1
fi

cd $BASE_DIR

##############################################################################
do_fortune() {
echo "You will be happy with this bot :)"

}


do_help() {
cat <<EOF
General commands:
fortune - Display a fortune
help - this message

EOF
}
################## End Helper functions ############################################


########## Main event function - All others should be called from here ##############
#####################################################################################
do_event() {
EVENT_NICK="$1"
shift 1
EVENT_CONTENT="${@}"

case "$1" in
           help)
              echo ""
              do_help
              ;;
         fortune)
               echo ""
               do_fortune
               ;;
esac
}

# Dont quote $EVENT_CONTENT so it may be parameterized.
do_event "$EVENT_NICK" $EVENT_CONTENT

