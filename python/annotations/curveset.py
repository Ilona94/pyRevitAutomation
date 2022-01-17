from python.annotations.projection import Projection
from pyrevit import revit

class CurveList:
    """Class responsible for operations on a list of curves"""
    revitUI = __revit__.ActiveUIDocument
    revitDoc = __revit__.ActiveUIDocument.Document
    revitActiveViewId = __revit__.ActiveUIDocument.ActiveView.Id

    def __init__(self,curve_list):
        self.curve_list = curve_list

    #Check if two curves aren't too close together
    @staticmethod
    def intersects(curve1, curve2, tolerance = 0.0002):
        """Check if two curves intersect

        :param curve1: 1st curve to be checked
        :type curve1: Autodesk.Revit.DB.Line object
        :param curve2: 2nd curve to be checked
        :type curve2: Autodesk.Revit.DB.Line object
        :param tolerance: tolerance, defaults to 0.0002
        :type tolerance: float, optional
        :return: True if intersects, False if not
        :rtype: boolean
        """
        doc=revit.doc
        scale = doc.ActiveView.Scale
        ref_points = []
        ref_points.append(curve1.GetEndPoint(0))
        ref_points.append(curve1.GetEndPoint(1))

        for point in ref_points:
            projected_point = Projection.project_point_to_line(point, curve2)
            distance = projected_point.DistanceTo(point)
            if distance < tolerance *  scale:
                if round(distance, 2) == 0:
                    if "Disjoint" not in curve1.Intersect(curve2).ToString():
                        return True
                else:
                    return True
        return False

    #Check if a given curve on the curve list does not intersect with any other curve on the list
    def intersects_with(self, element_number):
        """Check if a given curve in a curve list intersects with any other curve in this list

        :param element_number: index of curve in list that needs to be checked
        :type element_number: integer
        :return: True if intersects with any other curve, False if not
        :rtype: boolean
        """
        for i,curve in enumerate(self.curve_list):
            if i == element_number:
                continue
            else:       
                if CurveList.intersects(self.curve_list[element_number], curve):
                    return True
        return False
