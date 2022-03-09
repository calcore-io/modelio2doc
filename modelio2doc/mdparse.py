'''
Created on Mar 8, 2022

@author: Carlos Calvillo Cortes
'''

from attrs import define, Factory
import pathlib as pl
import lxml.etree as ET
import modelio2doc.general as grl
import re



@define
class MdFile(object):
    
    _curr_location: str = Factory(str)
    md_file_in: pl.Path = None
    md_file_out: pl.Path = None
    

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
                md_out.write(self.parse_line(line))
        
                
        md_out.close()
        
    def parse_line(self, line_in):
        
        line_out = ""
        token_pattern = r'\$\{(.+)\}'
        regex = re.compile(token_pattern)
        
        line_out = re.sub(regex, self.resolve_token, line_in)
        
        return line_out
    
    def resolve_token(self, matchobj):
        
        # Get token type
        token = matchobj.group(1).split(":")
        token_type = token[0]
        
        action = ""
        
        match token_type:
            case "set-active-location":
                loc_owner = token[1]
                loc_ = token[2]
                loc_name = token[3]
                action = loc_owner + ">" + token_type + ">" + loc_name
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
        
        
        return "[" + token_type + "-" + action + "]"
        
    
    