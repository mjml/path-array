import FreeCAD as App
import Path
from math import *

Console = App.Console
eps = 1e-9

def place_array (objlist, props={}):
    Console.PrintMessage('---\n')
    rowheight = 0.0
    row = 1 # which row in the Y dir
    cnt = 1 # index of current item in X dir
    margin = props.get('margin') or [ 12.0, 0.0 ]
    pad = props.get('pad') or [ 8, 6.5 ]
    cursor = [ margin[0], margin[1] ]
    if not props.get('stock'):
         raise Exception("No stock dimensions provided")
    stock = props['stock']
    for obj in objlist:
        Console.PrintMessage("Aligning " + obj.Label + "\n")
        T1 = App.Matrix()
        T2 = App.Matrix()
        R1 = App.Matrix()
        R2 = App.Matrix()
        obj.Placement.Matrix = App.Matrix()
        bb = obj.Shape.BoundBox
        Console.PrintMessage("bb1 is " + str(bb) + "\n")
        dim = App.Vector( bb.XLength, bb.YLength, bb.ZLength )

        # Translate to origin
        T1.A14 = -bb.XMin
        T1.A24 = -bb.YMin
        T1.A34 = -bb.ZMin
        obj.Placement.Matrix = T1
        Console.PrintMessage("bb2 is " + str(bb) + "\n")

        # Rotate the object so that its minimal dimension coincides with Z
        if min(dim) > stock[2] + eps:
            raise Exception("The object " + obj.Label + " is too large to be milled from stock of depth " + str(stock[2]))
        if min(dim) == bb.XLength:
            # rotate X to Z
            R1.A11 = 0;  R1.A13 = 1
            R1.A31 = -1; R1.A33 = 0
        elif min(dim) == bb.YLength:
            # rotate Y to Z
            R1.A22 = 0;  R1.A23 = 1
            R1.A32 = -1; R1.A33 = 0
        else:
            # Sink Z so that Z=0 is the top surface
            R1.A34 = 0
        obj.Placement.Matrix = R1 * T1
        bb = obj.Shape.BoundBox
        Console.PrintMessage("bb3 is " + str(bb) + "\n")
        dim = App.Vector( bb.XLength, bb.YLength, bb.ZLength )
        
        # Orient the object to fit available space
        if (min(dim) == bb.XLength):
            R2.A11 = 0; R2.A12 = -1
            R2.A21 = 1; R2.A22 = 0
            R2.A14 = bb.YLength
        obj.Placement.Matrix = R2 * R1 * T1
        bb = obj.Shape.BoundBox # is this wrongly assuming a recompute/update after the Matrix update?
        Console.PrintMessage("bb4 is " + str(bb) + "\n")
        dim = App.Vector( bb.XLength, bb.YLength, bb.ZLength ) 
        if dim.y > rowheight + eps:
            rowheight = dim.y
        
        # Translate the object to the cursor position
        if cnt > 1:
            cursor[0] = cursor[0] + pad[0]
        
        if (cursor[0] + bb.XLength + margin[0] > stock[0] + eps):
            cursor[0] = margin[0]
            cnt = 1
            cursor[1] = cursor[1] + rowheight + pad[1]
            row = row + 1
            rowheight = bb.YLength
            if cursor[1] > stock[1] - margin[1]:
                raise Exception("Not enough room in stock for chosen objects! Try rearranging their order to see if you can find a better fit.")
    
        T2.A14 = cursor[0]
        T2.A24 = cursor[1]
        cursor[0] = cursor[0] + bb.XLength

        obj.Placement.Matrix = T2 * R2 * R1 * T1
        
        cnt = cnt + 1

            
        


