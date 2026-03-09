# cate_freesurfer6

A Dockerized pipeline for FreeSurfer 6 MRI processing and PET SUVR analysis.

## Overview

This repository provides:

1. A Docker image with FreeSurfer 6, FSL, MATLAB Runtime (R2012b), and R pre-installed (about 24gb).
2. Scripts for running `recon-all` on T1 MRI data (in parallel), extracting cortical/subcortical statistics, and converting outputs for visualization.
3. Scripts for co-registering PET scans to MRI and computing SUVRs (Standardized Uptake Value Ratios) by brain region.
4. You will need to acquire a FreeSurfer license (free for academic use) and set it up in the container at /usr/local/freesurfer. This can be permanently done by copying the `license.txt` file into the Docker image (see Dockerfile) or by mounting a local directory containing the license at runtime.

---

## Repository Structure

```text
cate_freesurfer6/
├── Dockerfile                        # Docker image build file
├── fs_install_mcr.sh                 # Installs MATLAB Runtime (used in Docker build)
├── download.py                       # Downloads per-subject zip files from Dropbox CSV
├── dropbox_uf_import_mri.py          # Reorganizes downloaded MRI folders into nii/ for recon-all
├── dropbox_uf_import_pet.py          # Reorganizes downloaded PET folders into nii/ for SUVR
├── mri_scripts/                      # See mri_scripts/README.md
│   ├── recon-all.py
│   ├── mriWebConvert.py
│   ├── stats.py
│   ├── stats2tableV1.command
│   └── quantifyHippocampalSubfields.sh   # Collects hippocampal subfield volumes across subjects
└── suvr_scripts/                     # See suvr_scripts/README.md
    ├── mri_pet_process.sh
    ├── petSUVR.R
    ├── mergeTables.py
    ├── runin-maker.py
    ├── dicomconvert.sh
    ├── FreesurferLUTR.txt
    └── compoundLU.csv
```

---

## Docker Image

The image is based on `ubuntu:focal` and includes:

- FreeSurfer 6.0.0
- MATLAB Runtime R2012b (required for hippocampal subfield segmentation)
- FSL (latest installer)
- R with `oro.nifti` package

### Build

```bash
docker build -t brainprocessing .
```

### Run

```bash
docker run -it -v /path/to/data:/workspace/data brainprocessing
```

---

## Data Setup

Setting up data from Dropbox is a two-step process: download, then import/reorganize.

### Step 1: Download from Dropbox

Prepare a CSV with `name` and `link` columns. The `name` must match the raw subject folder naming from the source system — typically `<subjid>_<MMDDYYYY>` (scan date in month-day-year order):

```csv
name,link
<subjid0>_<scandate>,<dropbox_link>
<subjid1>_<scandate>,<dropbox_link>

i.e
name,link
123456_12252023,https://www.dropbox.com/s/abc123/123456_12252023.zip?dl=1
789012_01152024,https://www.dropbox.com/s/def456/789012_01152024.zip?dl=1
```

Run `download.py` separately for MRI and PET batches, giving each a distinct folder name:

```bash
python3 download.py mri_links.csv mri_batch48
python3 download.py pet_links.csv pet_batch48
```

Each zip is extracted to `<folder_name>/` and the zip is deleted. The raw layout after downloading:

```text
mri_batch48/
├── 123456_12252023/    # raw MRI files (T1, other modalities)
└── 789012_01152024/

pet_batch48/
├── 123456_12252023/    # raw PET files (3mmblur, 5mmblur, CT, etc.)
└── 789012_01152024/
```

### Step 2: Import and reorganize

Run the import scripts to rename subjects to the pipeline naming convention (`<src>-<prefix>-<id>-<YYYYMMDD>-<timestamp>`) and sort files into the directories expected by the pipelines.

**MRI** — finds the T1 (or `Cor_MPRAGE`) file per subject, copies it to `nii/`, and moves all other modalities to `mri_modalities/`:

```bash
# --dry-run first to preview changes
python3 dropbox_uf_import_mri.py mri_batch48/ MTS --dry-run
python3 dropbox_uf_import_mri.py mri_batch48/ MTS
```

**PET** — finds PET NIfTIs (3mmblur, 5mmblur, 6mmblur, 256) and CT, copying each to `nii/` or `ct/`:

```bash
python3 dropbox_uf_import_pet.py pet_batch48/ MTS --dry-run
python3 dropbox_uf_import_pet.py pet_batch48/ MTS
```

After importing, the layout is:

```text
mri_batch48/
├── nii/
│   ├── MTS-123-123456-20231225-20231225120000.nii       # T1 → input for recon-all
│   └── MTS-789-789012-20240115-20240115093000.nii
└── mri_modalities/
    └── MTS-123-123456-20231225-20231225120000/          # other modalities archived

pet_batch48/
├── nii/
│   ├── MTS-123-123456-20231225-20231225120000_PET_3mmblur.nii   # → input for SUVR
│   └── MTS-789-789012-20240115-20240115093000_PET_3mmblur.nii
└── ct/
    └── MTS-123-123456-20231225-20231225120000_PET_CT.nii
```

The `nii/` directories feed directly into the MRI and PET pipelines respectively. See the pipeline READMEs for next steps.

---

## Pipelines

- **MRI processing** — see [mri_scripts/README.md](mri_scripts/README.md)
- **PET SUVR analysis** — see [suvr_scripts/README.md](suvr_scripts/README.md)

---

## Dependencies

| Tool | Version | Purpose |
| --- | --- | --- |
| FreeSurfer | 6.0.0 | MRI cortical reconstruction |
| FSL | latest | PET-MRI registration (FLIRT) |
| MATLAB Runtime | R2012b | Hippocampal subfield segmentation |
| R (`oro.nifti`) | — | NIfTI I/O for PET SUVR computation |
| Python | 3.x | Pipeline orchestration scripts |
