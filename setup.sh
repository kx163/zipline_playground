#!/usr/bin/env bash
# The API key of quandl.com, used to ingest data of bundle 'quandl'
QUANDL_API_KEY=91ju4M5qZaGXUwmW34qG

# convenient function to run algorithm with forex bundle and calendar
function zipfx() {
    zipline run \
        -f "$1" \
        -s ${2:-2015.1.1} \
        -e ${3:-2017.1.1} \
        -b custom_history \
        --data-frequency minute \
        --trading-calendar CFX;
}

# convenient function to backup the relevant system files
function backup() {
    echo "in backup()"
    if [ ! -z "${VIRTUAL_ENV+x}" ] ; then
        SYS_BAK="${VIRTUAL_ENV}/../sys.bak/"
        echo $SYS_BAK
        if [[ ! -e ${SYS_BAK} ]] ; then
            mkdir -p ${SYS_BAK}
        fi
        # backup the forex calendar
        FOREX_CALENDAR="${VIRTUAL_ENV}/lib/python3.5/site-packages/zipline/utils/calendars/exchange_calendar_cfx.py"
        echo $FOREX_CALENDAR
        if [ -f ${FOREX_CALENDAR} ] ; then
            cp ${FOREX_CALENDAR} ${SYS_BAK}
        fi
        # backup the calendar register file
        CALENDAR_UTILS="${VIRTUAL_ENV}/lib/python3.5/site-packages/zipline/utils/calendars/calendar_utils.py"
        echo $CALENDAR_UTILS
        if [ -f ${CALENDAR_UTILS} ] ; then
            cp ${CALENDAR_UTILS} ${SYS_BAK}
        fi
        # backup the extension file for ingest
        EXTENSION="$HOME/.zipline/extension.py"
        echo $EXTENSION
        if [ -f ${EXTENSION} ] ; then
            cp ${EXTENSION} ${SYS_BAK}
        fi
    fi
}

# convenient function to restore the relevant system files
function restore() {
    if [ ! -z "${VIRTUAL_ENV+_}" ] ; then
        SYS_BAK="${VIRTUAL_ENV}/../sys.bak/"
        if [[ ! -e ${SYS_BAK} ]] ; then
            mkdir -p ${SYS_BAK}
        fi
        # restore the forex calendar
        FOREX_CALENDAR="${VIRTUAL_ENV}/lib/python3.5/site-packages/zipline/utils/calendars/exchange_calendar_cfx.py"
        if [ -f ${FOREX_CALENDAR} ] ; then
            cp "${SYS_BAK}exchange_calendar_cfx.py" ${FOREX_CALENDAR}
        fi
        # restore the calendar register file
        CALENDAR_UTILS="${VIRTUAL_ENV}lib/python3.5/site-packages/zipline/utils/calendars/calendar_utils.py"
        if [ -f ${CALENDAR_UTILS} ] ; then
            cp "${SYS_BAK}calendar_utils.py" ${CALENDAR_UTILS}
        fi
        # restore the extension file for ingest
        EXTENSION="$HOME/.zipline/extension.py"
        if [ -f ${EXTENSION} ] ; then
            cp "${SYS_BAK}extension.py" ${EXTENSION}
        fi
    fi
}