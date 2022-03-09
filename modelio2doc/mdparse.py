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

@define
class Token(object):
    
    name: str = Factory(str)
    extensions: list[str] = Factory(list)
    argument: str = Factory(str)
    model_reference: model.Model = None
    
    def resolve(self):
        return_val = None
        
        action = "wrong_token: " + self.argument
        match self.name:
            case "set-location":
                action = "found"
            case "img":
                action = "1"
            case "txt":
                action = "2"
            case "attr":
                action = "3"
            case "for":
                action = "4"
            case "get":
                action = "5"
        
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
    md_file_in: pl.Path = None
    md_file_out: pl.Path = None
    model_reference: model.Model = None
    

    def load(self, md_file_in):
        md_file_in = grl.string_to_path(str(md_file_in))
        
        if grl.file_exists(md_file_in):
            self.md_file_in = md_file_in
            
    
    def generate(self, md_file_out = None):
        
        if md_file_out is None:
            in_file_name = self.md_file_in.stem
            md_file_out = self.md_file_in.with_name('out_'+in_file_name+self.md_file_in.suffix)
        
        print(md_file_out)
        
        if grl.file_exists(md_file_out):
            grl.delete_file(md_file_out)
        
        md_out = open(md_file_out, 'w')
              
        with open(self.md_file_in, 'r') as md_in:
            for line in md_in:
                md_out.write(self._parse_line(line))
        
                
        md_out.close()
        
    def _parse_line(self, line_in):
        
        line_out = ""
        token_pattern = r'\$\{(.+)\}'
        regex = re.compile(token_pattern)
        
        line_out = re.sub(regex, self._process_token, line_in)
        
        return line_out
    
    def _process_token(self, matchobj):
        
        return_val = matchobj.group(0)
        
        # Get token type
        try:
            line_split = matchobj.group(1).split(">>")
            
            # Create empty Token object
            token = Token(model_reference = self.model_reference)
            
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
        
        return "[" + return_val + "]"
        
    
    