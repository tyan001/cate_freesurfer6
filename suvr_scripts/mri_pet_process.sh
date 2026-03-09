# !/bin/sh
# Convert the image's format to NITFTI
# call mgz2nii.csh before this code
############## REGISTRATION  SKULL_BAESED ##############
# AV45 to FreeSurfer Space  
# use T1.mgz as reference

#run form directory of script

mriFolder=./MRI
petFolder=../nii
tempFolder=./temp
resFolder=./res

export FREESURFER_HOME=/usr/local/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=$mriFolder
export PATH=$PATH:/usr/local/fsl/bin
export FSLOUTPUTTYPE=NIFTI

/usr/local/fsl/etc/fslconf/fsl.sh

if [ ! -d $tempFolder ]; then
   mkdir $tempFolder
fi

if [ ! -d $resFolder ]; then
   mkdir $resFolder
fi

for line in $(cat ./run.in); do
   elements=(${line//,/ })
   echo $elements
   
   # Path to the T1.nii files from Freesurfer. These T1.nii s are generated from mgz2nii.csh
   InputFile_PET=${elements[0]}
   # Path to the Nii PET scans
   InputMRISubject=${elements[1]}
   #Name and Path to registered PET
   regPetFile=$tempFolder/${InputFile_PET}_reg_${InputMRISubject}
   
   #echo "${elements[0]}, ${elements[1]}" 
   
   #Check if the T1 for the given patient already exists in tempDir
   if [ ! -f  $tempFolder/${InputMRISubject}_T1.nii ]; then
      if [ ! -f $mriFolder/$InputMRISubject/mri/T1.nii ]; then
         mri_convert -ot nii --out_orientation RAS $mriFolder/$InputMRISubject/mri/T1.mgz $tempFolder/${InputMRISubject}_T1.nii
      else
         cp $mriFolder/$InputMRISubject/mri/T1.nii $tempFolder/${InputMRISubject}_T1.nii
	 echo hello
      fi
   fi

   #Check if the aparc+aseg for the given patient already exists in tempDir
   if [ ! -f  $tempFolder/${InputMRISubject}_aparc+aseg.nii ]; then
      if [ ! -f $mriFolder/$InputMRISubject/mri/T1.nii ]; then
         mri_convert -ot nii --out_orientation RAS $mriFolder/$InputMRISubject/mri/aparc+aseg.mgz $tempFolder/${InputMRISubject}_aparc+aseg.nii
      else
         cp $mriFolder/$InputMRISubject/mri/aparc+aseg.mgz $tempFolder/${InputMRISubject}_aparc+aseg.nii
      fi
   fi

   # If aparcstatsVolumLeft does not exsist, run freesurfer command and create
   if [ ! -f "${tempFolder}/${InputMRISubject}_aparcstatsVolumLeft.csv" ]; then
      if [ ! -f "$mriFolder/${InputMRISubject}/stats/aparcstatsVolumLeft.csv" ]; then
         echo "Creating aparcstatsVolumLeft for: ${InputMRISubject}"
         aparcstats2table  --subjects ${InputMRISubject} --hemi lh --meas volume  --tablefile "${tempFolder}/${InputMRISubject}_aparcstatsVolumLeft.csv"
         sed -i -e 's/\t/,/g' "${tempFolder}/${InputMRISubject}_aparcstatsVolumLeft.csv"
      else
         cp "$mriFolder/${InputMRISubject}/stats/aparcstatsVolumLeft.csv" "${tempFolder}/${InputMRISubject}_aparcstatsVolumLeft.csv"
      fi
   fi
   # If aparcstatsVolumRight does not exsist, run freesurfer command and create
   if [ ! -f "${tempFolder}/${InputMRISubject}_aparcstatsVolumRight.csv" ]; then
      if [ ! -f "$mriFolder/${InputMRISubject}/stats/aparcstatsVolumRight.csv" ]; then
         echo "Creating aparcstatsVolumRight for: ${InputMRISubject}"
         aparcstats2table  --subjects ${InputMRISubject} --hemi rh --meas volume  --tablefile "${tempFolder}/${InputMRISubject}_aparcstatsVolumRight.csv"
         sed -i -e 's/\t/,/g' "${tempFolder}/${InputMRISubject}_aparcstatsVolumRight.csv"
      else
         cp "$mriFolder/${InputMRISubject}/stats/aparcstatsVolumRight.csv" "${tempFolder}/${InputMRISubject}_aparcstatsVolumRight.csv"
      fi
   fi
   # If asegVolume does not exsist, run freesurfer command and create
   if [ ! -f "${tempFolder}/${InputMRISubject}_asegVolume.csv" ]; then
      if [ ! -f "$mriFolder/${InputMRISubject}/stats/asegVolume.csv" ]; then
         echo "Creating asegVolume for: ${InputMRISubject}"
         asegstats2table  --subjects ${InputMRISubject} -m volume --tablefile "${tempFolder}/${InputMRISubject}_asegVolume.csv"
         sed -i -e 's/\t/,/g' "${tempFolder}/${InputMRISubject}_asegVolume.csv"
      else
         cp "$mriFolder/${InputMRISubject}/stats/asegVolume.csv" "${tempFolder}/${InputMRISubject}_asegVolume.csv"
      fi
   fi

   # Registration FLIRT from FSL
   # AV45 to MRI native space with Skull
   # input AV45   reference MRI_Std
   # output AV45_T1_Skull in native space
   if [ ! -f $regPetFile.nii ]; then
      echo "Registering PET to MRI..."
      echo "    PET: " "$petFolder/$InputFile_PET.nii"
      echo "    MRI: " "$tempFolder/${InputMRISubject}_T1.nii"
      flirt -in $petFolder/$InputFile_PET.nii -ref $tempFolder/${InputMRISubject}_T1.nii -out $regPetFile.nii -omat $regPetFile.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
      #gunzip $regPetFile.nii.gz
   fi

   echo "Computing SUVRs for ${InputFile_PET}_reg_${InputMRISubject}"
   # pass nii files and path to mri data
   ./petSUVR.R $tempFolder/${InputMRISubject} ${regPetFile} $resFolder ${InputFile_PET}_reg_${InputMRISubject}

done

