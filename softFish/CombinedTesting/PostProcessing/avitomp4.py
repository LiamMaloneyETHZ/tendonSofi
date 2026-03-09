import os

#function from https://stackoverflow.com/questions/22748617/python-avi-to-mp4, string work my own
def convert_avi_to_mp4(avi_file_path, output_name):
    #also said that we could take away the single quotes around the input and output
    os.popen("ffmpeg -i '{input}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}.mp4'".format(input = avi_file_path, output = output_name))
    return True

####ADD absolute path to video file below
abs_path="/home/srl-slim-tim/ForceTest/20250804_1257_f3.0Hz_film_test_data.avi"
output_name=abs_path[:-4] #removes the .avi part of the string

convert_avi_to_mp4(abs_path,output_name)