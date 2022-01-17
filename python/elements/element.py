from .geometry import Geometry
from .parameters import Parameters

class Element:
    """Base class for all Revit Element Types
    """
    def __init__(self, revit_el):
        self.el = revit_el
        self.id = revit_el.Id.ToString()
        self.category = revit_el.Category.Name
        self.g = Geometry()
        self.p = Parameters()


    def parameters(self):
        """Returns Revit elements' parameters
        
        :return: Parameter key value pairs
        :rtype: dict
        """
        return self.p.get_params(self.el)

    def geometry(self):
        """Returns Revit elements' geometry
        
        :return: List of Revit geometry elements
        :rtype: list
        """
        return self.g.get_geometry(self.el)

    def as_dict(self):
        """Returns element information as a dictionary
        
        :return: Element information with keys: 'id', 'parameters'
        :rtype: dict
        """
        return {
                'id': self.id, 
                'category': self.category,
                'parameters': self.parameters()
                }