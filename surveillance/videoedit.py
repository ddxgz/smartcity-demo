import os
import commands
import time
import string
import sys
import logging
import functools

from utils import funclogger, time2Stamp, stamp2Time

logging.basicConfig(level=logging.DEBUG)


DEBUG = 1

ENDPOINT="http://10.200.45.160:8080/auth/v1.0"
USERNAME="test:tester"
USERKEY="testing"

CONTAINER="DEMOROOM"
FILE_SUFFIX="ts"
SEGMENT_TIME_LEN="10"
SEGMENT_PREFIX="uwsgitst"

BIG_FOLDER="/usr/share/nginx/html/video/hls"
#NEWFOLDER="3031"
#VIDEOFOLDER="/usr/share/nginx/html/video/hls"
#HLSFOLDER="/usr/share/nginx/html/video/hls"
LIST_NAME="ffmpegts.m3u8"
SEG_NAME="seg%04d.ts"
LIST_VIDEO_TO_COMBINE = "videolist.txt"
COMBINED_VIEDO_NAME="combined.ts"
LIST_FOLDER="/usr/share/nginx/html/video/hls"
HTTP_PREFIX="http://10.200.46.209:80/video/hls/"

DEFAULT_LIST = "http://10.200.46.209:80/video/hls/3031/default.m3u8"

EVENTS_TXT = "/root/django/mysite/polls/events.txt"

START_TIME="2014-07-29 16:36:27"
END_TIME="2014-07-29 16:47:27"
#INTERVAL=


@funclogger('------------editting----------')
def editting(start_time, end_time, source_folder, output_folder):
    # time1 = time2Stamp(start_time)
    # time2 = time2Stamp(end_time)
    # time1 = int(time1)
    # time2 = int(time2)
    # logging.debug("start time: %s, time1: %s", start_time, time1)
    # logging.debug("end time:  %s, time2: %s", end_time, time2)
    # video_list is in order
    video_list, suffix = videos_in_duration(start_time, end_time, source_folder)
    logging.debug('video_list:%s, suffix: %s' % (video_list, suffix))
    # combine videos into one
    videoname = str(start_time) + '-' + str(end_time)
    full_video = combine_videos(video_list, source_folder, videoname, suffix)
    logging.debug('full video: %s' % full_video)
    # cut head and tail
    head_shift_time = start_time - int(video_list[0][-14:-4])
    duration_time = end_time - start_time + 1
    video_output = cut_video(full_video, source_folder, head_shift_time, duration_time)
    logging.debug('video_output:%s' % video_output)


def videos_in_duration(start_time, end_time, source_folder, reverse=False):
    """
    :start_time, timestamp
    :end_time, timestamp
    :source_folder, string 

    return:
    video_list, suffix
    """
    logging.debug('start time:%s, endtime: %s, source folder:%s' % (start_time, end_time, 
        source_folder))
    files = os.listdir(source_folder)
    logging.debug('files in source folder:%s' % files)
    videos = get_file_with_prefix(files, frefix='DEMO_')
    suffix = videos[0][-4:]
    stamps = []
    video_stamps = {}
    videos_in_duration = []
    for video in videos:
        stamp = video[video.find("_") + 1:video.find(".")]
        stamp = string.atoi(stamp)
        # logging.debug('stamp:%s' % stamp)
        stamps.append(stamp)
        video_stamps[str(stamp)] = video
        # logging.debug('stamps:%s' % stamps)
        # logging.debug('video_stamps:%s' % video_stamps)
    stamps.sort(reverse=True)
    logging.debug('stamps:%s' % stamps)
    for stamp in stamps:
        if stamp <= end_time:
            if stamp <= start_time:
                videos_in_duration.append(video_stamps.get(str(stamp)))
                break
            videos_in_duration.append(video_stamps.get(str(stamp)))
            continue
    logging.debug('videos_in_duration:%s' % videos_in_duration)
    videos_path_in_duration = []
    for video in videos_in_duration:
        videos_path_in_duration.append(source_folder + video)
    videos_path_in_duration.sort(reverse=reverse)
    logging.debug('videos_path_in_duration:%s' % videos_path_in_duration)
    return videos_path_in_duration, suffix


def get_file_with_prefix(files, frefix='DEMO_'):
    videos = []
    for file_ in files:
        if len(file_) > len(frefix) and file_[0:len(frefix)] == frefix:
            videos.append(file_)
            logging.debug('file is video:%s' % videos)
    return videos

