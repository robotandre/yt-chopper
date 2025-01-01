import os 
import string
import pathlib
import subprocess

####
# Directions:
# Make a .txt file with the same name as the video file with timestamps
# formatted like this:
##
# 0:20; outputTitle.mp4; Metadata Title; Track#
### Example:
### videofile.mp4
### videofile.txt
##
# 0:00; 1_outputTitle.mp4; Metadata Title; 1
# 0:30; 2_outputTitle.mp4; Second Metadata Title; 2
##
# This will make a video clip from 0:00 to 0:30 (named "1_outputTitle.mp4")
# and another for 0:30 to the end of the video (named "2_outputTitle.mp4").
###
# Not all options are necessary! You can include as little as timestamps!
##
# 0:00
# 0:30
##
# This would make the same clips but autogenerate a filename!
####

def getTimestamps(timestamp_filename):
    with open(timestamp_filename, 'r') as file_handle:
        timestamps = file_handle.read().strip().split('\n')
    return timestamps

def getVideoQueue():
    all_filenames = os.listdir()
    videoqueue = []

    for file in all_filenames:

        if file.endswith(".txt"):
            continue 

        basename = os.path.splitext(file)[0]
        timestamp_file = basename + ".txt"

        if timestamp_file in all_filenames:
            videoqueue.append(file)

    return videoqueue

def getVideoLength(filename):
    command = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', '-sexagesimal', filename
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    return result.stdout.strip()

startTime = "00:00"
stopTime = "00:00"

videoQueue = getVideoQueue()

for videoFilename in videoQueue:
    timestamps = getTimestamps(os.path.splitext(videoFilename)[0] + ".txt")
    videoLength = getVideoLength(videoFilename)
    
    timestampCounter = 0
    timestampLength = len(timestamps)

    while timestampCounter < timestampLength:
       currentTimestamp = timestamps[timestampCounter].split(";")
       try: 
        nextTimestamp = timestamps[timestampCounter+1].split(";")
        stopTime = nextTimestamp[0].strip()
       except:
        stopTime = videoLength


       # 1:00; filename.mp4; File Title; 1
       # Start; filename.mp4; File Title; File Track #

       startTime = currentTimestamp[0].strip()

       # Temporary name incase no input.
       outputFilename = f"clip_{startTime.replace(':', '-')}_{stopTime.replace(':', '-')}_{videoFilename[:-4]}.mp4"
       outputMetadata = ""

       if len(currentTimestamp) > 1:
           outputFilename = currentTimestamp[1].strip()
       
       if len(currentTimestamp) > 2:
           outputMetadata += f" -metadata title=\"{currentTimestamp[2].strip()}\""

       if len(currentTimestamp) > 3:
           outputMetadata += f" -metadata track=\"{currentTimestamp[3].strip()}\""

       if len(currentTimestamp) < 3:
           os.system(f"ffmpeg -ss {startTime} -to {stopTime} -i \"{videoFilename}\" \"{outputFilename}\"")
       else:
           os.system(f"ffmpeg -ss {startTime} -to {stopTime} -i \"{videoFilename}\" \"tmp_{outputFilename}\"")
           os.system(f"ffmpeg -i \"tmp_{outputFilename}\" -codec copy{outputMetadata} \"{outputFilename}\"")
           os.system(f"rm \"tmp_{outputFilename}\"")

       startTime = stopTime
       timestampCounter += 1