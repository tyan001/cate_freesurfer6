#!/usr/bin/env python3

import os
import glob
import argparse
import subprocess
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

# nohup python3 recon-all.py --input nii/ --output fsout --cores 2 &

def process_nifti(nifti_file, output_dir):
    """Process a single NIFTI file with recon-all."""
    # Extract filename without extension to use as subject ID
    filename = os.path.basename(nifti_file)
    subject_id = filename.replace('.nii.gz', '').replace('.nii', '')
    
    # Construct the recon-all command
    cmd = [
        'recon-all',
        '-i', nifti_file,
        '-s', subject_id,
        '-all',
        '-hippocampal-subfields-T1',
        '-sd', output_dir
    ]
    
    print(f"Processing {nifti_file} as subject {subject_id}")
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print(f"Completed processing {subject_id}")
        return (True, subject_id)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {subject_id}: {e}")
        return (False, subject_id)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process NIFTI files with FreeSurfer recon-all in parallel')
    parser.add_argument('--input', '-i', required=True, help='Input directory containing NIFTI files')
    parser.add_argument('--output', '-o', default='fsout', help='Output directory for FreeSurfer results')
    parser.add_argument('--cores', '-c', type=int, default=1, help='Number of cores to use')
    args = parser.parse_args()
    
    # nohup python3 recon-all.py --input nii/ --output fsout --cores 2 &
    
    # Create output directory if it doesn't exist
    # output_dir = os.path.join(args.input, args.output)
    os.makedirs(args.output, exist_ok=True)
    
    # Find all NIFTI files
    nifti_files = []
    for ext in ['.nii', '.nii.gz']:
        nifti_files.extend(glob.glob(os.path.join(args.input, f'*{ext}')))
    
    if not nifti_files:
        print(f"No NIFTI files found in {args.input}")
        return
    
    print(f"Found {len(nifti_files)} NIFTI files to process")
    print(f"Using {args.cores} cores for parallel processing")
    
    # Set the maximum number of cores to use
    max_cores = min(args.cores, multiprocessing.cpu_count(), len(nifti_files))
    
    # Process files in parallel
    results = []
    with ProcessPoolExecutor(max_workers=max_cores) as executor:
        futures = {executor.submit(process_nifti, nifti_file, args.output): nifti_file for nifti_file in nifti_files}
        for future in futures:
            results.append(future.result())
    
    # Print summary
    successful = [subj for success, subj in results if success]
    failed = [subj for success, subj in results if not success]
    
    print("\nProcessing Summary:")
    print(f"Total files: {len(nifti_files)}")
    print(f"Successfully processed: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed subjects:")
        for subj in failed:
            print(f"- {subj}")

if __name__ == "__main__":
    main()