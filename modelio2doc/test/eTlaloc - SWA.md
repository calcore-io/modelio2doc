# Some Level 1 heading

Some text

## Some level 2 heading ${set-location>>n}

Some more text. Some attached image below.

${set-location:package.name:UseCase:ucd_diagram}

${img:type:location:elementName} diagram, type, name

${txt>>:type:location:elementName} type: name, description

Description: ${get.desc>>etlaloc_sya/pkg_SYA/SYA_UseCases/ucd_actors}

${get.image>>etlaloc_sya/pkg_SYA/SYA_UseCases/ucd_actors}

Figure "${get.name>>etlaloc_sya/pkg_SYA/SYA_UseCases/ucd_actors}"



-------------------------

${set-location>>etlaloc_sya/pkg_SYA/SYA_UseCases/ucd_actors}${get.image}

${get.desc}

${clear-location}

${get.desc}



name:type.name:type:name:type:name:type

${for:type==>element}

​	${get:element:field}

​	

​	${for:type==>nested_element}

​			${get:nested_element:field}

​	${end-for}

​	

${end-for}