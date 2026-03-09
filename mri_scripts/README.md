# MRI Scripts

Scripts for running FreeSurfer `recon-all` on T1 MRI data in parallel, extracting cortical/subcortical statistics, and converting outputs for visualization.

---

## Scripts

| Script | Description |
|--------|-------------|
| `recon-all.py` | Parallel `recon-all` runner |
| `stats.py` | Extracts FreeSurfer stats tables and exports to CSV |
| `mriWebConvert.py` | Converts FreeSurfer outputs to NIfTI/GIFTI |
| `quantifyHippocampalSubfields.sh` | Collects hippocampal subfield volumes across subjects (called by `stats.py`) |
| `stats2tableV1.command` | Legacy shell script for stats table extraction |

---

## Directory Layout

Run scripts from the project root. Expected inputs and generated outputs:

```text
<project_dir>/
├── nii/                          # INPUT: T1 NIfTI files (one per subject, from import step)
│   ├── MTS-123-123456-20231225-20231225120000.nii
│   └── ...
├── fsout/                        # OUTPUT: recon-all results (auto-created by recon-all.py)
│   └── <subjid>/
│       ├── mri/                  #   volumes (T1.mgz, brain.mgz, aparc+aseg.mgz, wm.mgz, ...)
│       ├── surf/                 #   surfaces (lh/rh.pial, lh/rh.white, ...)
│       └── stats/                #   stats tables (aseg.stats, lh/rh.aparc.stats, ...)
├── stats/
│   └── csv/                      # OUTPUT: cleaned CSV tables (auto-created by stats.py)
│       ├── aseg_vol.csv
│       ├── aparc_vol_lh.csv
│       ├── aparc_vol_rh.csv
│       └── hippocampal_subfields.csv
└── websitefiles/                 # OUTPUT: NIfTI/GIFTI for visualization (auto-created by mriWebConvert.py)
    └── <subjid>/
        ├── T1.nii
        ├── brain.nii
        ├── aparc+aseg.nii
        ├── wm.nii
        ├── lh.pial.gii
        ├── rh.pial.gii
        ├── lh.white.gii
        └── rh.white.gii
```

---

## Pipeline Steps

### 1. Run recon-all (parallel)

Processes all `.nii` / `.nii.gz` files in the input directory:

```bash
python3 mri_scripts/recon-all.py --input nii/ --output fsout/ --cores 4
# Or in background:
nohup python3 mri_scripts/recon-all.py --input nii/ --output fsout/ --cores 2 &
```

Each NIfTI filename (without extension) is used as the subject ID. The `-hippocampal-subfields-T1` flag is included by default.

### 2. Extract statistics

Runs `asegstats2table`, `aparcstats2table`, and `quantifyHippocampalSubfields.sh` for all subjects, then exports cleaned CSV files:

```bash
python3 mri_scripts/stats.py -sd fsout/
```

Output is written to `./stats/csv/`.

### 3. Convert outputs for visualization

Converts `.mgz` volumes to NIfTI and surface files to GIFTI format:

```bash
python3 mri_scripts/mriWebConvert.py -i fsout/ -o websitefiles/
```

Converts per subject: `T1.mgz`, `brain.mgz`, `aparc+aseg.mgz`, `wm.mgz` → `.nii`; `lh/rh.pial`, `lh/rh.white` → `.gii`.

---

## Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| FreeSurfer | 6.0.0 | MRI cortical reconstruction |
| MATLAB Runtime | R2012b | Hippocampal subfield segmentation |
| Python | 3.x | Pipeline orchestration |