def combine_videos(videos, source_folder, videoname, suffix):
    logging.debug('in combine_videos:%s' % videos)
    new_folder = source_folder + 'concats/'
    # need a list file of video path and names, used for combining videos by ffmpeg  
    video_list_file = write_ffmpeg_concat_file(videos, new_folder, videoname)
    logging.debug('in combine_videos, video_list_file:%s' % video_list_file)
    # call ffmpeg to combine videos
    stat = commands.getoutput("ffmpeg -f concat -i " + video_list_file +  
        " -y " + " -c copy " +  new_folder + videoname + '-notfixed' + suffix)
    logging.debug('in combine_videos, stat:%s' % stat)
    return new_folder + videoname + '-notfixed' + suffix


def write_ffmpeg_concat_file(list_to_write, source_folder, videoname):
    logging.debug('in write_ffmpeg_concat_file:%s' % list_to_write)
    list_file_path_name =  source_folder + videoname + '.txt'
    file_object = open(list_file_path_name,"w+")
    try:
        for video in list_to_write:
            file_object.write("file '" + video + "'\n")
    except:
        logging.debug('write_ffmpeg_concat_file - try to write failed!')
    finally:
        file_object.close( )
    return list_file_path_name


def cut_video(full_video, source_folder, head_shift_time, duration_time):
    """
    """
    cut_video_name = full_video[-34:-13] + full_video[-4:]
    cut_video = source_folder + 'upload/' + cut_video_name
    logging.debug('in cut_video, cut_video:%s' % cut_video)
    # ffmpeg
    # stat = commands.getoutput("ffmpeg -i " + first_video + " -ss " + shift_time + " -to " #+ in
    #     + " -acodec copy -vcodec copy " + LIST_FOLDER + "/" + new_folder + "/" + cut_video)
    stat = commands.getoutput("ffmpeg -i " + full_video + " -y " +
        " -ss " + str(head_shift_time) + ' -t ' + str(duration_time)  + 
        " -acodec copy -vcodec copy " + cut_video)
    logging.debug('in cut_video, stat:%s' % stat)
    return cut_video


