from pyrevit import DB

class ElementCollector:
    """A high-level wrapper around the Revit.DB.FilteredElementCollector class"""

    MAPPING = {
        'beams':    [DB.BuiltInCategory.OST_BeamAnalytical],
        'columns':  [DB.BuiltInCategory.OST_StructuralColumns],
        'floors':   [DB.Floor],
        'walls':    [DB.Wall],
        'rebars':   [DB.Structure.Rebar, DB.Structure.AreaReinforcement, DB.Structure.PathReinforcement],
        'tags':     [DB.IndependentTag],
        'load_combinations': [DB.Structure.LoadCombination],
        'load_cases': [DB.Structure.LoadCase],
        'analytical_beams': [DB.BuiltInCategory.OST_BeamAnalytical],
        'analytical_columns': [DB.BuiltInCategory.OST_ColumnAnalytical],
        'analytical_floors': [DB.BuiltInCategory.OST_FloorAnalytical],
        'analytical_walls': [DB.BuiltInCategory.OST_WallAnalytical],
        'analytical_model': [DB.BuiltInCategory.OST_BeamAnalytical, DB.BuiltInCategory.OST_ColumnAnalytical, DB.BuiltInCategory.OST_FloorAnalytical, DB.BuiltInCategory.OST_WallAnalytical],
        'rebar_multitags': [DB.MultiReferenceAnnotationType],
        'single_rebar_tags_category': [DB.BuiltInCategory.OST_RebarTags]
    }

    def __init__(self):
        self.revitUI = __revit__.ActiveUIDocument
        self.revitDoc = __revit__.ActiveUIDocument.Document
        self.view = __revit__.ActiveUIDocument.ActiveView

        if self.view is None:   self.view_id = None
        else:                   self.view_id = __revit__.ActiveUIDocument.ActiveView.Id

    ### Collectors ###
    def collect(self, view_id=None):
        if view_id is None:     return DB.FilteredElementCollector(self.revitDoc)
        else:                   return DB.FilteredElementCollector(self.revitDoc, view_id)
    
    def collect_class(self, class_name, view_id=None):
        return self.collect(view_id).OfClass(class_name).ToElements()

    def collect_classes(self, class_list, view_id=None):
        result = []
        for c in class_list:
            result += list(self.collect_class(c, view_id))
        return result

    def collect_category(self, category, view_id=None, exclude_type=False):
        category=self.MAPPING[category][0]
        collector = self.collect(view_id).OfCategory(category)
        if exclude_type: 
            return collector.WhereElementIsNotElementType().ToElements()
        return collector.ToElements()

    def collect_categories(self, category_list, view_id=None):
        result = []
        for c in category_list:
            result += list(self.collect_category(c, view_id))
        return result


    def get_elements(self, el_type, handle="doc"):
        """Get elements of a particular element type
        
        :param el_type: Element type (options are: {} )
        :type el_type: str
        :param handle: Collect from "view" (ActiveView) or "doc" (Document), defaults to "doc"
        :type handle: str, optional
        :return: List of elements matching element type
        :rtype: list
        """.format(self.MAPPING.keys())

        assert el_type in self.MAPPING, "el_type: {} is not a valid option. Valid options are: {}".format(el_type, self.MAPPING.keys())
        assert handle.lower() == "doc" or handle.lower() == "view"
        if handle == "view": view = self.view_id
        else:                view = None
            
        query = self.MAPPING[el_type]
        result = []
        for item in query:
            if type(item) == DB.BuiltInCategory:    result += self.collect_category(item, view)
            else:                                   result += self.collect_class(item, view)
        
        return result

    
    def collect_area_reinforcements(self):
        area_reinforcements = DB.FilteredElementCollector(self.revitDoc, self.view_id).OfClass(DB.Structure.AreaReinforcement).ToElements()

        return area_reinforcements
    
    def collect_path_reinforcements(self):
        path_reinforcements = DB.FilteredElementCollector(self.revitDoc, self.view_id).OfClass(DB.Structure.PathReinforcement).ToElements()

        return path_reinforcements
    
    def path_reinforcement_exists(self):
        paths = self.collect_path_reinforcements()
        if len(paths) > 0:
            return True
        else:
            return False

    def collect_rebars_for_tagging(self):
        rebars_initial=DB.FilteredElementCollector(self.revitDoc, self.view_id).OfCategory(DB.BuiltInCategory.OST_Rebar).WhereElementIsNotElementType().ToElements()
        return rebars_initial
    

class FamilyCollector:
    """A high-level wrapper around the Revit.DB.FilteredElementCollector class"""

    def __init__(self):
        self.revitUI = __revit__.ActiveUIDocument
        self.revitDoc = __revit__.ActiveUIDocument.Document

    def collect_families(self):
        return DB.FilteredElementCollector(self.revitDoc).OfClass(DB.Family).ToElements()