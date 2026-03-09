#!/usr/bin/env python3
import os
import subprocess
import glob
import argparse
import logging
import multiprocessing
from pathlib import Path
from functools import partial

def setup_logging(verbose):
    """Set up logging configuration"""
    # Create logger
    logger = logging.getLogger("freesurfer_processor")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create formatter - without timestamps and log level names
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def convert_mgz_to_nii(input_file, output_file, logger):
    """Convert .mgz file to .nii using mri_convert"""
    cmd = f"mri_convert {input_file} {output_file}"
    logger.debug(f"Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert {input_file}: {e}")
        return False

def convert_surf_to_gii(input_file, output_file, logger):
    """Convert FreeSurfer surface file to GIFTI (.gii) using mris_convert"""
    cmd = f"mris_convert {input_file} {output_file}"
    logger.debug(f"Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert {input_file}: {e}")
        return False

def process_subject(subject_dir, output_base_dir, logger):
    """Process FreeSurfer files for a single subject"""
    subject_id = os.path.basename(subject_dir)
    output_dir = os.path.join(output_base_dir, subject_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # Use a process-specific logger to avoid race conditions
    process_logger = logging.getLogger(f"freesurfer_processor.{subject_id}")
    process_logger.setLevel(logger.level)
    for handler in logger.handlers:
        process_logger.addHandler(handler)
    
    process_logger.info(f"Processing subject: {subject_id}")
    
    # Convert MGZ volumes to NII
    mgz_to_nii_mapping = {
        os.path.join(subject_dir, "mri", "T1.mgz"): os.path.join(output_dir, "T1.nii"),
        os.path.join(subject_dir, "mri", "brain.mgz"): os.path.join(output_dir, "brain.nii"),
        os.path.join(subject_dir, "mri", "aparc+aseg.mgz"): os.path.join(output_dir, "aparc+aseg.nii"),
        os.path.join(subject_dir, "mri", "wm.mgz"): os.path.join(output_dir, "wm.nii")
    }
    
    for mgz_file, nii_file in mgz_to_nii_mapping.items():
        if os.path.exists(mgz_file):
            process_logger.info(f"  Converting {os.path.basename(mgz_file)} to NII format...")
            if convert_mgz_to_nii(mgz_file, nii_file, process_logger):
                process_logger.info(f"  Successfully converted to {os.path.basename(nii_file)}")
        else:
            process_logger.warning(f"  Warning: {mgz_file} not found")
    
    # Convert surface files to GIFTI
    surf_to_gii_mapping = {
        os.path.join(subject_dir, "surf", "lh.pial"): os.path.join(output_dir, "lh.pial.gii"),
        os.path.join(subject_dir, "surf", "lh.white"): os.path.join(output_dir, "lh.white.gii"),
        os.path.join(subject_dir, "surf", "rh.pial"): os.path.join(output_dir, "rh.pial.gii"),
        os.path.join(subject_dir, "surf", "rh.white"): os.path.join(output_dir, "rh.white.gii")
    }
    
    for surf_file, gii_file in surf_to_gii_mapping.items():
        if os.path.exists(surf_file):
            process_logger.info(f"  Converting {os.path.basename(surf_file)} to GIFTI format...")
            if convert_surf_to_gii(surf_file, gii_file, process_logger):
                process_logger.info(f"  Successfully converted to {os.path.basename(gii_file)}")
        else:
            process_logger.warning(f"  Warning: {surf_file} not found")
            
    return subject_id

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Process FreeSurfer output files and convert to NIfTI and GIFTI formats',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # python3 mriWebConvert.py  -i fsout -o websitefiles
    
    # Add arguments
    parser.add_argument('--input', '-i', required=True,
                        help='FreeSurfer subjects directory containing subject folders')
    parser.add_argument('--output', '-o', required=True,
                        help='Output website directory where processed files will be saved')
    parser.add_argument('--subjects', '-s', nargs='+',
                        help='Specific subjects to process (optional, processes all subjects if not specified)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress all output except errors')
    parser.add_argument('--log', '-l', 
                        help='Log file path (optional, logs to console by default)')
    parser.add_argument('--cores', '-c', type=int, default=4,
                        help='Number of CPU cores to use for parallel processing')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logger
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
        
    # Configure logging
    logger = setup_logging(args.verbose)
    
    # Add file handler if log file is specified
    if args.log:
        file_handler = logging.FileHandler(args.log)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    freesurfer_dir = args.input
    output_base_dir = args.output
    specific_subjects = args.subjects
    num_cores = min(args.cores, multiprocessing.cpu_count())
    
    # Validate input directory
    if not os.path.isdir(freesurfer_dir):
        logger.error(f"Input directory does not exist: {freesurfer_dir}")
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Find subject directories
    if specific_subjects:
        subject_dirs = [os.path.join(freesurfer_dir, subj) for subj in specific_subjects 
                       if os.path.isdir(os.path.join(freesurfer_dir, subj))]
        if not subject_dirs:
            logger.error("None of the specified subjects were found")
            return 1
    else:
        subject_dirs = [f for f in glob.glob(os.path.join(freesurfer_dir, "*")) 
                       if os.path.isdir(f) and not os.path.basename(f).startswith(".")]
        if not subject_dirs:
            logger.error(f"No subject directories found in {freesurfer_dir}")
            return 1
    
    logger.info(f"Found {len(subject_dirs)} subject directories")
    logger.info(f"Using {num_cores} CPU cores for parallel processing")
    
    # Process subjects in parallel
    try:
        # Create a pool of worker processes
        with multiprocessing.Pool(processes=num_cores) as pool:
            # Create a partial function with fixed arguments
            process_func = partial(process_subject, output_base_dir=output_base_dir, logger=logger)
            
            # Map the function to subject directories and get results
            results = pool.map(process_func, subject_dirs)
            
        # Log completion
        logger.info(f"Successfully processed {len(results)} subjects")
        logger.info("Processing complete!")
        
    except KeyboardInterrupt:
        logger.error("Processing interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"An error occurred during parallel processing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Configure multiprocessing to work properly in all environments
    multiprocessing.set_start_method('spawn', force=True)
    exit(main())