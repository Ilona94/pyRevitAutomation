from python.annotations.activeplane import ActivePlane
from python.elements.geometry import Geometry
from pyrevit import revit, DB
from System.Collections.Generic import List # import List type from .NET Collection assembly
import math
doc=revit.doc


class Tag:
    """Class responsible for generating Revit Tags within Revit transaction"""

    #doc = __revit__.ActiveUIDocument.Document

    def __init__(self, tag_vector, tag_type, single_tag_type):
        self.tag_vector = tag_vector
        self.tag_type = tag_type
        self.single_tag_type = single_tag_type
        self.options = DB.MultiReferenceAnnotationOptions(self.tag_type)
        self.set_options()
        #doc = __revit__.ActiveUIDocument.Document
    def set_options(self):
        """ Set the properties of the tag style using Properties from 
        Revit.DB.MultiReferenceAnnotationOptions Class"""
        self.options.TagHasLeader = True
        self.options.DimensionPlaneNormal = ActivePlane().normal
        self.options.DimensionLineDirection = self.tag_vector

    def create_tags (self,rebars,points,orientation):
        """Print tags within active plane view in Revit

        :param rebars: list of Rebar objects from class RebarSet
        :type rebars: list 
        :param points: Coordinates of point to place the tag object
        :type points: list
        :return: list of Revit annotation object instance
        :rtype: list 
        """

        printed_tags = []
        elementIds= []

        for (rebar,point) in zip(rebars,points):
            #Imported List type from .NET's Collections, 
            #REASON Revit API require to create a List type,
            #when you are asked to pass lists/collections of objects

            elementIds=List[DB.ElementId]()  # Creates an empty List container that can hold only ElementIds.
            print rebar
            elementIds.Add(rebar.id)  # Adds ElementIds to the List 

            #additional settings for MultiRebarTag
            self.options.TagHeadPosition = point
            self.options.DimensionLineOrigin = point
            self.options.SetElementsToDimension(elementIds)
            #settings for IndependatTag
            tag_mode = DB.TagMode.TM_ADDBY_CATEGORY
            if orientation == "horizontal":
                tag_orient = DB.TagOrientation.Vertical
            else:
                tag_orient = DB.TagOrientation.Horizontal
            rebar_ref = DB.Reference(rebar.set)
            if rebar.layout_rule.ToString() == "Single":
                with revit.Transaction("print single rebar tags"):
                    # IndependantTag Class - Create method
                    # True if leader to be added
                    #try:
                    tag = DB.IndependentTag.Create(doc,doc.ActiveView.Id,rebar_ref,False,tag_mode,tag_orient,point)
                    tag.ChangeTypeId(self.single_tag_type.Id)
                    tag.HasLeader=True
                    printed_tags.append(tag)
                    #except:
                    #    continue
            else:
                with revit.Transaction("print multirebar tags"):
                    # MultiReferenceAnnotation  Class - Create method
                    try:
                        multi_tag = DB.MultiReferenceAnnotation.Create(doc,doc.ActiveView.Id,self.options)
                        printed_tags.append(multi_tag)
                        doc.GetElement(multi_tag.TagId).TagOrientation = tag_orient

                    except:
                        continue
        return printed_tags

    @staticmethod
    def get_tag_points(list_of_bars,direction,reference_point,dist):
        """Get points for best tag location

        :param list_of_bars: list of Rebar objects from class RebarSet
        :type list_of_bars: list 
        :param direction: direction of rebars
        :type direction: XYZ object (vector)
        :return: list of Revit XYZ point objects
        :rtype: list 
        """
        all_tag_coordinates = []
        #Identify the index of coordinates that will differ between the tags in one line
        for i in range(0,3):
            if int(abs(direction[i]))==1:
                coord_index=i
        tag_points=[]
        for rebar in list_of_bars:
            #Get main geometrical information from rebar
            curve = rebar.get_curve_for_first_visible_bar()
            start_coord=curve.GetEndPoint(0)[coord_index]
            end_coord=curve.GetEndPoint(1)[coord_index]
            #Divide bar into segments where a tag could be placed
            no_of_divisions = int((curve.Length/dist))
            #Analysis will start with index indication segment in the middle of the bar
            segment_index = math.ceil((float(no_of_divisions)/2)-1)
            i=1
            toggle=True
            #Go through all the segments
            while i <= no_of_divisions:
                #For each segment identify start point and end point coordinates
                range_coords=[min(start_coord,end_coord)+(segment_index/no_of_divisions)*curve.Length,min(start_coord,end_coord)+((segment_index+1)/no_of_divisions)*curve.Length]
                is_segment_obstructed=False
                #Go through all the tags to check if a given segment in obstructed
                for existing_tag_coord in all_tag_coordinates:
                    if min(range_coords)<existing_tag_coord<max(range_coords):
                        is_segment_obstructed=True
                        break
                #If analysed segment is not obstructed, place the tag in there
                if not is_segment_obstructed:
                    tag_coord = sum(range_coords)/len(range_coords)
                    break
                #Go through all the segments searching for not obstructed one, starting with the ones closer to center
                segment_index=segment_index+i if toggle else segment_index-i
                i=i+1
                toggle = not toggle
            #If no not-obstructed segment has been identified, place the tag in the middle of the bar
            try:
                tag_coord
            except:
                tag_coord = sum([start_coord,end_coord])/len([start_coord,end_coord])
            #Add created tag to the list of all tags so that it is taken into account in the next obstruction check
            all_tag_coordinates.append(tag_coord)
            if coord_index == 0:
                tag_point = DB.XYZ(tag_coord,reference_point.Y,reference_point.Z)
            elif coord_index == 1:
                tag_point = DB.XYZ(reference_point.X,tag_coord,reference_point.Z)
            elif coord_index == 2:
                tag_point = DB.XYZ(reference_point.X,reference_point.Y,tag_coord)
            tag_points.append(tag_point)
            del tag_coord
        return tag_points
