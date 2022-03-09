#!/usr/local/bin/python2.7
# encoding: utf-8
'''
modelio2doc.__main__ -- shortdesc

modelio2doc.__main__ is a description

It defines classes_and_methods

@author:     Carlos Calvillo Cortes

@copyright:  2022 Carlos Calvillo Cortes. All rights reserved.

@license:    GPL v3

@contact:    carlos.calvillo@calcore.io
@deffield    updated: Updated
'''

import sys
import os
import pathlib as pl
import lxml.etree as ET
import anytree as at

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2022-03-07'
__updated__ = '2022-03-07'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg



def string_to_path(path_string):
    ''' Returns a "path" object for the given string. '''
    # pathlib requires regular diagonal, not reverse diagonal
    path_string = path_string.replace("\\", "/")
    
    return pl.Path(path_string)
    
    
def folder_exists(path):
    ''' Returns "True" if the given path is an existing folder. '''
    return_value = False
    
    if type(path) is str:
        path = string_to_path(path)
     
    if path is not None and path.exists() and path.is_dir():
        return_value = True
    
    return return_value


def file_exists(path):
    ''' Returns "True" if the given path is an existing file. '''
    return_value = False
    
    if type(path) is str:
        path = string_to_path(path)
     
    if path.exists() and path.is_file():
        return_value = True
    
    return return_value

def create_folder(folder):
    """ Creates the specified folder.
    """
    if folder_exists(folder) is False:
        try:
            folder.mkdir()
        except Exception as e:
            print('Failed to create folder %s. Reason: %s' % (folder, e))
    else:
        print("Folder to be created '%s' already exists." % folder)




def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2022 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
#         parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
#         parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
#         parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
#         parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')
        
        parser.add_argument("-t", "--template", dest="template", required=True, help="Input doc template file.")
        parser.add_argument("-mod_path", "--model_path", dest="model_path", required=True, help="Modelio project file")
        parser.add_argument("-mod_name", "--model_name", dest="model_name", required=True, help="Name of the modelio project")
        parser.add_argument("-o", "--output", dest="output", required=False, help="Output path")

        # Process arguments
        args = parser.parse_args()

#         paths = args.paths
#         verbose = args.verbose
#         recurse = args.recurse
#         inpat = args.include
#         expat = args.exclude
        
        template = args.template
        model_path = args.model_path
        model_name = args.model_name
        output = args.output

#         if verbose > 0:
#             print("Verbose mode on")
#             if recurse:
#                 print("Recursive mode on")
#             else:
#                 print("Recursive mode off")
                
        # ------- Dynamic imports
        modelio2doc_path = pl.Path(__file__).parent.absolute()
        try:
            import modelio2doc.model as mdl
            import modelio2doc.mdparse as mdp
        except:
            print("INFO: Setting up package...")
            # Add package path to sys.path and attempt the importing again
            modelio2doc_path_str = str(modelio2doc_path.parent)
            if modelio2doc_path_str not in sys.path:
                sys.path.append(modelio2doc_path_str)
                print("INFO: modelio2doc path added to sys.path.")
            # Attempt the import
            try:
                import modelio2doc.model as mdl
                import modelio2doc.mdparse as mdp
                
                print("INFO: Setting up package completed.")
            except Exception as e:
                print("ERROR: Couldn't load modelio2doc 'model' module.")
                print("Generated exception:\n")
                print(str(e))
                return 2
        
        
        # ------- Check input arguments
        
        # Does the input template file exists?
        template_file = string_to_path(template)
        if not file_exists(template_file):
            print("ERROR: Input template file not found.")
            return 2
        
        # Check modelio project path
        model_file = string_to_path(model_path)
        if not file_exists(model_file):
            print("ERROR: Input modelio project file not found.")
            return 2
        
        project_path = model_file.parent.absolute()
        
        # Check entry point in modelio model
        # Load project file name
        project_tree = ET.parse(str(model_file))
        project_root = project_tree.getroot()
        
        project_name = project_root.get("name", None)
        print("DEBUG: project name: ", project_name)
        
        project_data_path = None
        XML_elements = project_root.findall("fragment")
        for fragment in XML_elements:
            if fragment.get("id", None) ==  project_name:
                project_data_path = project_path / fragment.get("uri",None) / "model"
                print(project_data_path)
        
        if project_data_path is None:
            print("ERROR: Model data path not found")
            return 2
        
        # --------- Create Modelio Model Class
        modelio_el = mdl.ModelElement()
        modelio_attr = mdl.ElementAttr()
        
        
        
        modelio_obj = mdl.Model()
        modelio_obj.data_path = project_data_path
        modelio_obj.load_standard_elements()
        modelio_obj.load_project_uuid()
        modelio_obj.build_model_tree()
        
        modelio_obj.print_tree()
        
        print("")
        print("")
        print("")
        
        node = modelio_obj.get_element_by_path_str("Package:etlaloc_sya/Package:pkg_EEA")
        
        print(node)
        
#         for node in at.PreOrderIter(modelio_obj.model_tree_root, maxlevel=2):
#             print(node.type,":",node.name)
#         
#         print("")
#         print("")
#         print("")
#         
#         for child in modelio_obj.model_tree_root.children:
#             print(child.type+":"+child.name)
#             for child2 in child.children:
#                 print("    "+child2.type+":"+child2.name)
        
#          
#         for node in at.LevelOrderIter(modelio_obj.model_tree_root,maxlevel=2):
#             print(node.type,":",node.name)
#             
#             for node2 in at.LevelOrderIter(node,maxlevel=2):
#                 print("    ",node2.type,":",node2.name)

        
        
        
#         md_obj = mdp.MdFile()
#         
#         md_obj.load(template_file)
#         md_obj.generate()


        

        
        #print(modelio_obj.data_path)

        
        
        
        
                

#         if inpat and expat and inpat == expat:
#             raise CLIError("include and exclude pattern are equal! Nothing will be processed.")
# 
#         for inpath in paths:
#             ### do something with inpath ###
#             print(inpath)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
#         sys.argv.append("-h")
#         sys.argv.append("-v")
#         sys.argv.append("-r")
        
        sys.argv.append("-t")
        sys.argv.append("G:\\devproj\\github\\eTlatloc\\Software\\Architecture\\gen_swa\\SWA doc template\\eTlaloc - SWA.md")
        
        sys.argv.append("-mod_path")
        sys.argv.append("G:\\devproj\\github\\eTlatloc\\Software\\modelio_ws\\eTlaloc_SYA\\project.conf")
        
        sys.argv.append("-mod_name")
        sys.argv.append("eTlaloc_SYA")
        
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'modelio2doc.__main___profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())