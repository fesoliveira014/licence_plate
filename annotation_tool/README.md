# Annotation Tool for the Licence Plate Challenge

This tool was created as part of my computer vision course at University of Campinas for the purpose of annotating imagens for the Licence Plate Challenge project. Feel free to use or modify it as you wish.

The tool was developed in Python 2.7.6 and OpenCV 2.4.11.

## Run Instructions

To run the script, use the following terminal command:

`python annotation.py [-h] image`

The image extensions supported are those supported by OpenCV 2.4.11. When in doubt, use JPEG files.

## Usage

Double-click a spot on the image to create a point.
The quad will be created when the 4th point is on the screen.
Upon the quad creation, you will be asked to enter it's name, in our case, the plate number.

To select a quad, click in one of its points.
Once a quad is selected, you can reshape it by clicking and dragging its points.
You can also delete a selected quad by pressing "BACKSPACE".
Press "Enter" to save the annotation or "ESC" to discard your work.
