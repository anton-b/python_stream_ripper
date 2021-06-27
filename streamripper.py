import io
import signal
import requests
import re

# url = "http://dorognoe.hostingradio.ru:8000/dorognoe"
url = "http://air.radiorecord.ru:8102/sd90_128"


def get_data(curtitle, metadata_maybe, audio):
    m = re.search(br"StreamTitle='([^']*)';(.*)", metadata_maybe) or\
        re.search(br"StreamTitle='([^']*)';(.*)", audio)
    if m:
        curtitle = m.group(1).decode('utf-8', errors='replace')
        audio = m.group(2)
        return (curtitle, audio)
    return (curtitle, metadata_maybe)


def make_path(title):
    return f"{title}.mp3"


def stream_to_files(response, bufsize, opened_file=None, title=None):
    audio = next(response.iter_content(chunk_size=bufsize))
    metadata_maybe = next(r.iter_content(chunk_size=bufsize))
    (newtitle, towrite) = get_data(title, metadata_maybe, audio)
    if newtitle != title:
        print(newtitle)
        title = newtitle
        if isinstance(opened_file, io.IOBase):
            opened_file.close()
            opened_file = None
    if not opened_file:
        opened_file = open(make_path(title), 'wb')
    opened_file.write(audio)
    opened_file.write(towrite)
    stream_to_files(response, bufsize, opened_file, title)


if __name__ == '__main__':
    with requests.get(url, stream=True, headers={"Icy-MetaData": "1"}) as r:
        r.raise_for_status()
        metaint = int(r.headers['icy-metaint'])
        stream_to_files(r, metaint)
