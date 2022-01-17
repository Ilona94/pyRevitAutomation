from pyrevit import script
import json
import os


class Settings:
    """Class for managing User Config Settings
    """
    DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
    
    def __init__(self, file_path=None):

        if not file_path: file_path = self.DEFAULT_PATH
        
        #read in default settings file
        with open(file_path) as f:
            self.defaults = json.load(f)

        self.initialize()
    
    def get(self, section_name, name):
        """Gets settings parameter from a section
        
        :param section_name: Name of the section that contains the parameter
        :type section_name: str
        :param name: Parameter name
        :type name: str
        :return: Parameter value
        :rtype: based on parameter value type
        """
        try: 
            section = script.get_config(section_name)
            return getattr(section,name)
        except Exception as e:
            print(e)
            return

    def set_param(self, section_name, name, value):
        """Sets a settings parameter in a section
        
        :param section_name: Name of the section that contains the parameter
        :type section_name: str
        :param name: Parameter name
        :type name: str
        :param value: Parameter value
        :type value: based on parameter value type
        """
        section = script.get_config(section_name)
        setattr(section, name, value)
        script.save_config()


    def initialize(self):
        """ Initializes all parameters with a default value, 
            but only if the parameter has not been set already
        """
        assert self.defaults is not None and type(self.defaults) == dict, "Default settings need to be set first"
        for section_name, params in self.defaults.items():
            
            for param, value in params.items():
                if self.get(section_name, param) is None:
                    self.set_param(section_name, param, value)
                    

    def reset(self):
        """Resets all settings to default values
        
        :return: True if successful
        :rtype: Boolean
        """
        for section_name, params in self.defaults.items():
            for param, value in params.items():
                self.set_param(section_name, param, value)
        return True

    def as_dict(self):
        """Returns the settings parameters as a dictionary
        
        :return: Dictionary of parameter settings
        :rtype: dict
        """
        result = {}
        for section_name, params in self.defaults.items():
            result[section_name] = {}
            for param, value in params.items():
                result[section_name][param] = self.get(section_name, param)
        
        return result