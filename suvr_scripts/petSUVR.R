#!/usr/bin/env Rscript
#args[1] is MRI path to find aparc+aseg, asegVolume, aparcstatsVolumLeft, aparcstatsVolumRight 
#args[2] is PET name
#args[3] is output folder for results tables
#args[4] is the name with wich to start the output tables
#
#Usage: ./petSUVR.R <mriPath> <regPetPath> <outDir> <outNameStem>
#
#Output:
#   <outDir>/<outNameStem>_max
#   <outDir>/<outNameStem>_min
#   <outDir>/<outNameStem>_suv_cer
#   <outDir>/<outNameStem>_suv_cer_gm
#   <outDir>/<outNameStem>_mean_suv.csv
#   <outDir>/<outNameStem>_media_suv.csv
#   <outDir>/<outNameStem>_suvr_cerebellum.csv
#   <outDir>/<outNameStem>_suvr_cerebellum_gm.csv
#   <outDir>/<outNameStem>_suvr_combined_cerebellum.csv
#   <outDir>/<outNameStem>_suvr_combined_cerebellum_gm.csv
#   <outDir>/<outNameStem>_total_suv.csv
#
#Example usage:
# ./petSUVR.R ./temp/ADNI_002_S_0295_MR ./PET/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR ./res ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR
#
#The outputs will be:
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_max
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_min
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_suv_cer
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_suv_cer_gm
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_mean_suv.csv
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_media_suv.csv
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_suvr_cerebellum.csv
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_suvr_cerebellum_gm.csv
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_suvr_combined_cerebellum.csv
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_suvr_combined_cerebellum_gm.csv
#   ./res/ADNI_002_S_0295_PT_reg_ADNI_002_S_0295_MR_total_suv.csv
args = commandArgs(trailingOnly=TRUE)
inputMRI_folder = args[1]
output_folder = paste(args[3],"/",sep="")
inputPET_file = paste(args[2],".nii",sep="")
aparc_file=paste(inputMRI_folder,"_aparc+aseg.nii",sep="")
asegvo=paste(inputMRI_folder,"_asegVolume.csv",sep="")
apsl=paste(inputMRI_folder,"_aparcstatsVolumLeft.csv",sep="")
apsr=paste(inputMRI_folder,"_aparcstatsVolumRight.csv",sep="")
outName=args[4]

library(oro.nifti)
pet <-readNIfTI(inputPET_file)
aparcaseg <-readNIfTI(aparc_file)
rois_names <-read.csv("./FreesurferLUTR.txt",header = FALSE) 
rois_volumes_subcortical <-read.table(asegvo,header = FALSE, sep=',')
rois_volumes_cortical_r <-read.table(apsr,header = FALSE, sep=',')
rois_volumes_cortical_l <-read.table(apsl,header = FALSE, sep=',')

rois= as.vector(rois_names[[1]])
rois_names = as.vector(rois_names[[2]])
l=length(rois)

#process subcortical volumes into vectors of names and values
vol_v_subcortical <-vector()
vol_n_subcortical <-vector()
vol_v_subcortical = unname(unlist(rois_volumes_subcortical[2,]))
vol_n_subcortical = unname(unlist(rois_volumes_subcortical[1,]))
vol_n_subcortical = as.character(vol_n_subcortical)
vol_v_subcortical = as.numeric(as.character(vol_v_subcortical))

#process cortical right volumes into vectors of names and values
vol_v_cortical_r <-vector()
vol_n_cortical_r <-vector()
vol_v_cortical_r = unname(unlist(rois_volumes_cortical_r[2,]))
vol_n_cortical_r = unname(unlist(rois_volumes_cortical_r[1,]))
vol_n_cortical_r = as.character(vol_n_cortical_r)
vol_v_cortical_r = as.numeric(as.character(vol_v_cortical_r))

