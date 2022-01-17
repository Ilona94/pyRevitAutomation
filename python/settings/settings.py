from xml.etree.ElementTree import ElementTree
import xml.etree.ElementTree as ET
import os 
from python.elements.collector import ElementCollector
ir = ElementCollector()
floors = ir.floors()
floors_exist = ir.floors_exist()
walls = ir.walls()
walls_exist = ir.walls_exist()
from python.designdata import DesignData
dd = DesignData()

class Parameter:
    """
    A simple class that stores and validates parameter values
    """
    def __init__(self, name, param_type, default=None):
        self.name = name
        self.type = param_type
        self.default = default
    
    def set_value(self, value, with_type=False):
        """
        Sets parameter value. If with_type is True, then it tries to convert the
        input value type to the correct type
        """
        if with_type: 
            try:
                self.value = self.type(value)
            except Exception as e:
                return e
        else:
            self.value = value
            self.validate()

    def is_valid(self):
        """
        Return True if parameter value is valid
        """
        try:
            self.validate()
            return True
        except AssertionError as e:
            return False

    def validate(self):
        """
        Validates that parameter value is of the correct type
        """ 
        assert hasattr(self, 'value') or self.default, "Parameter {} has not been set with a value".format(self.name)
        assert type(self.value) == self.type, "Parameter {} has invalid type (expected {} but got {})".format(self.name, self.type, type(self.value))

        return True



class Settings:
    """
    A simple class that stores dictionary for global/floors/walls/beams etc.
    """
    PATH_XML = os.path.join(os.path.dirname(os.path.abspath(__file__)),'Settings.xml')
    PARAMS = [
            Parameter('upp_dir', int, 0),
            Parameter('low_dir', int, 0),
            Parameter('cover_top', int, 25),
            Parameter('cover_bottom', int, 25),
            Parameter('principle_top', int, 12),
            Parameter('cross_top', int, 12),
            Parameter('principle_bottom', int, 12),
            Parameter('cross_bottom', int, 12),
            Parameter('ro_v', float, 0.2),
            Parameter('ro_v2', float, 1.5),
            Parameter('CCClass', str, 'CC1'),
            Parameter('slider_w1', float, 3.0),
            Parameter('slider_w2', float, 2.0),
            Parameter('slider_w3', float, 1.0),
            Parameter('slider_w4', float, 1.0),
            Parameter('slider_ml', float, 0.6),
            Parameter('checking_tolerance', int, 51)
    ]

    def __init__(self, pathxml=None):
        self.dct = {}


        ET.register_namespace('',"http://schemas.microsoft.com/winfx/2006/xaml/presentation")
        ET.register_namespace('x',"http://schemas.microsoft.com/winfx/2006/xaml")

        if pathxml is None:     self.root = self.read_xml(self.PATH_XML)
        else:                   self.root = self.read_xml(pathxml)
        self.schema = "{http://schemas.microsoft.com/winfx/2006/xaml/presentation}"
        self.set_params()
        #self.groups = self.get_floor_groups()

    def read_xml(self, pathxml):
        assert os.path.exists(pathxml), "Settings xml does not exist"
        self.et = ElementTree()
        return self.et.parse(pathxml)
    
    def write_xml(self, filepath):
        self.et.write(filepath, xml_declaration = True, encoding = 'utf-8' , method = 'xml')

    def collect_dict(self):
        
        if floors_exist == True:
            self.get_floor_dict()
        if walls_exist == True:
            self.get_wall_dict()
        
        self.get_dict()
        return self.dct

    def add(self, name, settings):
        self.dct[name] = settings

    def get_floor_dict(self):
        self.dct["floors"] = {}

        for i in floors:
            sofgroup = i.LookupParameter('SOFiSTiK_Group').AsValueString()
            #print(sofgroup)
            self.dct["floors"][sofgroup] = {}
            dic = dd.get_data('floors',"A")
            #print(dic)
            
            for key in dic:
                valu = i.LookupParameter(str(key)).AsValueString()
                #print(valu)
                self.dct["floors"][sofgroup][key] = valu
        
        #print(self.dct)
        return self.dct    

    def get_wall_dict(self):
        self.dct["walls"] = {}

        

        for i in walls:
            sofgroup = i.LookupParameter('SOFiSTiK_Group').AsValueString()
            self.dct["walls"][sofgroup] = {}
            dic = dd.get_data("walls", "default")

            for key in dic:
                valu =  i.LookupParameter(str(key)).AsValueString()
                #print(valu)
                self.dct["walls"][sofgroup][key] = valu

        return self.dct
            

        
    def get_attr(self, key, val):
        """
        Searches data tree for element with particular attribute key and value
        """
        for el in self.root.iter():
            #print(el.attrib)
            if key not in el.attrib: continue 
            if el.attrib[key] == val: return el

    def get_param(self, name):
        """
        Gets internal parameter with provided name
        """
        for param in self.PARAMS:
            if param.name.lower() == name.lower(): return param


    def get_element_value(self, el):
        """
        Returns value of element based on element type
        """
        if 'TextBox' in el.tag: return el.attrib['Text']
        if 'Slider' in el.tag: return el.attrib['Value']
        

        for child in el:
            if 'RadioButton' in child.tag and child.attrib['IsChecked'] == 'True': return child.attrib['Name']

    def set_el_attr(self, el, value):

        if 'RadioButton' in el.tag: el.set("IsChecked", value)
        if 'TextBox' in el.tag: el.set("Text", value)


    def set_params(self):
        """
        Sets parameter values with values read from settings file
        """
        for param in self.PARAMS:
            #Get element with parameter name and skip if not found
            el = self.get_attr("Name", param.name)
            if el == None: continue

            #Get value from element 
            value = self.get_element_value(el)

            #Set settings parameter value
            param.set_value(value, with_type=True)

    def get_dict(self):
        """
        Returns dictionary of parameter settings
        """
        self.dct["global"] = {}
        #Return dictionary of parameter name-value pairs
        for param in self.PARAMS:
            try:
                self.dct["global"][param.name] = param.value
            except AttributeError as e:
                self.dct["global"][param.name] = param.default
                pass
        return self.dct
        
    def set_textvalues(self,name):
            
        for name, value in self.get_dict().items():
            el = self.get_attr('Name', name)
            if el == None: continue
            if 'Text' not in el.attrib: continue 
            
            #self.set_el_attr(el, eval('self.' + name + '.Text'))
            #Sets element text value from Window
            el.set('Text', eval('self.' + name + '.Text'))
            #print(el.attrib)
                





