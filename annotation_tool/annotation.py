import cv2
import numpy as np
import argparse
import os.path
from Tkinter import *

parser = argparse.ArgumentParser(description='''Annotation tool for the license plate challenge. \n
                                                Double-click a spot on the image to create a point. \n
                                                The quad will be created when the 4th point is on the screen. \n
                                                Upon the quad creation, you will be asked to enter it's name, in our case, the plate number. \n
                                                To select a quad, click in one of its points. \n
                                                Once a quad is selected, you can reshape it by clicking and dragging its points. \n
                                                You can also delete a selected quad by pressing "BACKSPACE" \n
                                                Press "Enter" to save the annotation or "ESC" to discard your work.''')
parser.add_argument('image', help='Image file path to be annotated. Must be of a format supported by the OpenCV library (use jpg when in doubt).')
args = parser.parse_args()

pointObjs = []
quadObjs = []

class Image:
    """
    Image class encapsulates the image data
    """
    def __init__(self, filename):
        """
        Constructs the Image object.

        Args:
            param1 (str): The image filename.
        """
        self.filename = filename
        self.imageData = cv2.imread(self.filename,1)

    def redraw(self):
        """
        Redraws the image.
        """
        self.imageData = cv2.imread(self.filename,1)

    def getData(self):
        """
        Returns the image data.
        """
        return self.imageData


class TakeInput(object):
    """
    TakeInput encapsulates a TK window used to get the user input when 
    entering the plate number.
    """
    def __init__(self,requestMessage):
        """
        Initialize and instantiate the text input window.

        Args:
            requestMessage (str): The request to be displayed on the window.
        """
        self.root = Tk()
        self.string = ''
        self.frame = Frame(self.root)
        self.frame.pack()        
        self.acceptInput(requestMessage)

    def acceptInput(self,requestMessage):
        r = self.frame

        k = Label(r,text=requestMessage)
        k.pack(side='left')
        self.e = Entry(r,text='Name')
        self.e.pack(side='left')
        self.e.focus_set()
        b = Button(r,text='okay',command=self.gettext)
        b.pack(side='right')

    def gettext(self):
        self.string = self.e.get()
        self.root.destroy()

    def getString(self):
        return self.string

    def waitForInput(self):
        self.root.mainloop()


def getText(requestMessage):
    """
    This functions calls the text input window and returns the input string.
    """
    msgBox = TakeInput(requestMessage)
    msgBox.waitForInput()
    return msgBox.getString()

class Point:
    """
    The Point class encapsulates an pixel's coordinates and allows s
    everal operation on that pixel.
    """
    points = []
    drawing = False

    def __init__(self, x, y):
        self.coords = (x,y)
        self.x = x
        self.y = y
        self.radius = 8
        self.clicked = False
        Point.points.append(self.coords)

    def click(self,x,y):
        if x > self.x - self.radius and x < self.x + self.radius and y > self.y - self.radius and y < self.y + self.radius:
            self.clicked = True
            return True

    def update(self,x,y):
        temp = (x,y)
        if temp != self.coords:
            for point in Point.points:
                if point == self.coords:
                    index = Point.points.index(point)
                    Point.points.remove(point)
                    self.coords = temp
                    self.x = x
                    self.y = y
                    Point.points.insert(index, self.coords)

    def unclick(self):
        self.clicked = False

    def draw(self, img):
        cv2.circle(img.getData(), self.coords, self.radius, (0,0,255), -1)

    def isClicked(self):
        return self.clicked

    def getCoords(self):
        return self.coords