#process cortical left volumes into vectors of names and values
vol_v_cortical_l <-vector()
vol_n_cortical_l <-vector()
vol_v_cortical_l = unname(unlist(rois_volumes_cortical_l[2,]))
vol_n_cortical_l = unname(unlist(rois_volumes_cortical_l[1,]))
vol_n_cortical_l = as.character(vol_n_cortical_l)
vol_v_cortical_l = as.numeric(as.character(vol_v_cortical_l))
#read values from nifti and store in list values()
values <-list()
min=.Machine$integer.max
max=-1
for( i in 1:length(rois)) { values[[i]]=rois[i]}
for( i in 1:256) { 
  for (j in 1:256) { 
    for(k in 1:256){
      tryCatch({
        if( aparcaseg[i,j,k] !=0) { 
          values[[match(aparcaseg[i,j,k], rois )]] <- c(values[[match(aparcaseg[i,j,k], rois )]], pet[i,j,k])
          if(max<pet[i,j,k]) max=pet[i,j,k] #store max value
          if(min>pet[i,j,k]) min=pet[i,j,k] #store min value
        }
      }, error = function(e) {
        print(paste("i; ",i,", j: ",j,", k: ",k,sep="" ) )
        print(paste("    ",aparcaseg[i,j,k], ": ",match(aparcaseg[i,j,k], rois ),sep="" ) )
      } )
 }}} 
 
 #use list values() to calculate the results 
 suv_med <- vector()
 suv_avr <- vector()
 suv_su <- vector()
 for( i in 1:length(rois)) { 
values[[i]] =values[[i]][-1]
suv_med[i]= median(values[[i]], na.rm = TRUE)
suv_avr[i]= mean(values[[i]], na.rm = TRUE)
suv_su[i]=  sum(values[[i]], na.rm = TRUE)
}

# reference roi: 7 Left-Cerebellum-White-Matter,8 Left-Cerebellum-Cortex,#46 Right-Cerebellum-White-Matter,47  Right-Cerebellum-Cortex
suv_cer= (
			suv_avr[match(7, rois )]* vol_v_subcortical[match("Left-Cerebellum-White-Matter", vol_n_subcortical)] +
			suv_avr[match(8, rois )]* vol_v_subcortical[match("Left-Cerebellum-Cortex", vol_n_subcortical)] +
			suv_avr[match(46, rois )]* vol_v_subcortical[match("Right-Cerebellum-White-Matter", vol_n_subcortical)] +
			suv_avr[match(47, rois )]* vol_v_subcortical[match("Right-Cerebellum-Cortex", vol_n_subcortical)] )/
			(
			vol_v_subcortical[match("Left-Cerebellum-White-Matter", vol_n_subcortical)]+
			vol_v_subcortical[match("Left-Cerebellum-Cortex", vol_n_subcortical)] +
			vol_v_subcortical[match("Right-Cerebellum-White-Matter", vol_n_subcortical)]+
			vol_v_subcortical[match("Right-Cerebellum-Cortex", vol_n_subcortical)]
			)

# reference roi:8 Left-Cerebellum-Cortex, 47 Right-Cerebellum-Cortex
suv_cer_gm= (
			suv_avr[match(8, rois )]* vol_v_subcortical[match("Left-Cerebellum-Cortex", vol_n_subcortical)] +
			suv_avr[match(47, rois )]* vol_v_subcortical[match("Right-Cerebellum-Cortex", vol_n_subcortical)] )/
			(
			vol_v_subcortical[match("Left-Cerebellum-Cortex", vol_n_subcortical)] +
			vol_v_subcortical[match("Right-Cerebellum-Cortex", vol_n_subcortical)]
			)



