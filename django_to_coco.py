#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
import numpy as np
import pandas as pd
import json, sys
import os, moveImages, clasesEquivalence
from PIL import Image
import math

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

### instancias: number of instances in each class
### imagesInCategories: unique images in each class
categorias, data, instancias, imagesInCategories = {}, {}, {}, {}
counterCategorias = 0        
id_segmentation = 1

# Objective species. If activated, only files .json with this ones will be filtrated
#listSpecies = ["Mullus surmulentus", "Pagellus acarne", "Diplodus anularis", "Serranus scriba", "Mullus barbatus", "Pagrus pagrus", "Pagellus erythrinus","Spicara maena","Sepia officinalis","Symphodus tinca H","Scorpaena porcus","Symphodus tinca M","Sphyraena sphyraena"]
listSpecies = []

########################################################
# Test functions #
########################################################

def errorMessage(msg):
    print("\n\n\n\n\n\n\n###########################\nERROR:\n\n",msg,"\n###########################\n\n", file=sys.stderr)
    exit()

def execute_tests():

    ## Test 1
    # Checkc all images have annotations
    for im in range(len(data['images'])):
        if not is_image_in_annotations(im):
            errorMessage("Img: " + str(data['images'][im]) + " \n\nDoesn't contain annotations")

    ## Test 2
    # Checks all annotations have images
    for an in range(len(data['annotations'])):
        tiene_annotations = False 
        for im in range(len(data['images'])):
            if data['images'][im]['id'] == data['annotations'][an]['image_id']:
                tiene_annotations = True # Tiene al menos una
        if not tiene_annotations:
            errorMessage("Annotations: " + str(data['annotations'][an]) + " \n\nYou're image does not exist")
       
    
########################################################


def getImageID(name):
    for i in range(0, len(data['images'])):
        if data['images'][i]['file_name'] == name:
            return data['images'][i]['id']

def polyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))    

def bounding_box(x,y):
    bot_left_x = x[np.argmin(x)]
    bot_left_y = y[np.argmin(y)]
    top_right_x = x[np.argmax(x)]
    top_right_y = y[np.argmax(y)]

    return [bot_left_x, bot_left_y, top_right_x - bot_left_x, top_right_y - bot_left_y] # x, y, width, height 

def muestraCategorias(data, instanc):
    cadena = ""
    for cat in data['categories']: 
        cadena += str(cat['id']) + ": " + str(cat['id']) + " ,"

    print ("Categories", cadena)

    cadena = ""
    for cat in data['categories']: 
        cadena += '"' + str(cat['name']) + '"'
        if instanc:
            cadena += ": " + str(instancias[cat['name']])
        cadena += " ,"

    print ("Categories names: ", cadena)


# Assign id corresponding
def corrige_id(id, categoria):
    data[categoria][id]['id'] = id


# Deletes images by id. Once finded it will execute again
def elimina_imagenes(images): 
    counter = 0
    for im_id in images:
        del data['images'][im_id - counter]
        counter += 1 

# Checks annotations with that id of image
def is_image_in_annotations(id):
    for annotation in range(0, len(data['annotations'])):
        if(data['annotations'][annotation]['image_id'] == id): 
            return True
    return False

# Moves all corresponding annotation id to the new one 
def mueve_annotations(id_old, id_new):
    for annotation in range(0, len(data['annotations'])):
        if(data['annotations'][annotation]['image_id'] == id_old): 
            data['annotations'][annotation]['image_id'] = id_new

# Deletes all annotations if are not objective specie
def elimina_annotations_vacias():
    imagenes_a_eliminar = []
    for image_id in range(0, len(data['images'])):
        if not is_image_in_annotations(image_id):        
            imagenes_a_eliminar.append(image_id)

    elimina_imagenes(imagenes_a_eliminar) # Delete images without annotations
    
    # Una vez eliminadas todas las imágenes corregiremos las anotaciones asociadas (Guardadas con el id) y el propio id de la imagen
    # Once deleted all images, we will correct associated annotations. (Stored by id) and it's own image id.
    for image_id in range(0, len(data['images'])):
        mueve_annotations(data['images'][image_id]['id'], image_id) 
        corrige_id(image_id, 'images')

    for annotation_id in range(0, len(data['annotations'])):
       corrige_id(annotation_id, 'annotations')

