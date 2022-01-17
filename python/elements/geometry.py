from pyrevit import DB

class Geometry:

    def __init__(self):
        self.view = __revit__.ActiveUIDocument.ActiveView

    def get_geometry(self, el):
        """
        Returns a Revit Geometry Element from a Revit Element
        @parameter el   Revit Element ()
        @returns    GeometryElement object
        """
        options = DB.Options()
        options.ComputeReferences = True
        #options.IncludeNonVisibleObjects = True
        options.View = self.view
        return el.get_Geometry(options)

    def get_lines(self, el):
        """
        Returns a list of Revit Line objects from a Revit Element
        @parameter el   Revit Element
        @returns    List of line objects
        """
        geoElems = self.get_geometry(el)
        if geoElems is None: return []
        return [obj for obj in geoElems if type(obj) == DB.Line]

    def get_solids(self, el):
        """
        Returns a list of Revit Solid objects from a Revit Element
        @parameter el   Revit Element
        @returns    List of solid objects
        """
        geoElems = self.get_geometry(el)
        if geoElems is None: return []
        return [obj for obj in geoElems if type(obj) == DB.Solid]       

    def get_points(self, line):
        """
        Returns a list of Revit Points objects from a Revit Line
        @parameter el   Revit Element
        @returns    List of solid objects
        """
        assert type(line) == DB.Line, "Provided object is not a Revit Line object"

        points = line.Tessellate()
        return [(p.X, p.Y, p.Z) for p in points]     


    @staticmethod
    def create_line(point1,point2):
        return DB.Line.CreateBound(point1,point2)

    @staticmethod
    def copy_point(point,direction,dist,num):

        """Copy any "point" coordinates "num" times with a certain "distance" in certain "direction"

        :param point: Reference start point to be copied
        :type point: list
        :param direction: Reference direction for creating copied point
        :type direction: list
        :param dist: Certain distance between copied point
        :type dist: float
        :param num: Number of elements
        :type num: int
        :return: List of copied points 
        :rtype: list
        """
        coordX=point.X
        coordY=point.Y
        coordZ=point.Z
        points = []

        for i in range(len(num)):
            coordX=coordX + (dist * int(abs(direction[0])))
            coordY=coordY + (dist * int(abs(direction[1])))
            coordZ=coordZ + (dist * int(abs(direction[2])))
            p = DB.XYZ(coordX,coordY,coordZ)
            points.append(p)
        return points


class Vector:
    revitUI = __revit__.ActiveUIDocument
    revitDoc = __revit__.ActiveUIDocument.Document
    revitActiveViewId = __revit__.ActiveUIDocument.ActiveView.Id

    @staticmethod
    def createvector(curve):
        """Create vector from a given curve

        :param curve: Curve
        :type curve: Revit curve object
        :return: Vector 
        :rtype: Revit XYZ vector object
        """
        v = curve.GetEndPoint(0) - curve.GetEndPoint(1)
        return v

    @staticmethod
    def if_perpendicular(vector1, vector2):
        """Check if two vectors are perpendicular

        :param vector1: 1st vector
        :type vector1: Revit XYZ vector object
        :param vector2: 2nd vector
        :type vector2: Revit XYZ vector object
        :return: True if perpendicular 
        :rtype: boolean
        """
        if round(vector1.DotProduct(vector2),2) == 0:
            return True
        else:
            return False