# cerebellum (7,8,46,47) + Right-Cerebral-White-Matter 41, Left-Cerebral-White-Matter 2, Brain-Stem 16)
suv_ref_suvr_global= (
			suv_avr[match(7, rois )]* vol_v_subcortical[match("Left-Cerebellum-White-Matter", vol_n_subcortical)]+
			suv_avr[match(8, rois )]* vol_v_subcortical[match("Left-Cerebellum-Cortex", vol_n_subcortical)]+
			suv_avr[match(46, rois )]* vol_v_subcortical[match("Right-Cerebellum-White-Matter", vol_n_subcortical)]+
      suv_avr[match(47, rois )]* vol_v_subcortical[match("Right-Cerebellum-Cortex", vol_n_subcortical)]+
			#suv_avr[match(41, rois )]* vol_v_subcortical[match("rhCerebralWhiteMatterVol", vol_n_subcortical)]+
      #suv_avr[match(2, rois )]* vol_v_subcortical[match("lhCerebralWhiteMatterVol", vol_n_subcortical)]+
      suv_avr[match(16, rois )]* vol_v_subcortical[match("Brain-Stem", vol_n_subcortical)] )/
			(
			vol_v_subcortical[match("Left-Cerebellum-White-Matter", vol_n_subcortical)]+
			vol_v_subcortical[match("Left-Cerebellum-Cortex", vol_n_subcortical)] +
			vol_v_subcortical[match("Right-Cerebellum-White-Matter", vol_n_subcortical)]+
			vol_v_subcortical[match("Right-Cerebellum-Cortex", vol_n_subcortical)]+
      #vol_v_subcortical[match("rhCerebralWhiteMatterVol", vol_n_subcortical)]+
      #vol_v_subcortical[match("lhCerebralWhiteMatterVol", vol_n_subcortical)]+
      vol_v_subcortical[match("Brain-Stem", vol_n_subcortical)]
			) 




#vol_v_subcortical[match(rois_names[i], vol_n_subcortical )]

# cortical 1001 - 1035 2001- 2035 & suvr_subcortical  4-85 251-255
suvr <-vector()
for( i in 1:length(suv_avr))suvr[i] = suv_avr[i]/suv_cer

#sum_suvrsTotal needs to read aparcstatvolume
sum_suvrsTotalL=0
sum_suvrsTotalR=0
sum_volTotalL=0
sum_volTotalR=0
#AnteriorCingulate
sum_suvrs_AnteriorCingulateLeft=0
sum_vol_AnteriorCingulateLeft=0
sum_suvrs_AnteriorCingulateRight=0
sum_vol_AnteriorCingulateRight=0
AnteriorCingulate=0
#PosteriorCingulate
sum_suvrs_PosteriorCingulateLeft=0
sum_vol_PosteriorCingulateLeft=0
sum_suvrs_PosteriorCingulateRight=0
sum_vol_PosteriorCingulateRight=0
PosteriorCingulate=0
#Frontal
sum_suvrs_FrontalLeft=0
sum_vol_FrontalLeft=0
sum_suvrs_FrontalRight=0
sum_vol_FrontalRight=0
Frontal=0
#Temporal
sum_suvrs_TemporalLeft=0
sum_vol_TemporalLeft=0
sum_suvrs_TemporalRight=0
sum_vol_TemporalRight=0
Temporal=0
#Parietal
sum_suvrs_ParietalLeft=0
sum_vol_ParietalLeft=0
sum_suvrs_ParietalRight=0
sum_vol_ParietalRight=0
Parietal=0

