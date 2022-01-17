#Import libraries
from pyrevit import revit, DB
from python.elements.geometry import Geometry

class ActivePlane:
    """Class responsible for getting main properties of ActivePlane"""
    def __init__(self):
        self.active_view = __revit__.ActiveUIDocument.ActiveView
        self.origin = self.active_view.Origin
        self.normal = self.active_view.ViewDirection
        self.up=self.active_view.UpDirection
        self.right = self.active_view.RightDirection
        self.scale = self.active_view.Scale
        self.crop_region_curve_loop=self.active_view.GetCropRegionShapeManager().GetCropShape()
        self.view_type=self.active_view.ViewType

#Import libraries
from python.annotations.projection import Projection

class ActivePlaneProperties(ActivePlane):
    """Class responsible for operations related to ActivePlane"""
    def __init__(self):
        ActivePlane.__init__(self)

    def get_line(self,handle = "vertical"):
        """Get vertical or horizontal line from active view
        
        :param handle: type of line, defaults to "vertical"
        :type handle: str, optional
        """
        if handle == "vertical":
            return Geometry().create_line(DB.XYZ(0,0,0),self.up)
        else:
            return Geometry().create_line(DB.XYZ(0,0,0),self.right)

    def check_if_curve_is_parallel_to_plane(self,curve,tol = 0.025):
        """Check if a given curve is parallel to active plane

        :param curve: curve to be checked
        :type curve: Autodesk.Revit.DB.Line object
        :param tol: tolerance, defaults to 0.025
        :type tol: float, optional
        :return: True if parallel, False if not
        :rtype: boolean
        """
        #Get main geometrical information from a given curve
        start_point = curve.GetEndPoint(0)
        end_point = curve.GetEndPoint(1)
        projected_start_point = Projection.project_point_to_plane(start_point)
        projected_end_point = Projection.project_point_to_plane(end_point)
        
        #Compare distances
        distance_1 = start_point.DistanceTo(end_point)
        distance_2 = projected_start_point.DistanceTo(projected_end_point)
        if abs(distance_2-distance_1) < tol:
            return True
        else:
            return False

    def get_bbox_from_active_view_crop_box(self):
        """Get coordinates of active view's crop box

        :return: bounding box 
        :rtype: Autodesk.Revit.DB.BoundingBoxXYZ
        """
        #Get coordinates from crop box curves
        points=[curve.GetEndPoint(0) for curve in self.crop_region_curve_loop[0]]
        x_list,y_list,z_list=[point[0] for point in points],[point[1] for point in points],[point[2] for point in points]
        if self.up[0]==-1 or self.right[0]==-1:
            x_max=min(x_list)
            x_min=max(x_list)
        else:
            x_max=max(x_list)
            x_min=min(x_list)
        if self.up[1]==-1 or self.right[1]==-1:
            y_max=min(y_list)
            y_min=max(y_list)
        else:
            y_max=max(y_list)
            y_min=min(y_list)
        if self.up[2]==-1 or self.right[2]==-1:
            z_max=min(z_list)
            z_min=max(z_list)
        else:
            z_max=max(z_list)
            z_min=min(z_list)
        
        #Create bounding box
        bbox = DB.BoundingBoxXYZ()
        bbox.Min = DB.XYZ(x_min,y_min,z_min)
        bbox.Max = DB.XYZ(x_max,y_max,z_max)
        return bbox
