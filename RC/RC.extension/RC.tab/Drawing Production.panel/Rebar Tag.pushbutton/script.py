#Import libraries
import sys
from pyrevit import revit, DB
from pyrevit.forms import ProgressBar,SelectFromList
from pyrevit import script
from pyrevit.userconfig import user_config
from os.path import abspath,normpath,join
from os import pardir
from rpw.ui.forms import Alert

#Get root directory
root_directories = user_config.get_ext_root_dirs()
for directory in root_directories:
    path = normpath(abspath(normpath(join(directory,  pardir))))
    sys.path.append(path)

#Import PyGirls' classes
from python.annotations.activeplane import ActivePlane
from python.annotations.projection import Projection
from python.annotations.curveset import CurveList
from python.elements.rebar import RebarSet,RebarSetList
from python.annotations.tags import Tag
from python.elements.geometry import Geometry,Vector
from python.annotations.activeplane import ActivePlaneProperties
from python.elements.collector import ElementCollector,FamilyCollector
from python.settings import Settings


__title__ = 'Rebar Tag'
__author__ = 'PyGirls'
__doc__ = 'Annotates all rebars visible in active view'\
#TODO: link do strony na gitlabie

#Get project-specific information
doc = revit.doc
settings = Settings()
active_plane = ActivePlane()
view_normal = active_plane.normal
scale = active_plane.scale
view_type = active_plane.view_type
collector = ElementCollector()


#Define distance between the tags
dist = 0.025*scale

#Set up the progress bar
progresbar = ProgressBar(title = "Rebar annotation progress bar")

#Check if the code is being run on appropriate view
assert ("DrawingSheet" not in view_type.ToString() and "ThreeD" not in view_type.ToString()),\
Alert('No active view selected. Please activate a plan view or a section view to be annotated.', exit = True)

#Check if the view is not rotated
# assert active_plane.active_view.LookupParameter("Rotation on Sheet").AsValueString()=="None",\
# Alert('Selected active view is rotated. Please select a plan view or a section view that is not rotated.', exit = True)

#pulling tag types from settings
tag_type_left_str = settings.get("drawing","drawing_multi_tag_left")
tag_type_right_str = settings.get("drawing","drawing_multi_tag_right")
single_tag_left_str = settings.get("drawing","drawing_tag_left")
single_tag_right_str = settings.get("drawing","drawing_tag_right")

#pull family name and type name from selected tags
single_tag_family_right_str = single_tag_right_str[0:single_tag_right_str.index(" // ")]
single_tag_type_right_str = single_tag_right_str[single_tag_right_str.index(" // ")+4:]
single_tag_family_left_str = single_tag_left_str[0:single_tag_left_str.index(" // ")]
single_tag_type_left_str = single_tag_left_str[single_tag_left_str.index(" // ")+4:]

#Select given multirebar tags
rebar_tags = collector.get_elements("rebar_multitags")
for rebar_tag in rebar_tags:
    type_name = rebar_tag.LookupParameter("Type Name").AsString()
    if type_name == tag_type_left_str:
        tag_type_left = rebar_tag
    if type_name == tag_type_right_str:
        tag_type_right = rebar_tag
#Select given single tags
single_rebar_tags = collector.collect_category("single_rebar_tags_category")
for single_rebar_tag in single_rebar_tags:
    type_name = single_rebar_tag.LookupParameter("Type Name").AsString()
    family_name = single_rebar_tag.LookupParameter("Family Name").AsString()
    if type_name == single_tag_type_left_str and family_name == single_tag_family_left_str:
        single_tag_type_left = single_rebar_tag
    if type_name == single_tag_type_right_str and family_name == single_tag_family_right_str:
        single_tag_type_right = single_rebar_tag
#Check if tag types are correctly defined in settings
assert (tag_type_left and tag_type_right), Alert('Multirebar tag types not defined. Go to settings.', exit = True)
assert (single_tag_type_left and single_tag_type_right), Alert('Single tag types not defined. Go to settings.', exit = True)

#Get main geometrical information from the active view
active_plane_properties = ActivePlaneProperties()
crop_box = active_plane_properties.get_bbox_from_active_view_crop_box()
ver_line = active_plane_properties.get_line()
hor_line = active_plane_properties.get_line("horizontal")
ver_vector = Vector().createvector(ver_line).Normalize()
hor_vector = Vector().createvector(hor_line).Normalize()

