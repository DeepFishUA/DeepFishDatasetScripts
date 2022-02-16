#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Mueve y renombra los archivos a una única carpeta

from genericpath import isfile
import warnings, random
import numpy as np
import pandas as pd
import json, sys
import os
from shutil import copyfile
from PIL import Image

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 
yolactDatabasePath = "~/Desktop/yolact-custom-data/dataset/DeepFish/"
yTrain = yolactDatabasePath + "train"
yVal = yolactDatabasePath + "val"

# Por ahora cambiar JPG a jpg, pero se podria hacer un preprocesado aqui
def preprocessImages(images): 
    for im in os.listdir(images):
        if im.endswith(".JPG"): 
            print("changed to minus", im) 
            exit()              
            imMinus = im[:-4] + '.jpg'
            os.system("mv " + im + " " + imMinus)

def fileExists(file):
    try:
        return os.path.isfile(file)
    except:
        return False

def labelToImg(obj):
    return obj[:-13] + ".jpg"

def imgToLabel(obj):
    return obj[:-4] + '__labels.json'

# Move all images to temp images folder
def moveToImages(root_path, output_path = "images/"):
    os.system("rm -f -R " + output_path)
    os.system("mkdir " + output_path)

    all_folders = os.listdir(root_path)
    
    # It means is all a big folder
    if not os.path.isdir(root_path + '/' + all_folders[0]):
        moveAllToImages(root_path, output_path)
    # Subfolders by date
    else:
        for folder_paths in all_folders:
            if folder_paths[0].isnumeric() and os.path.isdir(root_path + '/' + folder_paths): 
                folder_dir = root_path + '/' + folder_paths + '/'
                for fil in os.listdir(folder_dir): 
                    if fil.endswith(".jpg") and fil.startswith("B"):
                        try: # Don't copy jpg without json
                            fLabel = imgToLabel(fil)
                            copyfile(folder_dir + fLabel, output_path + folder_paths + '-' + fLabel) 
                            copyfile(folder_dir + fil,  output_path + folder_paths + '-' + fil) 
                        except:
                            continue


# Prepared to have it all in one folder
def moveAllToImages(root_path, output_path = "images/"):        
    os.system("rm -f -R " + output_path)
    os.system("mkdir " + output_path)
    all_files = os.listdir(root_path)
    for fil in all_files:
        # One only folder without dates prefix
        if os.path.isfile(root_path + '/' + fil):
            if not root_path.endswith("/"):
                root_path = root_path + '/'
            fil_dir = root_path + fil
            if not "E" in fil: 
                try: 
                    copyfile(fil_dir,  output_path + fil) 
                except:
                    continue



def moveimageTrainVal(image, moved, total, val, train):
    fLabel = image[:-4] + '__labels.json'
    if (moved / total) < pv: # Val
        folder = "val/"
        val += 1
    else: # Train
        folder = "train/"            
        train += 1
    try:
        os.rename('images/' + fLabel, folder + "images/" + fLabel)
        os.rename('images/' + image, folder + "images/" + image)
    except:                         
        pass
    return val, train

def duplicateTrainImages(image, moved):
    fLabel = image[:-4] + '__labels.json'
    folder = "train/"
    orig = folder + "images/"
    dup = moved
    newImg = orig + image[:-4] + str(moved) + ".jpg"
    while fileExists(newImg):
        dup += 3
        newImg = orig + image[:-4] + str(dup) + ".jpg"

    try:
        copyfile(orig + fLabel, orig + fLabel[:-13] + str(dup) + '__labels.json')
        copyfile(orig + image, newImg)
        return moved + 1
    except:                         
        return moved


def getMaxImInstances(imagesInCategorias):
    max = 0
    for cat in imagesInCategorias:
        if len(imagesInCategorias[cat]) > max:
            max = len(imagesInCategorias[cat])
    return max

def moveTrainVal(percVal, instancias, imagesInCategorias, Manual_Balance = False):
    os.system("rm -f -R train val")
    os.system("mkdir train val")
    os.system("mkdir train/images val/images")
    global pv
    pv = float(percVal) / 100
    instanciasRepartidas = {}
    globalTotal = getMaxImInstances(imagesInCategorias)

    for cat in imagesInCategorias:
        total = len(imagesInCategorias[cat])
        moved, val, train = 0, 0, 0

        for image in imagesInCategorias[cat]:
            val, train = moveimageTrainVal(image, moved, total, val, train)
            moved += 1

        movedBal = 0
        if Manual_Balance:
            totalBal = globalTotal - total
            while movedBal < totalBal:
                movedBal = duplicateTrainImages(random.choice(imagesInCategorias[cat]), movedBal) ## Todas interesan en train

        instanciasRepartidas[cat] = {"train": train + movedBal, "val": val}

    print(instanciasRepartidas)

    # Move the rest of the images
    noClasses_files = os.listdir('images/')
    totalR = len(noClasses_files)
    movedR = 0
    for file in noClasses_files:
        moveimageTrainVal(file, movedR, totalR, 0, 0)
        movedR += 2

def clean():
    os.system("rm -R images")
    os.system("rm -R train/images/*.json")
    os.system("rm -R val/images/*.json")

def moveToYolact():
    os.system("rm -r " + yTrain)
    os.system("rm -r " + yVal)
    os.system("cp -r train " + yTrain)
    os.system("cp -r val " + yVal)
    



    
    
    
    
    
    
    
    
    
    
    
    
    
    