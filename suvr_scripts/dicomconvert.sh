# This file is Chris's property and Chris's property only, if you are not Robin 
# than this file does NOT belong to you and you should therefore not claim 
# ownership for yourself or anyone else.
#
# VERSION 2.1 - 09/09/2019
#
# RESOURCE TO LOCAL FOLDER
export FREESURFER_HOME=/usr/local/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=$PWD

set +x
errorList=""

for f in ./DICOM/*; do 
   if [ -d $f ]; then
      startT=$SECONDS
      start=$(date +"%T")
      echo $file "has started running at" $start

      name=$(basename -- "$f")
      dcmunpack -src DICOM -targ NII -generic -run 5 n nii $name
 
      endT=$SECONDS
      end=$(date +"%T")
      echo $file "has finished running at" $end
      echo "Took: ${endT-startT} seconds"
   fi
done

