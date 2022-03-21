Import from SnapEDA

Symbol Lib exist
* Symbol Editor
* search for Symbol Lib
* click on it
* File - import symbol

Symbol Lib does not exist
* Symbol Editor
* File - new Library
* Go to git folder
* Enter name
* rest - see above

Footprint Lib
* same as Symbol only with the footprint editor

3D
* add folder with .3dshapes extension
* put wrl or step in folder
* add 3D in footprint editor
* click on footprint - click key 'e'
* 3D option
* path to 3D
  * ${KIPRJMOD}/3d-models/...
  * ki-lib_dir:xxx.3dshapes/...
* rotate and move to fit pcb footprint

ki-lib_dir must be defines in the preferendes - configure path - 3d path search Alias
with the path to the ki-lib git folder.

3d path configuration Forum post:
https://forum.kicad.info/t/help-understanding-3d-search-paths-and-environment-variables/20726/4 