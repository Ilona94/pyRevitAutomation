from python.annotations.projection import Projection
from pyrevit import revit, DB
from python.annotations.curveset import CurveList
from python.annotations.activeplane import ActivePlane
from python.annotations.activeplane import ActivePlaneProperties
doc=revit.doc

class RebarSet:

    def __init__(self, rebarset):
        revitUI = __revit__.ActiveUIDocument
        revitDoc = __revit__.ActiveUIDocument.Document
        revitActiveViewId = __revit__.ActiveUIDocument.ActiveView.Id
        self.set = rebarset
        self.id = rebarset.Id
        self.quantity = self.set.Quantity
        self.layout_rule = self.set.LayoutRule
        self.rebar_type = self.set.GetType

    def get_normal(self):
        """Returns normal direction to the bar

        :return: normal direction
        :rtype: XYZ Revit object
        """
        return self.set.GetShapeDrivenAccessor().Normal

    def show_defined_bar(self,i):
        """Returns rebar set with visible defined bar

        :param i: index of visible rebar
        :type i: integer 
        :return: rebar set with visible defined bar
        :rtype: rebar set
        """
        if self.layout_rule == DB.Structure.RebarLayoutRule.Single:
            pass
        else:
            for j in range(0,self.quantity):
                try:
                    if j == i:
                        with revit.Transaction("show bar"):
                            self.set.SetBarHiddenStatus(doc.ActiveView,j,False)
                    else:
                        with revit.Transaction("hide bar"):
                            self.set.SetBarHiddenStatus(doc.ActiveView,j,True)
                except:
                    continue
        return self.set

    def show_middle_bar(self):
        """Returns rebar set with visible middle bar

        :return: rebar set with visible middle bar
        :rtype: rebar set
        """
        return self.show_defined_bar(self.get_middle_bar_index())

    def get_curve_and_show_middle_bar(self):
        """Set visible middle bar in rebar set and return projected longest in plane centerline curve for middle bar

        :return: projected longest in plane centerline curve for middle bar
        :rtype: Revit line object
        """
        self.show_middle_bar()
        return Projection.project_curve_to_plane(self.get_curve_for_defined_bar(self.get_middle_bar_index()))

    def get_middle_bar_index(self):
        """Get middle bar index from rebarset

        :return: middle bar index
        :rtype: integer
        """
        return round(float(self.quantity) / 2) - 1

    def get_curve_and_show_defined_bar(self,i):
        """Set visible defined bar in rebar set and return projected longest in plane centerline curve for given bar
        
        :param i: index of visible rebar
        :type i: integer
        :return: projected longest in plane centerline curve for first visible bar
        :rtype: Revit line object
        """
        self.show_defined_bar(i)
        return Projection.project_curve_to_plane(self.get_curve_for_defined_bar(i))

    def visible_bars(self):
        """Returns a list of indexes of visible bars from rebar set

        :return: list of indexes of visible bars from rebar set
        :rtype: list
        """
        visible_bars = [i for i in range(0,self.quantity) if not self.set.IsBarHidden(doc.ActiveView,i)]
        return visible_bars

    def get_curve_for_defined_bar(self,i):
        """Returns longest in plane centerline curve for defined bar

        :param i: index of rebar
        :type i: integer
        :return: longest in plane centerline curve for defined bar
        :rtype: Revit line object
        """
        mpo = DB.Structure.MultiplanarOption.IncludeAllMultiplanarCurves
        rebar_shp = self.set.GetShapeDrivenAccessor()
        centerline_curves = []
        centerline_curves_length = []
        if self.layout_rule == DB.Structure.RebarLayoutRule.Single:
            for c in self.set.GetCenterlineCurves(0,0,0,mpo,0):
                if ActivePlaneProperties().check_if_curve_is_parallel_to_plane(c) == True and "Line" in c.ToString():
                    centerline_curves.append(c)
                    centerline_curves_length.append(c.Length)
        else:
            pos_transform = rebar_shp.GetBarPositionTransform(i)
            for c in self.set.GetCenterlineCurves(0,0,0,mpo,0):
                if ActivePlaneProperties().check_if_curve_is_parallel_to_plane(c) == True and "Line" in c.ToString():
                    centerline_curves.append(c.CreateTransformed(pos_transform))
                    centerline_curves_length.append(c.Length)          
        if centerline_curves_length == []:
            return None
        else:
            index_of_longest_bar = centerline_curves_length.index(max(centerline_curves_length))
            longest = centerline_curves[index_of_longest_bar]
            return longest

    def get_curve_for_first_visible_bar(self):
        """Returns longest in plane centerline curve for first visible bar

        :return: longest in plane centerline curve for first visible bar
        :rtype: Revit line object
        """
        first_visible_bar = self.visible_bars()[0]
        return self.get_curve_for_defined_bar(first_visible_bar)

