from datetime import datetime, timezone
import time

def timestampUnify(timestampParam):
    # unify all float/string/int with more than 10 digits to standard second level timestamp int
    timestampParamInt = int(timestampParam)
    return int(str(timestampParamInt)[:10]) if len(str(timestampParamInt)) > 10 else timestampParamInt

def timestampToUTCString(timestampParam):
    timestamp = timestampUnify(timestampParam)
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def getCurrentTimestamp():
    # this is a unified form of current UTC epoch timestamp on second level
    return timestampUnify(datetime.timestamp(datetime.now(timezone.utc)))

def getCurrentMinuteTimestamp():
    currentTime = datetime.now(timezone.utc)
    currentMinuteTime = currentTime.replace(second=0, microsecond=0)
    return timestampUnify(datetime.timestamp(currentMinuteTime))

def getCurrentYearMonthDayString():
    year = str(datetime.now(timezone.utc).year)
    month = str(datetime.now(timezone.utc).month)
    day = str(datetime.now(timezone.utc).day)
    return f"{month}m{day}d{year}y"

def getCurrentYearMonthDayHourString():
    year = str(datetime.now(timezone.utc).year)
    month = str(datetime.now(timezone.utc).month)
    day = str(datetime.now(timezone.utc).day)
    hour = str(datetime.now(timezone.utc).hour)
    return f"{hour}_{month}m{day}d{year}y"

def getLocalTimeFormattedString():
    curr_time = time.localtime()
    return time.strftime("[%Y/%m/%d] %H:%M:%S", curr_time)