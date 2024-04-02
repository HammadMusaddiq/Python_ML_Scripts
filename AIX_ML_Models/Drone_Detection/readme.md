This is FastAPI, for drone detection,

## RUN
In order to run:

if image is not already built.
1. sudo docker build -t (name_of_image) . 
2. sudo docker run -p 8003:out_port -d (name_of_image)

if image is already built
1. sudo docker run -p 8003:out_port -d (name_of_image)

## Flow

Model initialization
Establishing connection with FTP

### Image
can receive image in form of string of bytes or file or link
Perform inference
plot and upload on FTP
return FTP url and detection stats

### Video
Conversion of video into frames
perform inference
plot and store stats for each frame
recombine ploted frames to create video
upload video on FTP
return video URL and detection stats
