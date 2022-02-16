# DeepFishDatasetScripts
DeepFish project repository for dataset-related scripts.
Code prepared to convert files .JSON from the modification of Django Labeller used in the project DeepFish to one unic folder .JSON in COCO format. 

### Installation
 - Clone this repository and enter in it:
   ```Shell
   git clone https://github.com/DeepFishUA/DeepFishDatasetScripts.git
   cd DeepFishDatasetScripts
   ```
 - Copy your dataset of images with the structure:
   - <Folder_with_images>/<subfolder_with_date>/<imageX.jpg>
   - <Folder_with_images>/<subfolder_with_date>/<imageX.json>
 - Other structure available is withous subfolders:
   - <Folder_with_images>/<imageX.jpg>
   - <Folder_with_images>/<imageX.json>


### Convert directly to full folder
    ```Shell
    python3 django_to_coco_simple.py Folder_with_images
    ```

The output data_fish.json (.JSON with COCO format) will be on the folder "output_COCO" and it's images .jpg on the folder "output_COCO/images".

The output by console will be information about categories and classes useful if we are going to use yolact.


### Convert directly to train and data folders
    ```Shell
    python3 django_to_coco.py Folder_with_images percentajeValidation
    ```

The output data_fish.json (.JSON with COCO format) will be on the folder "train" and "val". Each one with it's images .jpg on the subfolder "images". 

The percentaje validation will refer to the presence of each class in the train and val set. By console output we will watch this instances per specie. 

The output by console will be information about categories and classes useful if we are going to use yolact.


### Resize images and labels
    
We may want to reduce the size of our images in order to increase the speed of our net, or adapt it's domain to the resolution of images it will receive. 

    ```Shell
    python3 resizeFolder.py Folder_with_images newResolutionX newResolutionY 
    ```

The output will be the images and it's labels with the same structure, reformated in a folder "Resized".

With the script "reduceSize.sh" we can execute the resizing and the connversion.

## Contact
If you have any doubt please let us know at uadeepfish@gmail.com.






