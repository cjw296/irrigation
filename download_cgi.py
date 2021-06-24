import re
from csv import DictReader
from datetime import datetime
from io import StringIO

import requests
from tabulate import tabulate

from download import time_periods

MARKER = '=======A copy of your extracted data follows======'

PATTERN = re.compile(r'<a href="(https://metdata.reading.ac.uk/cgi-bin/load_txt.csv\?[^.]+\.csv)">')


def download(start: datetime, end: datetime):
    response = requests.post(
        'https://metdata.reading.ac.uk/cgi-bin/climate_extract.cgi',
        data=dict(
            RR='y',
            daybeg=start.strftime('%d'),
            monthbeg=start.strftime('%b'),
            yearbeg=start.strftime('%Y'),
            dayend=end.strftime('%d'),
            monthend=end.strftime('%b'),
            yearend=end.strftime('%Y'),
            nexttask='retrieve',
        )
    )
    content = response.text
    try:
        download_url = PATTERN.search(content).group(1)
    except:
        pass
    else:
        assert not requests.get(download_url).content, 'download started working!'

    csv_text = (content.split(MARKER)[-1].replace('\n', '').replace('<br>', '\n').strip()+'\n')
    return DictReader(StringIO(csv_text))


def retrieve(start: datetime, end: datetime = None):
    end = end or datetime.now()
    for start, end in time_periods('climate_extract.cgi', start, end):
        yield from download(start, end)


if __name__ == '__main__':
    reader = retrieve(datetime(2021, 5, 1), datetime(2021, 6, 22))
    print(tabulate(reader, headers='keys'))
