import requests
import os
from multiprocessing.pool import ThreadPool
import re
import sys


if __name__ == "__main__":

    title = ''
    url_root = ''
    url = ''
    files = []
    page_url = sys.argv[1]
    page = (requests.get(page_url).text.split('\n'))

    for i in page:
        if '.mp4' in i:  # finds the url in the source code of the video that contains the
            url = i      # link the stream link that contains the .m3u8 files
            break

    title = re.split('/', page_url)[-2]  # get the title of the video (it's the last segment of the url, I'm lazy)

    video_url = url.split('.mp4')[0][13:]+'.mp4'  # extract the forementioned link

    video_file = requests.get(video_url).text.split('\n')  # getting the .mp4 link

    for i in video_file:
        if '.mp4' in i:
            url_root = (i.split("'")[1].split('.mp4')[0]+'.mp4/')  # find the link we will use to the .m3u8 files

    playlist_m3u8 = requests.get(url_root+'playlist.m3u8', verify=False).text  # this file contains
    chunklist_url = playlist_m3u8.split('\n')[3]  # the link for the file that contains the links of each video segment
    chunklist_m3u8 = requests.get(url_root + chunklist_url, verify=False).text  # we generate it and get the file
    chunklist_lines = chunklist_m3u8.split('\n')

    for i in chunklist_lines:
        if '.ts' in i:  # we get each segment filename that's used to generate the urls of each
            files.append(i)
    text = ''


    def download(link):
        with open(link, 'wb') as f:
            file = requests.get(url_root+link, verify=False)
            f.write(file.content)
            global text

        return


    for i in files:
        text += 'file '+i+'\n'  # this text contains the segment names and is used in the ffmpeg
        # to join them to generate the final video

    pool = ThreadPool(5)  # multithreading to download many segments simultaniously
    thread = pool.map(download, files)
    pool.close()
    pool.join()

    w = open('list.txt', 'w+')  # the file with the filenames for the ffmpeg
    w.write(text)
    w.close()

    os.system(('ffmpeg -f concat -i list.txt -acodec copy -vcodec copy {0}.mp4').format(title))   # finally we can GENERATE THE VIDEO

    for i in files:
        os.remove(i)
