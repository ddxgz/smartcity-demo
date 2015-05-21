import os
import commands
import time
import string
import logging
import functools

from utils import funclogger, time2Stamp, stamp2Time
from process import Config
from videoedit import get_file_with_prefix

logging.basicConfig(level=logging.DEBUG)


@funclogger('------------editting----------')
def videos_reaper(num_threshold):
    conf = Config()
    logging.debug('folder:%s' % (conf.video_dir))
    files = os.listdir(conf.video_dir)
    logging.debug('files in source folder:%s' % files)
    videos = get_file_with_prefix(files, frefix='DEMO_')
    if len(videos) > num_threshold:
        videos.sort()
        logging.debug('videos:%s' % videos)
        old_videos = videos[0:len(videos)-num_threshold]
        for old_video in old_videos:
            os.remove(conf.video_dir+old_video)
            logging.debug('removed: %s' % conf.video_dir+old_video)

# videos_reaper(3)
if __name__ == '__main__':
    while 1:
        time.sleep(60*60)
        logging.debug('reaping videos....')
        videos_reaper(100)
