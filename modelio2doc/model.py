'''
Created on Mar 7, 2022

@author: Carlos Calvillo Cortes
'''

from attrs import define, Factory
import pathlib as pl
import lxml.etree as ET
import modelio2doc.general as grl
import anytree as at


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
    _uuid: str = Factory(str)
    owner_uuid: str = Factory(str)
    file: pl.Path = None
    attributes: dict[str,list[ElementAttr]] = Factory(dict) # [name, ElementAttr]
    
    def load_attribute(self, name):
        pass
        


@define
class NavElement(object):
    
    name: str = Factory(str)
    type: str = Factory(str)
    type_qualifier: str = Factory(str)
    _uuid: str = Factory(str)


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
    _current_path: list[NavElement] = Factory(list)
    
    
    def _str_to_nav_path(self, path_str: str, ignore_current_path = False):
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
                # SHould be two parts, first is the type and second the name
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
            
        if ignore_current_path is False:
            # Pre-pend current path
            nav_path = self._current_path + nav_path
        
        return nav_path
                
    
    def _find_child_by_nav_element(self, node : ModelElement, nav_element : NavElement):
        
        return_value = None
        
       # print("node: ", node.name, " children: ", node.children)
        
        for child in node.children:
            if child.name == nav_element.name and child.type == nav_element.type:
                return_value = child
                break
        
        return return_value
        
    
    def _get_element_by_path_str(self, path_str: str, ignore_current_path: bool = False):
        ''' 
            Returns a ModelElement object at the given path string.
        '''
        
        return_val = None
        
        # Convert path string
        nav_path = self._str_to_nav_path(path_str, ignore_current_path)
        
        
        current_node = self._model_tree_root
        
        # Navigate Model to find element
        for nav_element in nav_path:
            current_node = self._find_child_by_nav_element(current_node, nav_element)
            return_val = current_node
            if current_node is None:
                # Element NOT found, break navigation since path is invalid
                break
        
        return return_val
    
    def _set_current_path(self, path_str: str):
        
        return_val = False
        
        # Check if path is valid
        element = self._get_element_by_path_str(path_str)
        
    
    
    def test(self):
        w = at.Walker()
        print(w.walk(self._model_tree_root, self._model_tree_root))
        
        
        
            
    def _find_childs(self,parent_uuid):
        
        #at_least_one_child = False
        for element in self._elements.values():
            if element.owner_uuid == parent_uuid:
                # Set parent
                self._elements[element._uuid].parent = self._elements[parent_uuid]
                self._find_childs(element._uuid)
        
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
                            element_obj._uuid = element.get("uid")
                    
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
                    
                    self._elements.update({element_obj._uuid:element_obj})
                    print("    ",element_obj.name)
    
    
    def get_project_uuid(self, default=None):
        return_val = default
        
        for element in self._elements.values():
            if element.type == "Project": #Access element object
                return_val = element._uuid
                break
        
        return return_val
    
        
    def _load_project_uuid(self):
        '''
        '''
        self._uuid = self.get_project_uuid()

            
    def _get_uuid(self, owner_type, owner_name, element_type, element_name):
        
       pass
   
    def load(self, project_data_path):
        
        self._data_path = grl.string_to_path(str(project_data_path))
        self._load_standard_elements()
        self._load_project_uuid()
        self._build_model_tree()
            
