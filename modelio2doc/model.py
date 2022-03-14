'''
Created on Mar 7, 2022

@author: Carlos Calvillo Cortes
'''

from attrs import define, Factory
import pathlib as pl
import lxml.etree as ET
import modelio2doc.general as grl
import anytree as at
import logging
from email._header_value_parser import get_attribute


@define
class ElementAttr(object):
    
    name: str = Factory(str)
    value: str = Factory(str)
    value_type: str = Factory(str)
    
    def get_value_type(self):
        '''
            Extract CDATA content type
        '''
        pass 


@define
class ModelElement(at.NodeMixin):
    
    name: str = Factory(str)
    type: str = Factory(str)
    uuid: str = Factory(str)
    owner_uuid: str = Factory(str)
    desc: str = Factory(str)
    file: pl.Path = None
    attributes: dict[str,list[ElementAttr]] = Factory(dict) # [name, ElementAttr]
    
    def load_attribute(self, name):
        pass
        


@define
class NavElement(object):
    
    name: str = Factory(str)
    type: str = Factory(str)
    type_qualifier: str = Factory(str)
    uuid: str = Factory(str)


@define
class Model(object):
    '''
    classdocs
    '''
     
    name: str = Factory(str)
    _uuid: str = Factory(str) 
    _data_path: pl.Path = None # project/data/fragments/project_name/model/
    _elements: dict[str, ModelElement] = Factory(dict) # [element_uuid, ModelElement]
    _model_tree_root: ModelElement = Factory(ModelElement)
    _current_element : ModelElement = None
    _current_path: list[NavElement] = Factory(list)
    
    
    def _str_to_nav_path(self, path_str: str):
        '''
            Returns a list of NavElement objects from the input path string.
            
            path string format example:
            
            "qualifier1.type1:name1/type2:name2/qualifier3.type3:name3"
        '''
        
        
        nav_path = []
        
        path_pieces = path_str.split("/")
        
        for piece in path_pieces:
            nav_element = NavElement()
            piece_split = piece.split(":")
            if len(piece_split) == 1:
                # If only one part, it is the name of the element
                nav_element.name = piece_split[0]
            else:
                # If two parts, first is the type and second the name
                nav_element.name = piece_split[1]
                el_type = piece_split[0]
                
                # Check if type is qualified
                el_type_split = el_type.split(".")
                if len(el_type_split) == 1:
                    # If only one part then the type is not qualified
                    nav_element.type = el_type
                else:
                    # Should be two parts, first will be the qualifier, second the type
                    nav_element.type_qualifier = el_type_split[0]
                    nav_element.type = el_type_split[1]
                
            nav_path.append(nav_element)
        
        return nav_path
                
    
    def _find_child_by_nav_element(self, node : ModelElement, nav_element : NavElement):
        
        return_value = None
        
       # print("node: ", node.name, " children: ", node.children)
        
        for child in node.children:
            if nav_element.name == child.name \
            and (nav_element.type == "" or nav_element.type == child.type) \
            and (nav_element.type_qualifier == "" or \
            nav_element.type_qualifier == child.type_qualifier):
                return_value = child
                break
        
        return return_value
        
    
    def _get_element_by_path_str(self, path_str: str):
        ''' 
            Returns a ModelElement object at the given path string.
        '''
        
        # Convert path string
        nav_path = self._str_to_nav_path(path_str)

        return self._get_element_by_path(nav_path)

    
    def _get_element_by_path(self, nav_path: list[NavElement]):
        
        return_val = None

        current_node = self._model_tree_root
        
        # Navigate Model to find element
        for nav_element in nav_path:
            current_node = self._find_child_by_nav_element(current_node, nav_element)
            return_val = current_node
            if current_node is None:
                # Element NOT found, break navigation since path is invalid
                logging.error("Provided element not found.")
                break
        
        # pre-pend current location
        if return_val is not None:
            nav_path = self._current_path + nav_path
        
        return return_val
        
    
    def set_current_path(self, path_str: str):
        
        return_val = False
        
        # Check if path is valid
        nav_path = self._str_to_nav_path(path_str)
        
        element = self._get_element_by_path(nav_path)
        if element is not None:
            self._current_path = nav_path
            return_val = True 
        
        return return_val
        
        
    def clear_current_path(self):
        
        self._current_path = []
        
        
        
    def set_current_element(self, name: str, type: str = None):
        
        nav_element = NavElement()
        
        nav_element.name = name
        
        type_split = type.split(".")
        if type_split > 1:
            nav_element.type_qualifier = type_split[1]
        nav_element.type = type_split[0]
        
        nav_path = self._current_path
        nav_path.append(nav_element)
        element = self._get_element_by_path(nav_path)
        if element is not None:       
            self._current_element = element
        else:
            logging.debug("Element not found.")
    
    def test(self):
        w = at.Walker()
        print(w.walk(self._model_tree_root, self._model_tree_root))
        
        
        
            
    def _find_childs(self,parent_uuid):
        
        #at_least_one_child = False
        for element in self._elements.values():
            if element.owner_uuid == parent_uuid:
                # Set parent
                self._elements[element.uuid].parent = self._elements[parent_uuid]
                self._find_childs(element.uuid)
        
        #return at_least_one_child
                
    
    def _build_model_tree(self):
        
        # Set Root (project element)
        project_uuid = self.get_project_uuid()
        self._elements[project_uuid].parent = None
        
        self._model_tree_root = self._elements[project_uuid]
        
        
        self._find_childs(project_uuid)
        
    def print_tree(self):
        print(at.RenderTree(self._model_tree_root))
                

    
    def _load_standard_elements(self, element_type = None):
        '''
            Load standard _elements to model object.
            
            Load standard _elements matching the 'element_type'.
        '''
        
        if element_type is None:
            element_type = "standard"
        
        if grl.folder_exists(self._data_path):
            for folder in self._data_path.glob(element_type+'.*'):
                print(folder.name)
                splitted_str = str(folder.name).split(".")
                for exml_file in folder.glob('*.exml'):
                    # Parse xml
                    el_tree = ET.parse(str(exml_file))
                    el_root = el_tree.getroot()
                    
                    element_obj = ModelElement()
                    
                    # Get element file
                    element_obj.file = exml_file
                    
                    # Get identification data
                    element = el_root.find("OBJECT/ID")
                    if element is not None:
                        element_obj.name = element.get("name")
                        el_type = None
                        if element.get("mc") is not None:
                            splitted_str = element.get("mc").split(".")
                            if len(splitted_str) > 1:
                                el_type = splitted_str[1]
                        
                        if el_type is not None: 
                            element_obj.type = el_type
                        
                        if element.get("uid") is not None:
                            element_obj.uuid = element.get("uid")
                    
                    # Get owner
                    element = el_root.find("OBJECT/PID")
                    if element is not None:
                        if element.get("uid") is not None:
                            element_obj.owner_uuid = element.get("uid")
                    
                    # Get attributes
                    for attribute in el_root.findall("OBJECT/ATTRIBUTES/ATT"):
                        
                        # Only PreviewData for now
                        if attribute.get("name") == "PreviewData":
                            attribute_obj = ElementAttr()
                            attribute_obj.name = attribute.get("name")
                            attribute_obj.value = attribute.text
                            
                            # Append attribute to element
                            element_obj.attributes.update({attribute_obj.name:attribute_obj})
                    
                    # Get description data
                    desc = el_root.xpath("//OBJECT/DEPENDENCIES/COMP[@relation='Descriptor']/OBJECT/ID[@mc='Infrastructure.Note']")
                    if desc:
                        desc = desc[0].xpath("../ATTRIBUTES/ATT[@name='Content']/text()")
                        if desc is not None:
                            element_obj.desc = ''.join(desc)
                    
                    self._elements.update({element_obj.uuid:element_obj})
                    print("    ",element_obj.name)
    
    
    def get_project_uuid(self, default=None):
        return_val = default
        
        for element in self._elements.values():
            if element.type == "Project": #Access element object
                return_val = element.uuid
                break
        
        return return_val
    
        
    def _load_project_uuid(self):
        '''
        '''
        self._uuid = self.get_project_uuid()

            
    def _get_uuid(self, owner_type, owner_name, element_type, element_name):
        
       pass
   
    def get_attribute(self, attr_name : str, path_str: str = None):
        
        return_val = None
        
        if path_str is not None:
            element = self._get_element_by_path_str(path_str)
        else:
            element = self._current_element
            
        if element is not None:
            uuid = element.uuid
            return_val = self._elements[uuid].attributes[attr_name]
        
        return return_val
   
    def load(self, project_data_path):
        
        self._data_path = grl.string_to_path(str(project_data_path))
        self._load_standard_elements()
        self._load_project_uuid()
        self._build_model_tree()
            