#tmp <-list()
#tmp[[1]] = c(1)
#tmp[[2]] = c(2)
for( i in 1:length(suvr)) #this can be improved by skipping the first values
{
	if(rois[i] > 1000 )
	{	#left 1001 - 1035 use vol_v_cortical_l
		if(rois[i] < 2000 ) 
		{ 
			if (is.finite(suvr[i] ))
			{	#left
				vol = vol_v_cortical_l[match( gsub("-", "_", paste (substring(rois_names[i], 5, nchar(rois_names[i])), "_volume", sep="")), vol_n_cortical_l )]
				#total left
				sum_suvrsTotalL= sum_suvrsTotalL + suvr[i]* vol
				sum_volTotalL = sum_volTotalL + vol


        #AnteriorCingulateLeft
				if(rois[i] == 1026 || rois[i] == 1002)
				{
					sum_suvrs_AnteriorCingulateLeft = sum_suvrs_AnteriorCingulateLeft + suvr[i]*vol 
					sum_vol_AnteriorCingulateLeft = sum_vol_AnteriorCingulateLeft + vol
				}
				#PosteriorCingulateleft
				if(rois[i] == 1010 || rois[i] == 1023)
				{
					sum_suvrs_PosteriorCingulateLeft = sum_suvrs_PosteriorCingulateLeft + suvr[i]*vol 
					sum_vol_PosteriorCingulateLeft = sum_vol_PosteriorCingulateLeft + vol
				}
				#FrontalLeft 1003, 1012, 1014, 1018, 1019, 1020, 1027, 1028, 1032
				if(rois[i] == 1003 || rois[i] == 1012 || rois[i] == 1014 || rois[i] == 1018 || rois[i] == 1019
					|| rois[i] == 1020 || rois[i] == 1027 || rois[i] == 1028 || rois[i] == 1032)
				{
					sum_suvrs_FrontalLeft = sum_suvrs_FrontalLeft + suvr[i]*vol 
					sum_vol_FrontalLeft = sum_vol_FrontalLeft + vol
				}
				#TemporalLeft
				if(rois[i] == 1030 || rois[i] == 1015 )
				{
					sum_suvrs_TemporalLeft = sum_suvrs_TemporalLeft + suvr[i]*vol 
					sum_vol_TemporalLeft = sum_vol_TemporalLeft + vol
				}
				#ParietalLeft 
				if(rois[i] == 1008 || rois[i] == 1025 || rois[i] == 1029 || rois[i] == 1031)
				{
					sum_suvrs_ParietalLeft = sum_suvrs_ParietalLeft + suvr[i]*vol 
					sum_vol_ParietalLeft = sum_vol_ParietalLeft + vol
				}
			}
	    }
		#right 2001 - 2035 use vol_v_cortical_r, ignore 2000 
		if(rois[i] > 2000 ) 
		{	
			if (is.finite(suvr[i] ))
			{	#right
				vol= vol_v_cortical_r[match( gsub("-", "_", paste (substring(rois_names[i], 5, nchar(rois_names[i])), "_volume", sep="")), vol_n_cortical_r )]
				#tmp[[1]] <-c(tmp[[1]], suvr[i])
				#tmp[[2]] <-c(tmp[[2]], vol_v_cortical_r[match( gsub("-", "_", paste (substring(rois_names[i], 5, nchar(rois_names[i])), "_volume", sep="")), vol_n_cortical_r )])
				#total right
				sum_suvrsTotalR= sum_suvrsTotalR+ suvr[i]* vol
				sum_volTotalR = sum_volTotalR+ vol


				#AnteriorCingulateRight
				if(rois[i] == 2026 || rois[i] == 2002)
				{
					sum_suvrs_AnteriorCingulateRight = sum_suvrs_AnteriorCingulateRight + suvr[i]*vol
					sum_vol_AnteriorCingulateRight = sum_vol_AnteriorCingulateRight + vol
				}
				#PosteriorCingulateRight
				if(rois[i] == 2010 || rois[i] == 2023)
				{
					sum_suvrs_PosteriorCingulateRight = sum_suvrs_PosteriorCingulateRight + suvr[i]*vol
					sum_vol_PosteriorCingulateRight = sum_vol_PosteriorCingulateRight + vol
				}
				#FrontalRight
				if(rois[i] == 2003 || rois[i] == 2012 || rois[i] == 2014 || rois[i] == 2018 || rois[i] == 2019
					|| rois[i] == 2020 || rois[i] == 2027 || rois[i] == 2028 || rois[i] == 2032)
				{
					sum_suvrs_FrontalRight = sum_suvrs_FrontalRight + suvr[i]*vol 
					sum_vol_FrontalRight = sum_vol_FrontalRight + vol
				}
				#TemporalRight
				if(rois[i] == 2030 || rois[i] == 2015 )
				{
					sum_suvrs_TemporalRight = sum_suvrs_TemporalRight + suvr[i]*vol 
					sum_vol_TemporalRight = sum_vol_TemporalRight + vol
				}
				#ParietalRight
				if(rois[i] == 2008 || rois[i] == 2025 || rois[i] == 2029 || rois[i] == 2031)
				{
					#tmp[[1]] <-c(tmp[[1]], suvr[i])
					#tmp[[2]] <-c(tmp[[2]], vol)
					sum_suvrs_ParietalRight = sum_suvrs_ParietalRight + suvr[i]*vol 
					sum_vol_ParietalRight = sum_vol_ParietalRight + vol
				}

			}
		}
	}
}
#suvrTotal all cortical
suvr_total = (sum_suvrsTotalL + sum_suvrsTotalR) /(sum_volTotalR + sum_volTotalL)
suvr_totalL = sum_suvrsTotalL /sum_volTotalL
suvr_totalR = sum_suvrsTotalR /sum_volTotalR

