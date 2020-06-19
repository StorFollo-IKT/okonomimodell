"""
 * Convert a microsoft timestamp to UNIX timestamp
 * http://www.morecavalier.com/index.php?whom=Apps%2FLDAP+timestamp+converter
 * @param int ad_date Microsoft timestamp
 * @return int UNIX timestamp
 """


def microsoft_timestamp_to_unix(ad_date):
    if not ad_date:
        raise ValueError('Invalid date')

    secsAfterADEpoch = ad_date / 10000000
    AD2Unix = ((1970 - 1601) * 365 - 3 + round((1970 - 1601) / 4)) * 86400

    """Why -3 ?
    If the year is the last year of a century, eg. 1700, 1800, 1900, 2000,
    then it is only a leap year if it is exactly divisible by 400.
    Therefore, 1900 wasn't a leap year but 2000 was."""

    unixTimeStamp = int(secsAfterADEpoch - AD2Unix)

    return unixTimeStamp
