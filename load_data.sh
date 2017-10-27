#!/bin/bash

export ROOTPATH=$PWD
cd $ROOTPATH

# Rebuild db
echo Rebuilding db
python manage.py packages -o setup_db
echo     rebuild complete.
echo ~-~-~-~-~-~-~

echo Loading thesauri and collections...
python manage.py packages -o import_reference_data -s $ROOTPATH/package/reference_data/FPAN-thesaurus.xml -ow overwrite -st keep
python manage.py packages -o import_reference_data -s $ROOTPATH/package/reference_data/FPAN-collections.xml -ow overwrite -st keep
echo     load complete.
echo ~-~-~-~-~-~-~

echo Loading resource models and branches...
python manage.py packages -o import_graphs -s $ROOTPATH/package/branches/
python manage.py packages -o import_graphs -s $ROOTPATH/package/resource_models/
echo     load complete.
echo ~-~-~-~-~-~-~

echo Loading map overlays...
echo     "(none to load at this time)"
echo     load complete.
echo ~-~-~-~-~-~-~

echo Loading business data...
echo FloridaStructures.csv
python manage.py packages -o import_business_data -s $ROOTPATH/package/business_data/FloridaStructures.csv -c "$ROOTPATH/package/business_data/Historic Structure.mapping" -ow overwrite --bulk
echo HistoricCemeteries.csv
python manage.py packages -o import_business_data -s $ROOTPATH/package/business_data/HistoricCemeteries.csv -c "$ROOTPATH/package/business_data/Historic Cemetery.mapping" -ow overwrite --bulk
echo     load complete.
echo ~-~-~-~-~-~-~