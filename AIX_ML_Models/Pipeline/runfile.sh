pkill python3
rm -rf *.log
echo "Killing all the existing processes"
sleep 2
nohup python3 local_video_hit.py > pipeline.log 2>&1 &

echo "Started All Python Services"
