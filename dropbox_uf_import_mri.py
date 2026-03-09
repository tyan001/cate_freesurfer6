"""
MRI Data Processing Script

This script processes MRI data folders, reorganizing and renaming files based on specific patterns.
It separates T1 files from other modalities and moves them to designated directories.

Usage:
    python script_name.py [-h] [--dry-run] [--log-file LOG_FILE] base_path data_src

Arguments:
    base_path   The base directory containing MRI data folders
    data_src    Data source identifier (e.g., 'MTS' for Mt. Sinai)

Optional arguments:
    -h, --help            Show this help message and exit
    --dry-run             Perform a dry run without making any changes
    --log-file LOG_FILE   Specify the log file name (default: mri_processing.log in the base directory)
"""

from pathlib import Path
import re
import datetime
import shutil
import argparse
import logging

def setup_logger(name, log_file, level=logging.INFO):
    """
    Set up a logger with a specified name and log file.

    Args:
        name (str): Name of the logger.
        log_file (str or Path): Path to the log file.
        level (int): Logging level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger object.
    """
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
    """
    Match a folder name against predefined patterns.

    Args:
        test_string (str): The folder name to test.

    Returns:
        tuple or None: A tuple containing the pattern name and matched groups,
                       or None if no pattern matches.
    """
    patterns = [
        ("standard", r'^(\d+)_(\d+)$'),  # Pattern for format: 123456_12345678
        ("with_words", r'^(\d+)_(\w+)_(\d+)$'),  # Pattern for format: 123456_CL_12345678
        ("with_scanNum", r'^(\d+)-(\d+)_(\d+)$'),  # Pattern for format: 123456-12_12345678 (12th scan of patient 123456)
        ("with_letterNum", r'^(\d+)-([A-Z]+\d+)_(\d+)$'),  # Pattern for format: 123456-C1_12345678 
    ]
    
    for name, pattern in patterns:
        match = re.match(pattern, test_string)
        if match:
            return name, match.groups()
    
    return None


def rearrange_date(date_string):
    """
    Rearranges a date string from MMDDYYYY format to YYYYMMDD format with validation.
    
    Args:
        date_string (str): A date string in MMDDYYYY format (e.g., "12252023")
    
    Returns:
        str: The date string in YYYYMMDD format (e.g., "20231225")
        
    Raises:
        ValueError: If the date string is invalid or not in correct format
    """
    try:
        # Parse the date to validate it
        date_obj = datetime.datetime.strptime(date_string, '%m%d%Y')
        # Format it to desired output
        return date_obj.strftime('%Y%m%d')
    except ValueError:
        raise ValueError("Invalid date format. Use MMDDYYYY format with valid date.")


def get_new_name(dir, dataSrc):
    """
    Generate a new name for a directory based on its current name and a data source identifier.

    Args:
        dir (Path): The directory to rename.
        dataSrc (str): Data source identifier (e.g., 'MTS' for Mt. Sinai, UMD for UM).

    Returns:
        str or None: The new name for the directory, or None if the directory name doesn't match any known pattern.
    """
    try:
        name, groups = folder_name_patterns(dir.name)
        now = datetime.datetime.now()
    except Exception as e:
        logger.error(f"Error processing {dir.name}: {e}")
        return None
    
    logger.info(f"Processing {dir.name}")
    if name == 'standard':
        id = groups[0]
        id_prefix = id[:3] # groups[0][:3]
        scan_date = rearrange_date(groups[1]) # rearrange date to YYYYMMDD format
        proposed_name = f"{dataSrc}-{id_prefix}-{id}-{scan_date}-{now.strftime('%Y%m%d%H%M%S')}"
        return proposed_name
    elif name in ['with_words', 'with_scanNum', 'with_letterNum']:
        id = groups[0]
        id_prefix = id[:3] # groups[0][:3]
        scan_date = rearrange_date(groups[2]) # rearrange to YYYYMMDD format
        proposed_name = f"{dataSrc}-{id_prefix}-{id}-{scan_date}-{now.strftime('%Y%m%d%H%M%S')}"
        return proposed_name
    else:
        return None

