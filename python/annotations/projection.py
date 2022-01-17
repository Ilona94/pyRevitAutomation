from python.annotations.activeplane import ActivePlane
from python.elements.geometry import Geometry #import create_line

class Projection:
    active_view = __revit__.ActiveUIDocument.ActiveView
    def __init__(self):
        pass

#Function with changed name from "project_point_onto"
    @staticmethod
    def project_point_to_plane(point):
        """Project point on active plane
        
        :param point: Point as Revit Element
        :type point: Revit.DB.XYZ
        """
        active_plane = ActivePlane()
        vector = point - active_plane.origin
        dist = active_plane.normal.DotProduct(vector)
        #Project point on plane
        projected_point = point - dist * active_plane.normal
        return projected_point

#Project curve onto a plane
    @staticmethod
    def project_curve_to_plane(curve):
        """Create projected curve from point projection on active plane
        :param curve: Curve as Revit Element
        :type curve: Revit.DB.ModelLine
        """
        #projectedcurves1=[] Do we need it?
        active_plane = ActivePlane()
        start_point=curve.GetEndPoint(0)
        end_point=curve.GetEndPoint(1)
        start_point_projected = Projection.project_point_to_plane(start_point)
        end_point_projected = Projection.project_point_to_plane(end_point)
        line = Geometry.create_line(start_point_projected, end_point_projected)
        return line

    @staticmethod
    
    def project_point_to_line(point,curve):
        """Project point on line
        :param point: Point as Revit Element
        :type point: Revit.DB.XYZ (Creates an XYZ with the supplied coordinates)
        :param curve: Curve as Revit Element
        :type curve: Revit.DB.ModelLine
        :return: Point as Revit Element
        :rtype: Revit.DB.XYZ
        """
        #projected point
        P=point
        #curve start point
        A=curve.GetEndPoint(0)
        #curve end point
        B=curve.GetEndPoint(1)
        #Vector connecting given point (P) and curve start point (A)
        vector_AP=P-A
        #Vector connecting curve's start point (A) and end point (B)
        vector_AB=B-A
        #Dot_product as a scalar product or inner product
        dot_product_1=vector_AP.DotProduct(vector_AB)
        dot_product_2=vector_AB.DotProduct(vector_AB)
        division=dot_product_1/dot_product_2
        #Mathematical formula for projected point coordinates
        projected_point=A+division*vector_AB
        return projected_point
