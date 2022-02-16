#!/bin/bash
# Reduces size of images and labels and executes conversion
echo introduce folder, resolution and perc

python3 resizeFolder.py $1 $3 $4
python3 django_to_coco.py Resized $2
rm -f -R Res2
