#!bin/baah

# This file prepares and runs the testing sweet

SECONDS=0 # time script

rm ./output.txt # will error without file, but still proceed
python3 ./starter_code.py
python3 ./test_output.py

duration=$SECONDS
echo "$(($duration / 60)) minutes and $(($duration % 60)) seconds elapsed."
