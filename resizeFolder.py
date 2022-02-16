from glob import glob
import os, json, sys
import cv2

# Image from label
def findResIndex(path):
    for i in range(len(path)):
        if path[i] == "Resized":
            return i + 1

### Resize images
print("Resize images")

sufix    = "/*/*.jpg"

if len(sys.argv) != 4:
    print("Write the source folder <folder> and the resolucion <x> <y>")
    exit()

originFolder = sys.argv[1]
if originFolder[-1] == '/':
    originFolder = originFolder[:-1]

xResolucion = sys.argv[2] # 1280
yResolucion = sys.argv[3] # 960

os.system("rm -f -R Resized")
os.system("cp -r " + originFolder + " Resized")

allImages = glob( originFolder + sufix) 
destImages = glob("Resized" + sufix)


for i in range(len(allImages)):
    os.system("rm -R " + destImages[i])
    os.system("convert -resize " + xResolucion + "x" + yResolucion + " " + allImages[i] + " " + destImages[i])


### Resize labels

sufix = "/*/*labels.json"
allLabels = glob("Resized" + sufix) 


counterTumbadas = 0 # Imagenes tumbadas

for label_file in allLabels:
    with open(label_file, "r") as json_file:
        file = label_file.split("/")
        index_folder = findResIndex(file)
        last_identifier = '/'.join(file[index_folder:-1])
        img_path = originFolder + '/' + last_identifier + '/' + file[-1][:-13] + ".jpg"
        
        im = cv2.imread(img_path)

        try:
            # Rotated images
            if im.shape[1] < im.shape[0]:
                counterTumbadas += 1
                print("Rotated images", counterTumbadas, " image: ", img_path)
                continue

            xFactor = xResolucion / im.shape[1]
            yFactor = yResolucion / im.shape[0]
        except:
            print("File .jpg desn't exist ", img_path, "\nassociated to :", label_file, "\n\n")
            continue


        data = json.load(json_file)
        all_labels = data['labels']

        for i in range(len(all_labels)):
            label = all_labels[i]
            for k in range(len(label['regions'])): # Num regions
                region = label['regions'][k]
                for j in range(len(region)):
                    tupla = region[j]
                    tupla['x'] *= xFactor
                    tupla['y'] *= yFactor
                
    with open(label_file, "w") as jsonFile:
        json.dump(data, jsonFile)



