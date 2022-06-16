# modelio2doc

[TOC]

# Overview

Tool for aiding the generation of documentation from a Modelio project.

The user creates an input template document with some "tokens" that operate over Modelio elements. Modelio2doc will "parse" this document and will resolve the tokens so that a final document is generated. 

Current implementation:

- Only markdown input/output format supported
- Only simple token-replacement supported

Future extensions:

- More input/output formats, e.g., MS Word, LibreOffice, HTML
- Advance token support, e.g., "if-else" conditionals, "for" loops, etc.

## Installation

TBD

# Usage

TBD

# Syntax

## General Syntax

### Element specification

For referencing an element within the Modelio model use this syntax:

*type_qualifier*.*type*:name

[optional] ***type_qualifier***: in Modelio, the different elements have a category for its type. This is known here as the "type_qualifier". Most of user defined elements will be of an standard type and hence will use the word "standard" for this field.

[optional] ***type***: type of the element to point to. E.g., Pacake, Actor, UseCase, UseCaseDiagram, etc.

[mandatory] **name**: name of the element.

**Note:** In Modelio, elements of same name are allowed as long as they are of different type/type_qualifier. In modelio2doc, when referring to an element without its type or type_qualifier, the reference will be to the first element matching the "name".

### Location specification

A location specification uses the following syntax:

*element_specification1/element_specification2/.../element_specificationN*

Each *element_specification* follows the syntax in section "Element specification".

### Command specification

A command within modelio2doc follows the next syntax:

${cmd_name*.cmd_extension1.cmd_extension2. ... .cmd_extensionN*>>*location_specification*}

[mandatory] **cmd_name**: Name of the command

[optional] ***cmd_extensionN***: A set of "command extensions". Depending on the given command, it may or may not require extensions.

[optional] **>>**: command separator which is optional

[optional] ***location_specification***: an optional location specification for the model element to operate with. If not provided, the command will operate (if applicable) over the "current location" which is set by the command "set-location".     

## Commands Syntax

### Set location (set-location)

This command is used to set the current model location. Following commands will operate with paths relative to this one.

The syntax is:

${set-location>>*location_specification*}

[mandatory] location_specification: shall be path to an existing model element (of any defined type).

### Clear location (clear-location)

TBD

### Get name (get.name)

TBD

### Get description (get.desc)

TBD

### Get image (get.image)

TBD

### Get attribute (get.att)

TBD

 