class Quad:
    """
    The Quad class encapsulates sets of four points, drawing a box on
    the screen cornered at the points coordenates.
    """
    selection = False

    def __init__(self, points):
        self.name = ''
        self.points = points
        self.clicked = False
        self.setName()
        self.coords = []
        for point in self.points:
            self.coords.append(point.getCoords())

    def click(self,x,y):
        for point in self.points:
            if point.click(x,y):
                self.clicked = True
                print('Quad ' + self.getName() + ' (' + str(self.getCoords()) + ') is has been selected.')
                return True
        return False

    def clickPoint(self,x,y):
        for point in self.points:
            if point.click(x,y):
                return True
        return False

    def unclick(self):
        print('Quad ' + self.getName() + ' (' + str(self.getCoords()) + ') is has been unselected.')
        self.clicked = False

    def unclickPoint(self):
        for point in self.points:
            point.unclick()

    def isClicked(self):
        return self.clicked

    def draw(self,img):
        pts = np.array(self.coords, np.int32)
        if self.clicked:
            cv2.polylines(img.getData(), [pts], True, (255,0,0), thickness=5)
        else:
            cv2.polylines(img.getData(), [pts], True, (0,0,255), thickness=5)
        for point in self.points:
            point.draw(img)

    def delete(self):
        for point in self.points:
            self.points.remove(point)

    def update(self,x,y):
        for point in self.points:
            if point.isClicked():
                index = self.coords.index(point.getCoords())
                self.coords.remove(point.getCoords())
                point.update(x,y)
                self.coords.insert(index, point.getCoords())



    def setName(self):
        self.name = getText('Enter the plate (ABC1234):')

    def getName(self):
        return self.name

    def getCoords(self):
        return self.coords

    def toString(self):
        output = ''
        for point in self.coords:
            output += str(point[0]) + ',' + str(point[1])
            if self.coords.index(point) != 3:
                output += ','
            else:
                output += ',' + self.name
        return output


# MouseCallback: Sets the behavior of clicking and dragging the points.
def mouseCallback(event, x, y, flags, params):
    global pointObjs
    global quadObjs
    if event == cv2.EVENT_LBUTTONDBLCLK and len(pointObjs) < 4:
        print('x: %d, y: %d')%(x,y)
        pointObjs.append(Point(x,y))
    elif event == cv2.EVENT_LBUTTONDOWN:
        Point.drawing = True
        if Quad.selection == False:
            for quad in quadObjs:
                if quad.click(x,y):
                    Quad.selection = True
        else:
            Quad.selection = False
            for quad in quadObjs:
                if quad.clickPoint(x,y):
                    Quad.selection = True
                    quad.click(x,y)
                elif quad.isClicked():
                    quad.unclick()
    elif event == cv2.EVENT_MOUSEMOVE:
        if Point.drawing:
            for quad in quadObjs:
                if quad.isClicked():
                    quad.update(x,y)
    elif event == cv2.EVENT_LBUTTONUP:
        Point.drawing = False
        for quad in quadObjs:
            quad.unclickPoint()

# Main Loop

img = Image(args.image)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 1200, 800)
cv2.setMouseCallback('image', mouseCallback)

print('\n')
print('Double-click a spot on the image to create a point.')
print('The quad will be created when the 4th point is on the screen.')
print('Upon the quad creation, you will be asked to enter it\'s name, in our case, the plate number.')
print('To select a quad, click in one of its points.')
print('Once a quad is selected, you can reshape it by clicking and dragging its points.')
print('You can also delete a selected quad by pressing "BACKSPACE"')
print('Press "Enter" to save the annotation or "ESC" to discard your work.')


while(1):
    key = cv2.waitKey(20)
    cv2.imshow('image', img.getData())
    img.redraw()
    for point in pointObjs:
        point.draw(img)
    for quad in quadObjs:
        quad.draw(img)
    if len(pointObjs) == 4:
        quadObjs.append(Quad(pointObjs))
        pointObjs = []
    if key & 0xFF == 8:
        print('deleting...')
        for quad in quadObjs:
            if quad.isClicked():
                print('Quad ' + quad.getName() + ' (' + str(quad.getCoords()) + ') is has been deleted.')
                quadObjs.remove(quad)
                quad.delete()
                Quad.selection = False
    if key & 0xFF == 27 or key & 0xFF == 13:
        break


print('\n')

# If the user desires to save the annotation, it will be saved as a txt file with the following format:
# x1,y2,x2,y2,x3,y3,x4,y4,ABC1234
# Where ABC1234 is the plate content inputed by the user.

if key & 0xFF == 13:
    if len(quadObjs) == 0:
        print('Error: no plate to annotate!')
    else:
        outputFilename = os.path.splitext(args.image)[0] + '.txt'
        f = open(outputFilename, 'w')
        for quad in quadObjs:
            print('output: ' + quad.toString())
            f.write(quad.toString())    
        f.close()
else:
    print('Exiting without saving annotation.')

print('\n')

cv2.destroyAllWindows() 