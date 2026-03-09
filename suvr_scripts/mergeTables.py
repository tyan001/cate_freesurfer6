import csv
from os import listdir, path, makedirs
from pathlib import Path

# Constants
RES_DIR = "./res"
STATS_DIR = "./stats"
COMPOUND_LOOKUP_FILE = 'compoundLU.csv'

# Centiloid conversion formulas by compound
CENTILOID_FORMULAS = {
    "Amyvid": lambda suvr: 183.07 * suvr - 177.26,
    "Neuraceq": lambda suvr: 153.4 * suvr - 154.9,
    "PiB": lambda suvr: 100 * ((suvr - 1.009) / 1.067)
}


def load_compound_lookup(filename):
    """Load compound lookup table from CSV file."""
    compound_dict = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            pid = row[0]
            compound = row[1]
            
            # Check for mismatches
            if pid in compound_dict:
                if compound_dict[pid] != compound:
                    print(f"Date missmatch: {compound_dict[pid]}, {compound}")
            else:
                compound_dict[pid] = compound
    
    return compound_dict


def merge_simple_table(table_name, res_dir, output_dir):
    """
    Merge simple tables (suvr_cerebellum.csv and suvr_cerebellum_gm.csv).
    These tables have a 2-row header and don't require compound/centiloid calculations.
    """
    print(f"Processing: {table_name}")
    output_path = path.join(output_dir, table_name)
    is_new_table = not path.exists(output_path)
    
    with open(output_path, 'w') as write_file:
        writer = csv.writer(write_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_index = 0
        
        for file in listdir(res_dir):
            if file.endswith("_" + table_name):
                # Extract name from filename
                name = file[:file.find("_" + table_name)]
                
                with open(f"{res_dir}/{file}") as csv_file:
                    reader = csv.reader(csv_file, delimiter=',')
                    
                    for row_index, row in enumerate(reader):
                        if row_index < 2:
                            # Header rows
                            if is_new_table and file_index == 0:
                                row.insert(0, 'PID')
                                writer.writerow(row)
                        else:
                            # Data rows
                            row.insert(0, name)
                            writer.writerow(row)
                
                file_index += 1


def extract_pid_from_filename(filename, method):
    """Extract PID from filename using specified method."""
    if method == 'cerebellum':
        # Used in suvr_combined_cerebellum.csv
        start = filename.find("_reg_", 1) + 13
        pid = filename[start:]
        pid = pid[:pid.find("-", 0)]
    elif method == 'cerebellum_gm':
        # Used in suvr_combined_cerebellum_gm.csv
        start = filename.find("_reg_", 1) + 5
        pid = filename[start:]
        pid = pid[:pid.find("_", 1)]
    return pid


def merge_combined_cerebellum(compound_dict, res_dir, output_dir):
    """Merge suvr_combined_cerebellum.csv with compound and centiloid calculations."""
    table_name = 'suvr_combined_cerebellum.csv'
    print(f"Processing: {table_name}")
    output_path = path.join(output_dir, table_name)
    is_new_table = not path.exists(output_path)
    
    with open(output_path, 'w') as write_file:
        writer = csv.writer(write_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_index = 0
        
        for file in listdir(res_dir):
            if file.endswith("_" + table_name):
                name = file[:file.find("_" + table_name)]
                
                with open(f"{res_dir}/{file}") as csv_file:
                    reader = csv.reader(csv_file, delimiter=',')
                    global_index = 0
                    
                    for row_index, row in enumerate(reader):
                        if row_index == 0:
                            # Header row
                            global_index = row.index('Global')
                            if is_new_table and file_index == 0:
                                row.insert(0, 'PID')
                                row.insert(1, 'Compound')
                                row.append('Centiloid')
                                writer.writerow(row)
                        else:
                            # Data rows
                            suvr = float(row[global_index])
                            row.insert(0, name)
                            
                            # Extract PID from filename
                            pid = extract_pid_from_filename(row[0], 'cerebellum')
                            print(pid)
                            
                            # Get compound from lookup or default to Neuraceq
                            compound = compound_dict.get(pid, "Neuraceq")
                            
                            # Add compound data and calculate centiloid
                            row.insert(1, compound)
                            if compound in CENTILOID_FORMULAS:
                                centiloid = CENTILOID_FORMULAS[compound](suvr)
                                row.append(str(centiloid))
                            else:
                                # Default to Neuraceq formula if compound not in formulas
                                centiloid = CENTILOID_FORMULAS["Neuraceq"](suvr)
                                row.append(str(centiloid))
                            
                            writer.writerow(row)
                    
                file_index += 1


def merge_combined_cerebellum_gm(compound_dict, res_dir, output_dir):
    """Merge suvr_combined_cerebellum_gm.csv with compound and centiloid calculations."""
    table_name = 'suvr_combined_cerebellum_gm.csv'
    print(f"Processing: {table_name}")
    output_path = path.join(output_dir, table_name)
    is_new_table = not path.exists(output_path)
    
    with open(output_path, 'w') as write_file:
        writer = csv.writer(write_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_index = 0
        
        for file in listdir(res_dir):
            if file.endswith("_" + table_name):
                name = file[:file.find("_" + table_name)]
                
                with open(f"{res_dir}/{file}") as csv_file:
                    reader = csv.reader(csv_file, delimiter=',')
                    global_index = 0
                    
                    for row_index, row in enumerate(reader):
                        if row_index == 0:
                            # Header row
                            global_index = row.index('Global')
                            if is_new_table and file_index == 0:
                                row.insert(0, 'PID')
                                row.insert(1, 'Compound')
                                row.append('Centiloid')
                                writer.writerow(row)
                        else:
                            # Data rows
                            suvr = float(row[global_index])
                            row.insert(0, name)
                            
                            # Extract PID from filename
                            pid = extract_pid_from_filename(row[0], 'cerebellum_gm')
                            
                            # Get compound from lookup or default to Neuraceq
                            compound = compound_dict.get(pid, "Neuraceq")
                            
                            # Add compound data and calculate centiloid
                            row.insert(1, compound)
                            if compound in CENTILOID_FORMULAS:
                                centiloid = CENTILOID_FORMULAS[compound](suvr)
                                row.append(str(centiloid))
                            else:
                                # Default to Neuraceq formula if compound not in formulas
                                centiloid = CENTILOID_FORMULAS["Neuraceq"](suvr)
                                row.append(str(centiloid))
                            
                            writer.writerow(row)
                    
                file_index += 1


def setup_output_directory(output_dir):
    """
    Create the output directory if it doesn't exist and set permissions.
    Uses exist_ok=True to avoid errors if directory already exists.
    """
    makedirs(output_dir, exist_ok=True)
    
    # Set directory permissions to allow full access (read, write, execute)
    # This is optional and may not work on all systems (especially Windows)
    try:
        stats_path = Path(output_dir)
        stats_path.chmod(0o777)  # rwxrwxrwx permissions
    except Exception as e:
        # Silently continue if permission change fails (e.g., on Windows or restricted systems)
        pass


def main():
    """Main execution function."""
    # Create stats directory with appropriate permissions
    setup_output_directory(STATS_DIR)
    
    # Load compound lookup table
    compound_dict = load_compound_lookup(COMPOUND_LOOKUP_FILE)
    
    # Merge simple tables
    merge_simple_table('suvr_cerebellum.csv', RES_DIR, STATS_DIR)
    merge_simple_table('suvr_cerebellum_gm.csv', RES_DIR, STATS_DIR)
    
    # Merge combined tables with calculations
    merge_combined_cerebellum(compound_dict, RES_DIR, STATS_DIR)
    merge_combined_cerebellum_gm(compound_dict, RES_DIR, STATS_DIR)


if __name__ == "__main__":
    main()