class RebarSetList():

    def __init__(self, rebarset_list):
        self.set_list=rebarset_list

    def sort_rebarset_list_by_direction(self,direction):
        """Sorts rebar set by direction

        :param direction: vector that rebar set needs to be sorted by
        :type direction: Revit XYZ vector object
        :return: sorted rebars
        :rtype: list of RebarSet class objects
        """
        mid_point_list = [[],[],[]]
        for rebarset in self.set_list:
            curve = rebarset.get_curve_for_first_visible_bar()
            start_point = curve.GetEndPoint(0)
            end_point = curve.GetEndPoint(1)
            for i, sublist in enumerate(mid_point_list):
                sublist.append((start_point[i]+end_point[i])/2)
        list_of_pairs = [zip(mid_point,self.set_list) for mid_point in mid_point_list]
        for i,pair in enumerate(list_of_pairs):
            if round(direction[i]) == 1:
                sorted_pairs = sorted(pair)
            elif round(direction[i]) == -1:
                sorted_pairs = sorted(pair,reverse=True)
        rebars = [j for i,j in sorted_pairs]
        return rebars

    def cut_rebar_set_list(self):
        """Cut rebarset into two lists

        :return: two lists of rebars after cutting
        :rtype: list of two lists with RebarSet class objects
        """
        if self.set_list != []:
            rebars_1 = self.set_list[0:len(self.set_list)/2]
            rebars_2 = self.set_list[len(self.set_list)/2:]
            return [rebars_1,rebars_2]
        else:
            return [[],[]]

    def display_one_bar_per_set(self):
        """Method used for showing such a bar per set so that no bar intersects with any other

        """
        #Firstly, do show middle for all
        projected_curves = [rebar.get_curve_and_show_middle_bar() for rebar in self.set_list]
        #numbers is a list of indexes of displayed bar for all rebar sets
        numbers=[rebar.get_middle_bar_index() for rebar in self.set_list]
        i=0
        x=0
        proceed_to_the_next_bar=False
        toggle = 1
        while_loop_control=0
        #Then, see if bars intersect and try showing different bars from set
        while i<len(self.set_list):
            while_loop_control = while_loop_control+1
            rebarset = self.set_list[i]
            curves_to_be_compared = projected_curves
            #While loop control set up to avoid crushing Revit
            if while_loop_control == 200:
                break
            if CurveList(curves_to_be_compared).intersects_with(i):
                #If bar intersects with something, try showing next one in the following order - 5,4,6,3,7,2,8,2,etc.
                x=x+1
                numbers[i] = numbers[i]+x*toggle
                toggle = toggle*(-1)
                #Check if rebar 
                if numbers[i]>=0 and numbers[i]<=rebarset.quantity-1:
                    projected_curves[i]=rebarset.get_curve_and_show_defined_bar(int(numbers[i]))
                else:
                    projected_curves[i]=rebarset.get_curve_and_show_middle_bar()
                    proceed_to_the_next_bar = True
            else:
                proceed_to_the_next_bar = True
            if proceed_to_the_next_bar == True:
                i=i+1
                x=0
                toggle = 1
