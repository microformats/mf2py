"""functions to parse the properties of elements"""

from .dom_helpers import get_attr
import sys
import re

if sys.version < '3':
    from urlparse import urljoin
    text_type = unicode
    binary_type = str
else:
    from urllib.parse import urljoin
    text_type = str
    binary_type = bytes


DATE_RE = r'\d{4}-\d{2}-\d{2}'
RAWTIME_RE = r'(?P<hour>\d{1,2})(:(?P<minute>\d{2})(:(?P<second>\d{2})(\.\d+)?)?)?'
AMPM_RE = 'am|pm|a\.m\.|p\.m\.'
TIMEZONE_RE = r'Z|[+-]\d{2}:?\d{2}?'
TIME_RE = r'(?P<rawtime>%s)( ?(?P<ampm>%s))?( ?(?P<tz>%s))?' % (RAWTIME_RE, AMPM_RE, TIMEZONE_RE)
DATETIME_RE = r'(?P<date>%s)[T ](?P<time>%s)' % (DATE_RE, TIME_RE)


def text(el):
    """Process p-* properties"""
    # handle value-class-pattern
    value_classes = el.find_all(class_='value',recursive=False)
    if value_classes:
        return ''.join(vc.get_text() for vc in value_classes)

    prop_value = get_attr(el, "title", check_name="abbr")
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "value", check_name=("data","input"))
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "alt", check_name=("img","area"))
    if prop_value is not None:
        return prop_value

    ## see if get_text() replaces img with alts
    # strip here?
    return el.get_text()

def url(el, base_url=''):
    """Process p-* properties"""
    ## do the normalise absolute url thing
    prop_value = get_attr(el, "href", check_name=("a","area"))
    if prop_value is not None:
        return urljoin(base_url, prop_value)

    prop_value = get_attr(el, "src", check_name=("img", "audio", "video", "source"))
    if prop_value is not None:
        return urljoin(base_url, prop_value)

    prop_value = get_attr(el, "data", check_name="object")
    if prop_value is not None:
        return urljoin(base_url, prop_value)

    # add value-class-pattern

    prop_value = get_attr(el, "title", check_name="abbr")
    if prop_value is not None:
        return prop_value

    prop_value = get_attr(el, "value", check_name=("data","input"))
    if prop_value is not None:
        return prop_value

    # strip here?
    return el.get_text()


def datetime(el, default_date=None):
    """Process dt-* properties
    :param el: Tag containing the dt-value
    :return: a tuple of two strings, (datetime, date)
    """
    def try_normalize(dtstr, match=None):
        """Try to normalize a datetime string.
        1. Use 'T' as the date/time separator.
        2. No : in timezones, and Z replaced by +0000.
        3. Convert 12-hour time to 24-hour time

        pass match in if we have already calculated it to avoid rework
        """
        match = match or re.match(DATETIME_RE + '$', dtstr)
        if match:
            datestr = match.group('date')
            hourstr = match.group('hour')
            minutestr = match.group('minute') or '00'
            secondstr = match.group('second') or '00'
            ampmstr = match.group('ampm')
            if ampmstr:
                hourstr = match.group('hour')
                if ampmstr.startswith('p'):
                    hourstr = str(int(hourstr) + 12)
            dtstr = '%sT%s:%s:%s' % (datestr, hourstr, minutestr, secondstr)
            tzstr = match.group('tz')
            if tzstr:
                if tzstr == 'Z':
                    dtstr += '+0000'
                else:
                    dtstr += tzstr.replace(':', '')
        return dtstr

    # handle value-class-pattern
    value_els = el.find_all(class_='value')
    if value_els:
        date_parts = []
        for value_el in value_els:
            if value_el.name in ('img', 'area'):
                alt = value_el.get('alt') or value_el.get_text()
                if alt:
                    date_parts.append(alt.strip())
            elif value_el.name == 'data':
                val = value_el.get('value') or value_el.get_text()
                if val:
                    date_parts.append(val.strip())
            elif value_el.name == 'abbr':
                title = value_el.get('title') or value_el.get_text()
                if title:
                    date_parts.append(title.strip())
            elif value_el.name in ('del', 'ins', 'time'):
                dt = value_el.get('datetime') or value_el.get_text()
                if dt:
                    date_parts.append(dt.strip())
            else:
                val = value_el.get_text()
                if val:
                    date_parts.append(val.strip())

        date_part = default_date
        time_part = None
        for part in date_parts:
            match = re.match(DATETIME_RE + '$', part)
            if match:
                # if it's a full datetime, then we're done
                date_part = match.group('date')
                time_part = match.group('time')
                return try_normalize(part, match=match), date_part

            if re.match(TIME_RE + '$', part):
                time_part = part
            elif re.match(DATE_RE + '$', part):
                date_part = part

        if date_part and time_part:
            date_time_value = '%sT%s' % (date_part,
                                         time_part)
        else:
            date_time_value = date_part or time_part

        return try_normalize(date_time_value), date_part

    prop_value = get_attr(el, "datetime", check_name=("time", "ins", "del"))\
        or get_attr(el, "title", check_name="abbr")\
        or get_attr(el, "value", check_name=("data", "input"))\
        or el.get_text()  # strip here?

    # if this is just a time, augment with default date
    match = re.match(TIME_RE + '$', prop_value)
    if match and default_date:
        prop_value = '%sT%s' % (default_date, prop_value)
        return try_normalize(prop_value), default_date

    # otherwise, treat it as a full date
    match = re.match(DATETIME_RE + '$', prop_value)
    return try_normalize(prop_value, match=match), match and match.group('date')


def embedded(el):
    """Process e-* properties"""
    return {
        'html': el.decode_contents(),    # secret bs4 method to get innerHTML
        'value': el.get_text()     # strip here?
    }