# Read all the data
def countData():
    root_path = "images/"

    images, jsons = [], []
    jsons += [js for js in os.listdir(root_path) if js.endswith(".json")]
    # Qr images not added. If needed delete: '"B" in'
    images += [im for im in os.listdir(root_path) if im.endswith(".jpg") and "B" in im]

    id_images = 0        
    data['images'] = []
    for image in images:
        data_image = {}
        data_image['file_name'] = image
        data_image['id'] = id_images
        id_images += 1
        data['images'].append(data_image)

    data['annotations'] = []
    counter = 0
    for js in jsons:
        with open(root_path + js) as f:
            if js.endswith(".jpg"):
                print("javascript bad written",i)

            js_data = json.load(f)

            if  js_data['image_filename'].endswith(".json"):
                continue
            # Add prefix

            folder_full_route = js.split("-") 
            folder_route = folder_full_route[0:len(folder_full_route)-1]
            folder_route = '-'.join(str(x) for x in folder_route)
            sufix = folder_full_route[len(folder_full_route)-1]


            if js_data["image_filename"].endswith('.json'): 
                js_data["image_filename"] = moveImages.labelToImg(js_data["image_filename"])
            elif js[:-13] != js_data['image_filename'][:-4]: 
                js_data["image_filename"] = moveImages.labelToImg(sufix)

            imF = folder_route + '-' + js_data["image_filename"]
            js_data["image_filename"] = imF

            imF = "images/" + imF
            if not moveImages.fileExists(imF): 
                counter +=1 
                print("Imágenes mal asociadas: ", counter)
    

            for i in range(0, len(js_data['labels'])):
                #ifImage_id is null
                if not getImageID(js_data['image_filename']):
                    continue 

                catStr = js_data['labels'][i]['label_class']

                # Exclude tray to get sizes
                # if not catStr or catStr.startswith("size") or catStr.startswith("Tray") or catStr.startswith("polygon"):
                if not catStr or catStr.startswith("size") or catStr.startswith("polygon"):
                    continue

                # check if the class is already used with other name, and changes it
                catStr = clasesEquivalence.transformToClassName(catStr)

                # filter images, if tray, continue here to not assign it as a category
                # filter by species
                # if catStr not in listSpecies:
                    #continue


                if catStr not in categorias:
                    global counterCategorias
                    categorias[catStr] = counterCategorias
                    instancias[catStr] = 1
                    counterCategorias += 1
                    imagesInCategories[catStr] = [js_data['image_filename']]
                else: # It was already or it is a tray and we want it no more as category
                    instancias[catStr] += 1
                    if not js_data['image_filename'] in imagesInCategories[catStr]:
                        imagesInCategories[catStr].append(js_data['image_filename'])