#suvr_global
sum_suvrs_suvr_globalLeft = sum_suvrs_FrontalLeft + sum_suvrs_AnteriorCingulateLeft +sum_suvrs_PosteriorCingulateLeft + sum_suvrs_ParietalLeft + sum_suvrs_TemporalLeft

sum_suvrs_suvr_globalRight= sum_suvrs_FrontalRight + sum_suvrs_AnteriorCingulateRight +sum_suvrs_PosteriorCingulateRight + sum_suvrs_ParietalRight + sum_suvrs_TemporalRight

sum_vol_suvr_globalLeft = sum_vol_FrontalLeft + sum_vol_AnteriorCingulateLeft + sum_vol_PosteriorCingulateLeft + sum_vol_ParietalLeft +sum_vol_TemporalLeft
sum_vol_suvr_globalRight = sum_vol_FrontalRight + sum_vol_AnteriorCingulateRight + sum_vol_PosteriorCingulateRight + sum_vol_ParietalRight +sum_vol_TemporalRight 

suvr_globalLeft = (sum_suvrs_suvr_globalLeft ) / sum_vol_suvr_globalLeft
suvr_globalRight = ( sum_suvrs_suvr_globalRight) /sum_vol_suvr_globalRight
suvr_global = (sum_suvrs_suvr_globalLeft + sum_suvrs_suvr_globalRight) / (sum_vol_suvr_globalLeft + sum_vol_suvr_globalRight)

#AnteriorCingulate
AnteriorCingulateLeft = sum_suvrs_AnteriorCingulateLeft/sum_vol_AnteriorCingulateLeft
AnteriorCingulateRight = sum_suvrs_AnteriorCingulateRight/sum_vol_AnteriorCingulateRight
AnteriorCingulate = (sum_suvrs_AnteriorCingulateLeft + sum_suvrs_AnteriorCingulateRight) / (sum_vol_AnteriorCingulateLeft + sum_vol_AnteriorCingulateRight)
#PosteriorCingulate
PosteriorCingulateLeft= sum_suvrs_PosteriorCingulateLeft/sum_vol_PosteriorCingulateLeft
PosteriorCingulateRight= sum_suvrs_PosteriorCingulateRight/sum_vol_PosteriorCingulateRight
PosteriorCingulate = (sum_suvrs_PosteriorCingulateLeft + sum_suvrs_PosteriorCingulateRight) / (sum_vol_PosteriorCingulateLeft + sum_vol_PosteriorCingulateRight)
#Frontal
FrontalLeft= sum_suvrs_FrontalLeft/sum_vol_FrontalLeft
FrontalRight= sum_suvrs_FrontalRight/sum_vol_FrontalRight
Frontal = (sum_suvrs_FrontalLeft + sum_suvrs_FrontalRight) / (sum_vol_FrontalLeft + sum_vol_FrontalRight)
#Temporal
TemporalLeft= sum_suvrs_TemporalLeft/sum_vol_TemporalLeft
TemporalRight= sum_suvrs_TemporalRight/sum_vol_TemporalRight
Temporal = (sum_suvrs_TemporalLeft + sum_suvrs_TemporalRight) / (sum_vol_TemporalLeft + sum_vol_TemporalRight)
#Parietal
ParietalLeft= sum_suvrs_ParietalLeft/sum_vol_ParietalLeft
ParietalRight= sum_suvrs_ParietalRight/sum_vol_ParietalRight
Parietal = (sum_suvrs_ParietalLeft + sum_suvrs_ParietalRight) / (sum_vol_ParietalLeft + sum_vol_ParietalRight)
regions <- vector()
regions <- c(
			 "AnteriorCingulateLeft",								# 1026,1002 
			 "AnteriorCingulateRight",							# 2026 & 2002
			 "PosteriorCingulateLeft",							# 1023,1010 
			 "PosteriorCingulateRight",							# 2023,2010
			 "FrontalLeft",                       	# 1003, 1012, 1014, 1018, 1019, 1020, 1027, 1028, 1032
			 "FrontalRight", 										    # 2003, 2012, 2014, 2018, 2019, 2020, 2027, 2028, 2032
			 "TemporalLeft",										    # 1015, 1030
			 "TemporalRight",										    # 2015, 2030
			 "ParietalLeft",										    # 1008, 1025, 1029, 1031 
			 "ParietalRight",									      # 2008, 2025, 2029, 2031
			 "AnteriorCingulate",
			 "PosteriorCingulate",
			 "Frontal",
			 "Temporal",
			 "Parietal",
			 "TotallLeft",
			 "TotallRight",
       "Total",                               # all regions
			 "GloballLeft",
			 "GloballRight",
			 "Global"                               # all combined regios
			 )