#Collecting rebars
rebars_initial = collector.collect_rebars_for_tagging()
ver_rebars = []
hor_rebars = []
single_hor_rebars = []
single_ver_rebars = []
with progresbar:
    progress = 0
    #Division to vertical/horizontal groups, neglecting non-annotatable rebars
    for i,rebar in enumerate(rebars_initial):
        if not doc.ActiveView.GetElementOverrides(rebar.Id).Halftone:
            #Progressbar -progress from 0% to 10%
            progresbar.update_progress(progress, 100)
            progress = (i * 10) / (len(rebars_initial)-0.99) #0.99 to avoid dividing by 0

            #Get main geometrical information from rebar
            rebar = RebarSet(rebar)
            curve = rebar.get_curve_for_first_visible_bar()
            normal = rebar.get_normal()

            #Check if rebar is annotatable by multirebar tag
            if not "RebarInSystem" in str(rebar.rebar_type) and curve != None:
                vector = Vector().createvector(curve)
                if rebar.layout_rule.ToString() != "Single":
                    normal = rebar.get_normal()
                    if not Vector().if_perpendicular(normal,view_normal):
                        continue
                if Vector().if_perpendicular(vector,hor_vector): ver_rebars.append(rebar)
                if Vector().if_perpendicular(vector,ver_vector): hor_rebars.append(rebar)


    #Check if the rebars in view are ok
    assert (ver_rebars != [] or hor_rebars != []), \
        Alert('No rebars selected. Please bear in mind that the script does not annotate non-orthogonal bars, path and area reinforcement, bars perpendicular to the view.', exit = True)

    #User input: 2 sides / 4 sides
    side_settings = SelectFromList.show(
        ["tags on 2 sides","tags on 4 sides"],
        title = "How do you want the tags to be placed?",
        checked_only = True
        )
    #Progressbar - progress from 10% to 15%
    progresbar.update_progress(15, 100)
    #Upper right point - reference point for placing tags
    reference_point = crop_box.Max.Add(active_plane.up.Multiply(dist)).Add(active_plane.right.Multiply(dist))
    if side_settings == "tags on 4 sides":
        #Lower left point - reference point for placing other tags
        reference_point_2 = crop_box.Min.Add(active_plane.up.Multiply(-dist)).Add(active_plane.right.Multiply(-dist))

    rebar_list = [hor_rebars,ver_rebars]
    vector_list = [hor_vector,ver_vector]
    tag_line_vector_list = reversed(vector_list)
    #Progressbar -progress from 15% to 20%
    progress = 20
    for rebar_group,vector,tag_line_vector in zip(rebar_list,vector_list,tag_line_vector_list):
        progresbar.update_progress(progress, 100)
        #Sort rebars
        sorting_vector = active_plane.up if vector == hor_vector else active_plane.right
        rebar_group = RebarSetList(rebar_group).sort_rebarset_list_by_direction(sorting_vector)
        
        #Display one bar per set
        RebarSetList(rebar_group).display_one_bar_per_set()

        #Progressbar -progress from 20% to 40% (horizontal), from 60% to 80% (vertical)
        progress = progress+20
        progresbar.update_progress(progress, 100)

        orientation = "horizontal" if vector == hor_vector else "vertical"

        if side_settings == "tags on 2 sides":
            #Identify location for tags
            tag_points = Tag.get_tag_points(rebar_group,vector,reference_point,dist)

            #Progressbar - progress from 40% to 50% (horizontal), from 80% to 90% (vertical)
            progress = progress+10
            progresbar.update_progress(progress, 100)
            #Annotate rebars
            Tag(tag_line_vector, tag_type_right,single_tag_type_right).create_tags(rebar_group,tag_points,orientation)

            #Progressbar - progress from 50% to 60% (horizontal), from 90% to 100% (vertical)
            progress = progress+10
            progresbar.update_progress(progress, 100)

        if side_settings == "tags on 4 sides":
            #Divide horizontal bars into two groups - upper, lower and vertical bars into left and right groups
            for i,bar in enumerate(RebarSetList(rebar_group).cut_rebar_set_list()):
                #Identify tag type and ref point for divided rebars
                tag_type = tag_type_left if i%2 == 0 else tag_type_right
                ref_point = reference_point_2 if i%2 == 0 else reference_point
                single_tag_type = single_tag_type_left if i%2 == 0 else single_tag_type_right
                #Identify location for tags
                tag_points = Tag.get_tag_points(bar,vector,ref_point,dist)
                #Progressbar - progress from 40% to 45%, 50% to 55% (horizontal), 80% to 85%, 90% to 95% (vertical)
                progress = progress+5
                progresbar.update_progress(progress, 100)

                #Annotate rebars
                Tag(tag_line_vector, tag_type,single_tag_type).create_tags(bar,tag_points,orientation)

                #Progressbar - progress from 45% to 50%, 55% to 60% (horizontal), 85% to 90%, 95% to 100% (vertical)
                progress = progress+5
                progresbar.update_progress(progress, 100)