"""
below is old
=============================================================================
"""
def selectObj(start_time, end_time, new_folder):
    time1 = time2Stamp(start_time)
    time2 = time2Stamp(end_time)
    time1 = int(time1)
    time2 = int(time2)
    if DEBUG:
        print("start time: ", start_time, time1)
        print("end time: ", end_time, time2)
    #print(time2)

    #objs=commands.getstatusoutput("swift -A " + $endpoint " -U "+$username " -K " +$userkey +" list " +$CONTAINER \
        #list DEMOROOM")
    #objs=commands.getoutput("swift -A http://10.200.45.160:8080/auth/v1.0 -U test:tester -K testing list DEMOROOM")
    objs = commands.getoutput("swift -A " + ENDPOINT + " -U "+USERNAME +" -K " 
        + USERKEY + " list " + CONTAINER)
   # os.system("swift -A " + ENDPOINT +" -U "+USERNAME +" -K " +USERKEY +" list " +CONTAINER )  
    #if DEBUG:
        #print (objs)
    b = ''.join(objs)
    objs = b.split("\n")
    objStamps = []
    for obj in objs:
       #objStamp=obj.split('_|.')
        stamp = obj[obj.find("_") + 1:obj.find(".")]
        #objStamp=objStampSuffix[1].split('.')
        stamp = string.atoi(stamp)
        objStamps.append(stamp)

    # sort the timestamp in case of the list from swift is not sorted
    objStamps.sort()
    if DEBUG:
        #print(objStamps)
        pass
    HLSFOLDER = BIG_FOLDER + "/" + new_folder
    VIDEOFOLDER=HLSFOLDER
    commands.getoutput("mkdir " + HLSFOLDER)
    downloadedVideos = []
    for (i,objStamp) in enumerate(objStamps):
        #print(objStamp)
        # download the first obj
        # to reconstruct, find the first and last video first, then download videos 
        # between them.
        assert(i <= (len(objStamps)-1))
        if objStamp < time1 and objStamps[i + 1] > time1 and i < (len(objStamps)-1):
            assert(objStamp < time1 and objStamps[i + 1] > time1)
            OBJECT = getObjName(objStamp)
            stat = commands.getoutput("swift -A " + ENDPOINT + " -U "+ USERNAME 
                + " -K " + USERKEY + " download " + CONTAINER + " "+ OBJECT 
                +" --output " + VIDEOFOLDER + "/" + OBJECT)
            #stat=commands.getoutput("swift -A " + ENDPOINT +" -U "+USERNAME +" -K " +USERKEY +" stat " +CONTAINER+" "+OBJECT)
            head_shift = time1 - objStamp
            if DEBUG:                
                print("objstamp:", objStamp)
                print("objstamp+1:", objStamps[i + 1])
                print("start time:", time1)
                print("head_shift", head_shift) 
                print("head_shift timestamp to time: ", stamp2Time(head_shift))
                print(stat)               
            downloadedVideos.append(VIDEOFOLDER + "/" + OBJECT)
            # for improving
            # start to play video when the first block is downloaded
            #videoToPlay()
        if objStamp >= time1 and objStamp < time2:
            if DEBUG:
                print("objstamp:", objStamp)
        #while (time1==objStamp && )
            #objs=commands.getstatusoutput("")
            OBJECT = getObjName(objStamp)
            stat = commands.getoutput("swift -A " + ENDPOINT + " -U " + USERNAME 
                + " -K " + USERKEY + " download " + CONTAINER + " " + OBJECT 
                + " --output " + VIDEOFOLDER + "/" + OBJECT)
            #stat=commands.getoutput("swift -A " + ENDPOINT +" -U "+USERNAME +" -K " +USERKEY +" stat " +CONTAINER+" "+OBJECT)
            if DEBUG:
                print (stat)
                #print("downloaded objStamp:", objStamp)
            downloadedVideos.append(VIDEOFOLDER + "/" + OBJECT)
        if i < (len(objStamps)-1) and objStamps[i + 1] >= time2 and objStamp < time2: 
            tail_shift = time2 - objStamp
            if DEBUG:                
                print("last downloadedVideo:", downloadedVideos[len(downloadedVideos)-1])
                print("end time:", time2)
                print("tail_shift", tail_shift) 
                print("tail_shift timestamp to time: ", stamp2Time(tail_shift))
                print(stat)  
            #for improving
            #refresh the m3u8 when other blocks are downloaded
        #print (downloadedVideos)
    if len(downloadedVideos) > 0:
        if DEBUG:
            print("downloadedVideos > 0, to get listToPlay")
        #listToPlay = prepareVideo(downloadedVideos,new_folder, head_shift, tail_shift)
        listToPlay = prepareVideo(downloadedVideos, new_folder, 0, tail_shift)
        #listToPlay = prepareVideo(downloadedVideos,new_folder)
        return listToPlay, head_shift
    else:
        print("no video downloaded")
        return DEFAULT_LIST, head_shift


def prepareVideo(videos, new_folder, head_shift, tail_shift):
    if DEBUG:
        print("in prepareVideo, 4 params")
    video_list = videos
    if head_shift:
        video_list[0] = cut_head_time(videos[0], new_folder, str(head_shift))
    if tail_shift:
        video_list[len(videos)-1] = cut_tail_time(videos[len(videos)-1], new_folder, str(tail_shift))
    if DEBUG:
            print(video_list[0])
            print(video_list[len(videos)-1])
    if len(videos) > 1:
        if DEBUG:
            print("number of downloaded videos > 1, start to combine")
        fullVideo = combineVideos(video_list, new_folder)
        listToPlay = segmentToList(fullVideo, new_folder)
    else:
        if DEBUG:
            print("number of downloaded videos <= 1")
        listToPlay = segmentToList(video_list[0], new_folder)
    return listToPlay


def prepareVideo3(videos, new_folder, tail_shift):
    if DEBUG:
        print("in prepareVideo, 3 params")
    video_list = videos
    #video_list[0] = cut_head_time(videos[0], new_folder, head_shift)
    video_list[len(videos)-1] = cut_tail_time(videos[len(videos)-1], new_folder, tail_shift)
    if DEBUG:
            print(video_list[0])
            print(video_list[len(videos)-1])
    if len(videos) > 1:
        if DEBUG:
            print("number of downloaded videos > 1, start to combine")
        fullVideo = combineVideos(video_list, new_folder)
        listToPlay = segmentToList(fullVideo, new_folder)
    else:
        if DEBUG:
            print("number of downloaded videos <= 1")
        listToPlay = segmentToList(video_list[0], new_folder)
    return listToPlay