# Same loop as before, but now we have conscience of all the data
def transcribeData(root_data): 
    # Tray reference
    tray_id = len(categorias)
    root_path = root_data + "/images/"

    images, jsons = [], []
    jsons += [js for js in os.listdir(root_path) if js.endswith(".json")]

    images += [im for im in os.listdir(root_path) if im.endswith(".jpg") and "B" in im]

    info_deepfish = {'description': 'DeepFish Dataset', 'url':'',
                    'version': 0.1, 'year':2021, 'date_created': '23/04/21'}
    licenses_deepfish = {'url': '', 'id': 0, 'name': 'DeepFish'}
    data['info'] = info_deepfish
    data['licenses'] = licenses_deepfish
    data['images'] = []

    id_images = 0
    for image in images:
        data_image = {}
        data_image['license'] = 0
        data_image['file_name'] = image
        im = Image.open(root_path + image)
        width, height = im.size
        data_image['width'] = width
        data_image['height'] = height
        data_image['id'] = id_images
        id_images += 1
        data['images'].append(data_image)

    data['annotations'] = []
    counter = 0
    for js in jsons:
        with open(root_path + js) as f:
            if js.endswith(".jpg"):
                print("javascript bad written",i)

            js_data = json.load(f)

            if  js_data['image_filename'].endswith(".json"):
                continue

            folder_full_route = js.split("-") 
            folder_route = folder_full_route[0:len(folder_full_route)-1]
            folder_route = '-'.join(str(x) for x in folder_route)
            sufix = folder_full_route[len(folder_full_route)-1]

            if js_data["image_filename"].endswith('.json'): 
                js_data["image_filename"] = moveImages.labelToImg(js_data["image_filename"])
            elif js[:-13] != js_data['image_filename'][:-4]: 
                js_data["image_filename"] = moveImages.labelToImg(sufix)

            imF = folder_route + '-' + js_data["image_filename"]
            js_data["image_filename"] = imF

            imF = root_path + imF
            if not moveImages.fileExists(imF): 
                counter +=1 
                # print("fichero:", js)
                # print("image_filename:", js_data['image_filename'])
                # print()
                print("Imágenes mal asociadas: ", counter, imF)
                # continue # Imágenes asociadas tienen diferente nombre que el label
    

            for i in range(0, len(js_data['labels'])):
                data_json = {}
                #ifImage_id is null
                if not getImageID(js_data['image_filename']):
                    continue 

                catStr = js_data['labels'][i]['label_class']
                
                if not catStr or catStr.startswith("size") or catStr.startswith("polygon"):
                    continue

                # check if the class is already used with other name, and changes it
                catStr = clasesEquivalence.transformToClassName(catStr)

                
                # Filter images not Tray and are specie out of objective
                if listSpecies:
                    if not catStr.startswith("Tray") and catStr not in listSpecies:
                        continue
                # It means we don't want to filter objective species
                else:
                    if catStr.startswith("Tray"):
                        continue


                regions = js_data['labels'][i]['regions']
                x, y = [], []
                for _ in range(0, len(regions)):
                    if len(regions[_]) > 50:
                        for __ in regions[_]:
                            x.append(__['x'])
                            y.append(__['y'])
                
                x = np.round(x,4)
                y = np.round(y,4)

                data_json['segmentation'] = [np.insert(y, np.arange(len(x)), x)]
                data_json['iscrowd'] = 0 

                data_json['image_id'] = getImageID(js_data['image_filename'])
                

                try:
                    data_json['bbox'] = bounding_box(x,y)
                except: 
                    continue
                # Area
                data_json['area'] = polyArea(x,y)
            
                # Id de la segmentacion
                global id_segmentation
                data_json['id'] = id_segmentation


                if not catStr.startswith("Tray"):
                    # Categoria del pez
                    data_json['category_id'] = categorias[catStr]

                    if math.isnan(categorias[catStr]) == False:
                        data['annotations'].append(data_json)
                    else:
                        print("Soy nan", catStr)
                        exit()
                else:
                    # Categoria de la bandeja
                    data_json['category_id'] = tray_id
                    data_json['category_id'] = catStr
                    #data['annotations'].append(data_json)
                    
                id_segmentation += 1

    data['categories'] = []
    # data_json = {}
    # data_json['supercategory'] = "tray"
    # data_json['id'] = tray_id
    # data_json['name'] = "tray"
    # data['categories'].append(data_json)
    # ## TODO other category for sizes

    for subCat in categorias:
        
        data_json = {}
        data_json['supercategory'] = "specie" 
        data_json['id'] = categorias[subCat]
        data_json['name'] = subCat
        data['categories'].append(data_json)


    elimina_annotations_vacias()

    ##################################################
    # Ejecuta test sobre conjunto train y validación
    ##################################################

    execute_tests()

    ##################################################

    pd.Series(data).to_json( root_data + '/data_fish.json')

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print("Introduce [root folder] [move_to_yolact?]") 
    exit()


############
## __main__:
############

moveImages.moveToImages(sys.argv[1])
countData()


moveImages.moveTrainVal(sys.argv[2], instancias, imagesInCategories)

transcribeData("train")
transcribeData("val")

# Assign true to show with instances
muestraCategorias(data, False) # You will have to change this in the config.py if you use yolact


# Mover a yolact
'''
if len(sys.argv) == 3:
    moveImages.clean()

    ## Directly in yolact
    moveImages.moveToYolact() # Moves train and val
'''
    

    
    
    
    
    
    
    
    
    
    