def process_folder(base_dir, data_src, dry_run=False):
    """
    Process MRI data folders, reorganizing and renaming files.

    This function:
    1. Identifies T1 files and moves them to a 'nii' subdirectory, renaming them.
    2. Moves all other files to a new subdirectory in 'mri_modalities', named after the original folder.
    3. Removes the original folder if it becomes empty after processing.

    Args:
        base_dir (str or Path): The base directory containing MRI data folders.
        data_src (str): Data source identifier (e.g., 'MTS' for Mt. Sinai).
        dry_run (bool): If True, simulate the operations without making changes.
    """
    base = Path(base_dir)
    nii_path = base/'nii'
    modalities_path = base/'mri_modalities'
    dirs = list(base.glob('*'))
    # Create output directories if they don't exist
    if not dry_run:
        nii_path.mkdir(exist_ok=True)
        modalities_path.mkdir(exist_ok=True)
    else:
        logger.info(f"[DRY RUN] Would create directories: {nii_path} and {modalities_path}")
    
    for dir in dirs:
        new_name = get_new_name(dir, data_src)
        if new_name is None:
            logger.warning(f"Skipping {dir.name} - unable to process")
            continue
        
        logger.info(f"New name: {new_name}")
        files = list(dir.glob('*'))
        
        # Look for T1 file, if not found, look for Cor_MPRAGE file
        t1_file = next((file for file in files if 'T1' in file.name), None)
        if t1_file is None:
            t1_file = next((file for file in files if 'Cor_MPRAGE' in file.name), None)
            logger.warning(f"No T1 found using Cor_MPRAGE file: {t1_file}")
        
        if t1_file:
            if 'Cor_MPRAGE' in t1_file.name:
                new_t1_name = f"{new_name}_CorMPRAGE.nii"
            else:
                new_t1_name = f"{new_name}{t1_file.suffix}"
            if not dry_run:
                shutil.copy(str(t1_file), str(nii_path / new_t1_name))
                logger.info(f"copy T1/Cor_MPRAGE file to: {nii_path / new_t1_name}")
            else:
                logger.info(f"[DRY RUN] Would copy T1/Cor_MPRAGE file to: {nii_path / new_t1_name}")
        else:
            logger.warning(f"No T1 or Cor_MPRAGE file found in {dir}")
            
            
        # Process other modalities
        new_modality_dir = modalities_path / new_name
        if not dry_run:
            new_modality_dir.mkdir(exist_ok=True)
        else:
            logger.info(f"[DRY RUN] Would create directory: {new_modality_dir}")
        
        for file in files:
            # if file != t1_file:  # Skip the T1 file as it's already processed
            if not dry_run:
                shutil.move(str(file), str(new_modality_dir / file.name))
                logger.info(f"Moved {file.name} to: {new_modality_dir}")
            else:
                logger.info(f"[DRY RUN] Would move {file.name} to: {new_modality_dir}")
        
        # Remove the original directory if it's empty
        if not dry_run:
            if not any(dir.iterdir()):
                dir.rmdir()
                logger.info(f"Removed empty directory: {dir}")
        else:
            logger.info(f"[DRY RUN] Would remove empty directory: {dir}")

if __name__ == '__main__':
    
    
    example_text = '''example:
    python3 dropbox_uf_import.py /path/to/base_directory MTS --dry-run --log-file custom_log.log
    python3 dropbox_uf_import.py batch48 MTS --dry-run
    '''

    parser = argparse.ArgumentParser(
        description="Process MRI data folders\n\n" + example_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("base_path", type=str, help="The base directory containing MRI data folders")
    parser.add_argument("data_src", type=str, help="Data source identifier (e.g., 'MTS' for Mt. Sinai)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making any changes")
    parser.add_argument("--log-file", type=str, default="uf_import.log", help="Specify the log file name")
    
    args = parser.parse_args()
    
    # Set up the logger with the log file in the base directory
    base_dir = Path(args.base_path)
    log_file_path = base_dir / args.log_file
    logger = setup_logger("MRI_Import", log_file_path)
    
    logger.info(f"Starting MRI data processing for {args.base_path}")
    logger.info(f"Data source: {args.data_src}")
    logger.info(f"Dry run: {'Yes' if args.dry_run else 'No'}")
    logger.info(f"Log file: {log_file_path}")
    
    process_folder(args.base_path, args.data_src, args.dry_run)
    
    logger.info("MRI data processing completed")