def prepareVideo2(videos, new_folder):
    if DEBUG:
        print("in prepareVideo, 2 params")
    #video_list = videos
    #video_list[0] = cut_to_targettime(videos[0], new_folder, shift_time)
    #if DEBUG:
            #print(video_list[0])
    if len(videos) > 1:
        if DEBUG:
            print("number of downloaded videos > 1, start to combine")
        fullVideo = combineVideos(videos, new_folder)
        listToPlay = segmentToList(fullVideo, new_folder)
    else:
        listToPlay = segmentToList(videos[0], new_folder)
    return listToPlay

# not used
def cut_head_time(first_video, new_folder, shift_time):
    """
    Used for cut off the head part when the request start_time is different 
    from the start time of the first downloaded video.
    """
    cut_video = "new_indexed.ts"
    # ffmpeg
    stat = commands.getoutput("ffmpeg -i " + first_video + " -ss " + shift_time + " -to " #+ in
        + " -acodec copy -vcodec copy " + LIST_FOLDER + "/" + new_folder + "/" + cut_video)
    cut_video = LIST_FOLDER + "/" + new_folder + "/" + cut_video
    if DEBUG:
        print(stat)
        print("cut_video: ", cut_video)
    return cut_video


def cut_tail_time(last_video, new_folder, shift_time):
    """
    Used for cut off the tail part when the request end_time is different 
    from the end time of the last downloaded video.
    """
    cut_video = "new_indexed.ts"
    # ffmpeg
    stat = commands.getoutput("ffmpeg -i " + last_video + " -ss 0 " + " -to " + shift_time
        + " -acodec copy -vcodec copy " + LIST_FOLDER + "/" + new_folder + "/" + cut_video)
    cut_video = LIST_FOLDER + "/" + new_folder + "/" + cut_video
    if DEBUG:
        print(stat)
        print("cut_video: ", cut_video)
    return cut_video


def segmentToList(fullVideo, new_folder):
   # stat=commands.getoutput("segmenter -i " + fullVideo+" -d "+SEGMENT_TIME_LEN+" -o "+ SEGMENT_PREFIX+" -x "+LIST_FOLDER+"/"+new_folder+"/"+LIST_NAME+" -p " +HTTP_PREFIX)
    stat = commands.getoutput("ffmpeg -i " + fullVideo + " -codec copy -f segment \
        -segment_time  " + SEGMENT_TIME_LEN + " -segment_list " + LIST_FOLDER 
        + "/" + new_folder + "/" + LIST_NAME + " -map 0 " + LIST_FOLDER + "/" 
        + new_folder + "/" + SEG_NAME)
    listForPlay = HTTP_PREFIX + new_folder + "/" + LIST_NAME
    #moveVideoFiles(LIST_FOLDER)
    return  listForPlay


#useless
def moveVideoFiles(targetFolder):
    commands.getoutput("mv " + "*.ts " + targetFolder)


def combineVideos__old(videos, new_folder):
    #stat=commands.getoutput("ls")
    sorted_videos = array_str_sort(videos)
    # need a list file of video path and names, used for combining videos by ffmpeg  
    video_list_file = write_file(sorted_videos, new_folder)
    # call ffmpeg to combine videos
    stat = commands.getoutput("ffmpeg -f concat -i " + video_list_file 
        + " -c copy " + LIST_FOLDER + "/" + new_folder + "/" + COMBINED_VIEDO_NAME)
    fullVideo = LIST_FOLDER + "/" + new_folder + "/" + COMBINED_VIEDO_NAME
    return fullVideo


def write_file(list_to_write, new_folder):
    list_file_path_name = LIST_FOLDER + "/" + new_folder + "/" + LIST_VIDEO_TO_COMBINE
    file_object = open(list_file_path_name,"w+")
    try:
        for video in list_to_write:
            file_object.write("file '" + video + "'\n")
    finally:
        file_object.close( )
    return list_file_path_name


def array_str_sort(str_array):
    sorted_str_array = sorted(str_array)
    return sorted_str_array


def getObjName(stamp):
    stampStr = str(stamp)
    objName = CONTAINER + "_" + stampStr + "." + FILE_SUFFIX
    return objName


def last_ten(array):
    #if DEBUG:
        #print("array length: %d", len(array)
    if len(array) >= 10:
        ten = array[len(array)-10:]
        return ten
    else:
        return array


def str2List(string_with_linebreak):
    return string_with_linebreak.split('\n')


