ODIR=./output
find $ODIR -name "*M.jpg" -exec rm {} \;
find $ODIR -name "*M.png" -exec rm {} \;
find $ODIR -name "*.tmp" -exec rm {} \;

# zip -r viaclasica.zip croquis aportaciones_croquis -x .DS_Store