suvr_all_vals <- vector()
suvr_all_vals <-c(AnteriorCingulateLeft,AnteriorCingulateRight,PosteriorCingulateLeft,PosteriorCingulateRight, 
					FrontalLeft, FrontalRight,TemporalLeft,TemporalRight, ParietalLeft, ParietalRight,
					AnteriorCingulate, PosteriorCingulate, Frontal, Temporal, Parietal, 
					suvr_totalL, suvr_totalR,suvr_total, suvr_globalLeft,suvr_globalRight, suvr_global)

#output to files
write(max, paste(output_folder,outName,"_max",sep=""))
write(min, paste(output_folder,outName,"_min",sep=""))

write(suv_cer_gm, paste(output_folder,outName,"_suv_cer_gm",sep=""))
write(suv_cer, paste(output_folder,outName,"_suv_cer",sep=""))

suvr_all_t <-data.frame(regions, suvr_all_vals )
suvr_all_t <- as.matrix(t(suvr_all_t))	
write.table(suvr_all_t, paste(output_folder,outName,"_suvr_combined_cerebellum.csv",sep=""),col.names =FALSE, row.names=FALSE, sep="," )		

suvr_all_t <-data.frame(regions, suvr_all_vals*suv_cer/suv_cer_gm )
suvr_all_t <- as.matrix(t(suvr_all_t))	
write.table(suvr_all_t, paste(output_folder,outName,"_suvr_combined_cerebellum_gm.csv",sep=""),col.names =FALSE, row.names=FALSE, sep="," )	


	
 suvr_t <-data.frame(rois, rois_names, suvr)
 suvr_t <- as.matrix(t(suvr_t))
 write.table(suvr_t, paste(output_folder,outName,"_suvr_cerebellum.csv",sep=""),col.names =FALSE, row.names=FALSE, sep="," )


 suvr_t <-data.frame(rois, rois_names, suvr*suv_cer/suv_cer_gm)
 suvr_t <- as.matrix(t(suvr_t))
 write.table(suvr_t, paste(output_folder,outName,"_suvr_cerebellum_gm.csv",sep=""),col.names =FALSE, row.names=FALSE, sep="," )

 
 suv_avr_t <-data.frame(rois, rois_names, suv_avr)
 suv_avr_t <- as.matrix(t(suv_avr_t))
 write.table(suv_avr_t, paste(output_folder,outName,"_mean_suv.csv",sep=""),col.names =FALSE, row.names=FALSE, sep=","  )
  suv_med_t <-data.frame(rois, rois_names, suv_med)
  suv_med_t  <- as.matrix(t(suv_med_t ))
 write.table(suv_med_t, paste(output_folder,outName,"_median_suv.csv",sep=""),col.names =FALSE, row.names=FALSE, sep="," )
  suv_su_t <-data.frame(rois, rois_names, suv_su)
  suv_su_t <- as.matrix(t(suv_su_t ))
 write.table(suv_su_t, paste(output_folder,outName,"_total_suv.csv",sep=""),col.names =FALSE, row.names=FALSE, sep="," )
quit()