def read_lines(infile, num_lines):
    """
    num_cases: number of cases
    all_cases: a list to store cases
    use a dict to store each case
    {num:N,
     len:L,
     outlets:[],
     devices:[]}

    num: number of deivces or outlets
    len: length of electric flow   
    """
    lines = []
    if DEBUG:
        print('in read_in()')   
    try:
        file_in = open(infile, 'r')
    except:
        print('reading error')
    else:
        for i in range(0,num_lines):
            line = file_in.readline()
            line = line.split('\n') 
            lines.append(line[0])
        #all_lines = all_lines.split('\n')
        #num_cases = all_lines[0]
        #count = int(num_cases)
    return lines


class VideoProcessor(object):
    def __init__(self, conn_params):
        self.endpoint = ENDPOINT
        self.tenant_user = USERNAME
        self.userkey = USERKEY
        #print(self._start_time)
        #if 1 == 0:
            #print ("...")

    def get_list(self, params):
        """
        will return the playlist and shift_time
        """
        self._start_time = params[0]
        self._end_time = params[1]
        self._newfolder = params[2]
        if DEBUG:
            print("process.py in debug mode")
            print("_start:%s, _end:%s, _newfolder:%s" % (self._start_time,
                self._end_time, self._newfolder))
        return selectObj(self._start_time,self._end_time,self._newfolder)

    def get_event_lists(self, num_events):
        """
        Return the a dict contains the asked number of event playlists 
        with the camera names
        [['camera':camera0, 'playlist':playlist0, 'shift_time':21],[]]
        :param num_events, how many events required
        """
        events = []
        records = self.recent_event_record(num_events)
        for record in records:
            end_time = stamp2Time(int(time2Stamp(record[2]) + 59))
            if DEBUG:
                print("endtime:%s" % end_time)
            playlist, shift_time = self.get_list([record[2], end_time, 
                str(time.time())+str(time2Stamp(record[2]))])
            events.append({'camera':record[1],'playlist':playlist,
                'shift_time':shift_time})
        return events

    def recent_event_record(self, num):
        """
        A record looks like this:
            Tenant:User,Camera,  Time,               Tag
            test:tester,DEMOROOM,08/07/2014 04:11:12,1
        return tuples in a list, each tuple is a event record 
        """
        lines = read_lines(EVENTS_TXT, num+1)
        if DEBUG:
            print("lines:%s", lines)
        records = []
        for line in lines[1:]:
            items = line.split(',')
            records.append((items[0],items[1],items[2],items[3]))
        if DEBUG:
            print("records:%s", records)
        return records

    def get_shift_time(self):
        pass


class SwiftProcessor(object):
    """
        Perform some actions with swift

        :param params: endpont, tenant:username, userkey
    """
    
    def __init__(self, params):
        self.endpoint = ENDPOINT
        self.tenant_user = USERNAME
        self.userkey = USERKEY
        if DEBUG:
            print("SwiftProcessor init, in debug mode")
            print("endpoint, user, key", self.endpoint)

    def list_container(self):
        if DEBUG:
            print("in list_container")
            print("endpoint, user, key", self.endpoint, self.tenant_user, self.userkey)
        containers = commands.getoutput("swift -A " + self.endpoint + " -U "
            + self.tenant_user + " -K " + self.userkey + " list")
        container_list = str2List(containers)
        if DEBUG:
            print(last_ten(container_list))
        return last_ten(container_list)

    def list_object(self, container):
        if DEBUG:
            print("in list_obj, container=", container)
        #if container:
            #container = DEMOROOM
        objs = commands.getoutput("swift -A " + self.endpoint + " -U "
            + self.tenant_user + " -K " + self.userkey + " list " + container)
        obj_list = str2List(objs)
        if DEBUG:
            #print(objs)
            print(last_ten(obj_list))
        return last_ten(obj_list)

        
def main():
    print("t")
    params = [START_TIME,END_TIME,"12345"]
    vProcessor = VideoProcessor(params)
    listToPlay = vProcessor.get_event_lists(4)
    print(listToPlay)


if __name__ == '__main__':
    editting(1430720523, 1430720740, '/home/pc/catch_video/videos/' ,
        '/home/pc/catch_video/videos/upload/')
    # editting(1430404940, 1430404952, '/root/catch_video/videos/' ,
    #     '/root/catch_video/videos/upload/')
    #sys.exit(main())
