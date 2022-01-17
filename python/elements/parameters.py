from pyrevit import DB

class Parameters:


    @staticmethod
    def get_params(el, built_in=False):
        """Gets all parameter values for a Revit element
        
        :param el: Revit Element 
        :type el: Any Revit.DB element (ex: Revit.DB.Floor or Revit.DB.Wall)
        :param built_in: Flag whether to only include BuiltIn parameters 
        :type built_in: Boolean
        :return: Analytical model parameter values (raises exception if cannot have an analytical model)
        :rtype: dict
        """

        params = {}
        for p in el.Parameters:
            #Skip built in parameters
            if built_in and str(p.Definition.BuiltInParameter) == "INVALID":	continue

            #Get parameter name and value
            name = str(p.Definition.Name)
            val = p.AsValueString()
            
            if val == None: val = ""

            #Try decoding unicode strings
            try:
                val = val.decode('ascii')
            except UnicodeDecodeError as e:
                val = ""

            params[name] = val

        #Add additional params
        if hasattr(el, "SpanDirectionAngle"): params["SpanDirectionAngle"] = el.SpanDirectionAngle
        return params

    @staticmethod
    def get_analytical_params(el):
        """Gets all analytical model parameters for a Revit Element
        
        :param el: Revit Element 
        :type el: Any Revit.DB element (ex: Revit.DB.Floor or Revit.DB.Wall)
        :return: Analytical model parameter values (raises exception if cannot have an analytical model)
        :rtype: dict
        """

        assert el.CanHaveAnalyticalModel(), "Element {} cannot have analytical model".format(el)

        if el.GetAnalyticalModel() is None: return {}
        a = el.GetAnalyticalModel()
        return self.get_params(a)
