'''
Created on Mar 8, 2022

@author: Carlos Calvillo Cortes
'''

from attrs import define, Factory
import pathlib as pl
import lxml.etree as ET
import modelio2doc.general as grl
import re
import model
import logging
import base64

@define
class Token(object):
    
    name: str = Factory(str)
    extensions: list[str] = Factory(list)
    argument: str = Factory(str)
    _model_reference: model.Model = None
    output_path: pl.Path = Factory(pl.Path)
    
    def resolve(self):
        return_val = None
        
        print("self.name: ", self.name)
        print("self.argument: ", self.argument)
        
        action = "wrong_token: " + self.argument
        match self.name:
            case "set-location":
                print("### SET-LOCATION")
                # Argument is required
                if self.argument != "":
                    loc_result = self._model_reference.set_current_path(self.argument)
                    if loc_result is not None:
                        action = "" 
                    else:
                        logging.error("Wrong location argument for 'set-location'.")
                        action = "Wrong location"     
                else:
                    self._model_reference.clear_current_path()
                    logging.info("Current path cleared.")
                    action = ""
            
            case "clear-location":
                self._model_reference.clear_current_path()
                action = ""

            case "get":
                action = self._resolve_get()
                
        
        return_val = action
        return return_val
    
    def _resolve_set_location(self):
        '''
            Resolve token of type ""
        '''
        return_val = None
        
        return return_val
    
    def _resolve_get(self):
        '''
            Resolve token of type ""
        '''
        return_val = None
        
        action = "ERROR -GET-"
        
        if len(self.extensions) == 0:
            logging.error("Missing extensions for 'get'")
            action = "Wrong extension"
        else:
            # Argument is an optional relative path. If not provided, do not pass the path
            # to the get element function.
            if self.argument != "":
                element = self._model_reference.get_element_by_path_str(self.argument)
            else:
                element = self._model_reference.get_element_by_path_str()
                
            if element is not None: 
                # Execute proper argument
                match self.extensions[0]:
                    case "image":
                        el_value = None
                        if "PreviewData" in element.attributes:
                            el_value = element.attributes["PreviewData"]
                        if el_value is None:
                            action = "Wrong image element"
                        else:
                            print(el_value.value)
                            re_image = r'data:image/(.+);(.+),(.+)'
                            regex = re.compile(re_image)
                            match = re.findall(regex, el_value.value)
                            
                            extension = match[0][0]
                            decode_str = match[0][1]
                            data = match[0][2]
                            
                            if extension is not None \
                            and decode_str is not None \
                            and data is not None:
                            
                                if decode_str != "base64":
                                    logging.warning("Image is not coded in base64")
                                    
                                img_data = base64.b64decode(data)
                                #Generate image file:
                                out_path = self.output_path / "img"
                                if grl.folder_exists(out_path) is False:
                                    print("Creating: ", out_path)
                                    grl.create_folder(out_path)
                                
                                out_file_path = out_path / ( element.uuid + ".png" )
                                with open(out_file_path, 'wb') as fh:
                                    fh.write(img_data)
                                
                                # Print markdown line to insert image
                                action = "![]("+str(out_file_path)+")"
                    
                    case "name":
                        action = element.name
                    
                    case "desc":
                        action = element.desc
                    
                    case "attr":
                        if self.extensions[1] in element.attributes:
                            action = element.attributes[self.extensions[1]]
                        else:
                            action = "Attribute not found."
                            logging.error("Attribute not found.")
            else:
                logging.error("Element not found.")
            
        return_val = action
        return return_val
    
    def _get_description(self):
        '''
        '''
        return_val = None
        
        return return_val
    
    def _get_image(self):
        '''
        '''
        return_val = None
        
        return return_val
    
    def _get_attribute(self):
        '''
        '''
        return_val = None
        
        return return_val

@define
class MdParse(object):
    
    _curr_location: str = Factory(str)
    _md_file_in: pl.Path = None
    _md_file_out: pl.Path = None
    _md_file_put_path: pl.Path = None
    _model_reference: model.Model = None
    

    def load(self, md_file_in):
        md_file_in = grl.string_to_path(str(md_file_in))
        
        if grl.file_exists(md_file_in):
            self._md_file_in = md_file_in
            
    
    def generate(self, model_ref: model.Model, md_file_in, md_file_out = None):
        
        # Set model reference
        self._model_reference = model_ref
        
        # Check input file
        md_file_in = grl.string_to_path(str(md_file_in))
        
        if grl.file_exists(md_file_in):
            self._md_file_in = md_file_in
        else:
            logging.error("Input file doesn't exists.")
        
        if md_file_out is None:
            in_file_name = self._md_file_in.stem
            md_file_out = self._md_file_in.with_name('out_'+in_file_name+self._md_file_in.suffix)
            
        self._md_file_put_path = md_file_out.parent.absolute()
        
        if grl.file_exists(md_file_out):
            grl.delete_file(md_file_out)
        
        md_out = open(md_file_out, 'w')
              
        with open(self._md_file_in, 'r') as md_in:
            for line in md_in:
                md_out.write(self._parse_line(line))
        
                
        md_out.close()
        
    def _parse_line(self, line_in):
        
        line_out = ""
        token_pattern = r'\$\{(.+?)\}'
        regex = re.compile(token_pattern)
        
        line_out = re.sub(regex, self._process_token, line_in)
        
        return line_out
    
    def _process_token(self, matchobj):
        
        return_val = matchobj.group(0)
        
        # Get token type
        try:
            line_split = matchobj.group(1).split(">>")
            
            # Create empty Token object
            token = Token(model_reference = self._model_reference)
            token.output_path = self._md_file_put_path
            
            # Token string is the text left to the ">>"
            aux_token_str = line_split[0]
            
            for i, token_part in enumerate(aux_token_str.split(".")):
                if i == 0:
                    # First element is the token name
                    token.name = token_part
                else:
                    # Subsequent elements if present are token extensions
                    token.extensions.append(token_part)
 
            # Token argument is the text right to the ">>"
            if len(line_split) > 1:
                token.argument = line_split[1] 
            
        except Exception as e:
            print('ERROR: Incorrect token found: %s.\n     generated exception: %s ' % (matchobj.group(1), e))
            return "ERROR: " + matchobj.group(0)
        
        
        resolved_token = token.resolve()
        if resolved_token is not None:
            return_val = resolved_token
        
        return return_val
        
    
    