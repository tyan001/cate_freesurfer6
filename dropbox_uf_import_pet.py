"""
PET Data Processing Script

This script processes PET data folders, reorganizing and renaming files based on specific patterns.
It separates PET and CT files and moves them to designated directories.

Usage:
    python script_name.py [-h] [--dry-run] [--log-file LOG_FILE] base_path data_src

Arguments:
    base_path   The base directory containing PET data folders
    data_src    Data source identifier (e.g., 'MTS' for Mt. Sinai)

Optional arguments:
    -h, --help            Show this help message and exit
    --dry-run             Perform a dry run without making any changes
    --log-file LOG_FILE   Specify the log file name (default: pet_processing.log in the base directory)
"""

from pathlib import Path
import re
import datetime
import shutil
import argparse
import logging

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

def folder_name_patterns(test_string):
    patterns = [
        ("standard", r'^(\d+)_(\d+)$'),
        ("with_words", r'^(\d+)_(\w+)_(\d+)$'),
        ("with_scanNum", r'^(\d+)-(\d+)_(\d+)$'),
        ("with_letterNum", r'^(\d+)-([A-Z]+\d+)_(\d+)$')
    ]
    
    for name, pattern in patterns:
        match = re.match(pattern, test_string)
        if match:
            return name, match.groups()
    
    return None

def rearrange_date(date_string):
    try:
        date_obj = datetime.datetime.strptime(date_string, '%m%d%Y')
        return date_obj.strftime('%Y%m%d')
    except ValueError:
        raise ValueError("Invalid date format. Use MMDDYYYY format with valid date.")

def get_new_name(dir, dataSrc):
    try:
        name, groups = folder_name_patterns(dir.name)
        now = datetime.datetime.now()
    except Exception as e:
        logger.error(f"Error processing {dir.name}: {e}")
        return None

    logger.info(f"Processing {dir.name}")
    if name == 'standard':
        id = groups[0]
        id_prefix = id[:3]
        scan_date = rearrange_date(groups[1])
        return f"{dataSrc}-{id_prefix}-{id}-{scan_date}-{now.strftime('%Y%m%d%H%M%S')}"
    elif name in ['with_words', 'with_scanNum', 'with_letterNum']:
        id = groups[0]
        id_prefix = id[:3]
        scan_date = rearrange_date(groups[2])
        return f"{dataSrc}-{id_prefix}-{id}-{scan_date}-{now.strftime('%Y%m%d%H%M%S')}"
    else:
        return None


def process_folder(base_dir, data_src, dry_run=False):
    base = Path(base_dir)
    nii_path = base / 'nii'
    ct_path = base / 'ct'
    
    # Define file patterns to process
    file_patterns = [
        {
            'pattern': 'mean_5mmblur.nii',
            'output_suffix': '_PET_5mmblur.nii',
            'destination': nii_path,
            'type': 'PET'
        },
        {
            'pattern': '6mmblur.nii',
            'output_suffix': '_PET_6mmblur.nii',
            'destination': nii_path,
            'type': 'PET'
        },
        {
            'pattern': '_PET_256.nii',
            'output_suffix': '_PET_256.nii',
            'destination': nii_path,
            'type': 'PET'
        },
        {
            'pattern': 'Amyloid_PET_CT',
            'output_suffix': '_PET_CT.nii',
            'destination': ct_path,
            'type': 'CT'
        },
        {
            'pattern': '_PET_3mmblur.nii',
            'output_suffix': '_PET_3mmblur.nii',
            'destination': nii_path,
            'type': 'PET'
        },
        
    ]
    
    # Create directories
    if not dry_run:
        nii_path.mkdir(exist_ok=True)
        ct_path.mkdir(exist_ok=True)
    else:
        logger.info(f"[DRY RUN] Would create directories: {nii_path} and {ct_path}")
    
    dirs = [d for d in base.iterdir() if d.is_dir()]
    
    for dir in dirs:
        new_name = get_new_name(dir, data_src)
        if new_name is None:
            logger.warning(f"Skipping {dir.name} - unable to process")
            continue
        
        logger.info(f"New name: {new_name}")
        files = list(dir.glob('*'))
        processed_files = set()
        
        # Process each file pattern
        for pattern_config in file_patterns:
            matching_file = next(
                (f for f in files if pattern_config['pattern'] in f.name), 
                None
            )
            
            if matching_file:
                new_filename = f"{new_name}{pattern_config['output_suffix']}"
                dest_path = pattern_config['destination'] / new_filename
                
                if not dry_run:
                    shutil.copy(str(matching_file), str(dest_path))
                    logger.info(f"Copied {pattern_config['type']} file to: {dest_path}")
                else:
                    logger.info(f"[DRY RUN] Would copy {pattern_config['type']} file to: {dest_path}")
                
                processed_files.add(matching_file)
            else:
                logger.warning(f"No {pattern_config['pattern']} file found in {dir}")
        
        # Log skipped files
        for file in files:
            if file not in processed_files:
                logger.info(f"Skipping unrelated file: {file.name}")
        
        # Remove empty directory
        if not dry_run and not any(dir.iterdir()):
            dir.rmdir()
            logger.info(f"Removed empty directory: {dir}")
        elif dry_run:
            logger.info(f"[DRY RUN] Would remove empty directory: {dir}")

if __name__ == '__main__':
    example_text = '''example:
    python3 pet_import.py /path/to/base_directory MTS --dry-run --log-file custom_log.log
    python3 pet_import.py batch48 MTS --dry-run
    '''

    parser = argparse.ArgumentParser(
        description="Process PET data folders\n\n" + example_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("base_path", type=str, help="The base directory containing PET data folders")
    parser.add_argument("data_src", type=str, help="Data source identifier (e.g., 'MTS' for Mt. Sinai)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making any changes")
    parser.add_argument("--log-file", type=str, default="pet_processing.log", help="Specify the log file name")

    args = parser.parse_args()

    base_dir = Path(args.base_path)
    log_file_path = base_dir / args.log_file
    logger = setup_logger("PET_Import", log_file_path)

    logger.info(f"Starting PET data processing for {args.base_path}")
    logger.info(f"Data source: {args.data_src}")
    logger.info(f"Dry run: {'Yes' if args.dry_run else 'No'}")
    logger.info(f"Log file: {log_file_path}")

    process_folder(args.base_path, args.data_src, args.dry_run)

    logger.info("PET data processing completed")
