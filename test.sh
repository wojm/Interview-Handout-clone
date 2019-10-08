#!bin/baah

# This file prepares and runs the testing sweet

rm ./output.txt # will error without file, but still proceed
python3 ./starter_code.py
python3 ./test_output.py
