url=rtsp://admin:12345@10.200.45.148:554/MPEG-4/ch2/main/av_stream
# url_sdp=rtsp://admin:12345@10.200.45.148:554/live/1/0547424F573B085C/gsfp90ef4k0a6iap.sdp

now()
{
    echo `date "+%Y-%m-%d %H:%M:%S"`
}
touch /tmp/catchtime

while [ 1 ]; do
     timestamp=`date +"%s.%5N"`
# ffmpeg  -i $url -vcodec libx264  -timelimit 10 ./videos/out.mp4
# the command below is the one used 
     # ffmpeg  -t 00:00:05 -rtsp_transport tcp -i $url -codec copy /root/catch_video/videos/DEMO_$timestamp.avi
     ffmpeg  -t 00:00:10 -rtsp_transport tcp -i $url -codec copy /root/catch_video/videos/DEMO_$timestamp.avi
     # ffmpeg  -timelimit 5 -i $url -codec copy ./videos/DEMO_$timestamp.mp4
done

# scp ~/catch_video/videos/*.mp4 pc@10.200.44.73:/home/pc/smartvision/

# ffmpeg -i rtsp://admin:12345@10.200.45.148:554/MPEG-4/ch2/main/av_stream -ss 00:00:01.500 -f image2 -vframes 1 thu.jpg
