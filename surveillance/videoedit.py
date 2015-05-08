import os
import commands
import time
import string
import logging
import functools

from utils import funclogger, time2Stamp, stamp2Time

logging.basicConfig(level=logging.DEBUG)


@funclogger('------------editting----------')
def editting(start_time, end_time, source_folder, output_folder):
    # time1 = time2Stamp(start_time)
    # time2 = time2Stamp(end_time)
    # time1 = int(time1)
    # time2 = int(time2)
    # logging.debug("start time: %s, time1: %s", start_time, time1)
    # logging.debug("end time:  %s, time2: %s", end_time, time2)
    # video_list is in order, need to check if ealiest and latest video suitable
    video_list, suffix = videos_in_duration(start_time, end_time, source_folder)
    logging.debug('video_list:%s, suffix: %s' % (video_list, suffix))
    # combine videos into one
    videoname = str(start_time) + '-' + str(end_time)
    full_video = combine_videos(video_list, source_folder, videoname, suffix)
    logging.debug('full video: %s' % full_video)
    # cut head and tail
    head_shift_time = start_time - float(video_list[0][-14-(5+1):-4])
    duration_time = end_time - start_time + 1
    video_output = cut_video(full_video, source_folder, head_shift_time, duration_time)
    logging.debug('video_output:%s' % video_output)
    return video_output


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
    videos_path_in_duration = \
            [(source_folder + video) for video in videos_in_duration]
#    videos_path_in_duration = []
#    for video in videos_in_duration:
#        videos_path_in_duration.append(source_folder + video)
    videos_path_in_duration.sort(reverse=reverse)
    logging.debug('videos_path_in_duration:%s' % videos_path_in_duration)
    return videos_path_in_duration, suffix


def get_file_with_prefix(files, frefix='DEMO_'):
    videos = []
    for file_ in files:
        logging.debug('file_ :%s , len(file_): %s, frefix:%s, len prefix:%s, file_[0:len(frefix)]:%s' % (file_, len(file_), frefix, len(frefix), file_[0:len(frefix)] ))
        if len(file_) > len(frefix) and file_[0:len(frefix)] == frefix:
            videos.append(file_)
            logging.debug('file is video:%s' % file_)
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
        " -ss " + str(int(head_shift_time)) + ' -t ' + str(int(duration_time))  +
        " -acodec copy -vcodec copy " + cut_video)
    logging.debug('in cut_video, stat:%s' % stat)
    return cut_video


if __name__ == '__main__':
    editting(1430720523, 1430720740, '/home/pc/catch_video/videos/' ,
        '/home/pc/catch_video/videos/upload/')
    # editting(1430404940, 1430404952, '/root/catch_video/videos/' ,
    #     '/root/catch_video/videos/upload/')
    #sys.exit(main())
