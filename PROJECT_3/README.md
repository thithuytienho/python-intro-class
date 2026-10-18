# Healthcare Dataset Cleaning and Encryption

A Python command-line utility for cleaning `healthcare_dataset.csv`, calculating descriptive statistics, pseudonymizing patient names, and encrypting the cleaned patient-level data with Fernet symmetric encryption.

## Features

* **Data cleaning with pandas**

  * Trims whitespace from text fields and treats empty strings as missing.
  * Converts age, billing amount, and room number to numeric types.
  * Marks ages outside `0–120`, negative/non-finite billing amounts, and invalid room numbers as missing.
  * Parses admission and discharge dates; unparseable dates become missing.
  * If a discharge date precedes its admission date, sets the discharge date to missing.
  * Removes exact duplicate rows after basic normalization.
  * Normalizes capitalization in selected categorical columns.
* **Descriptive statistics with NumPy**

  * Summarizes age, billing amount, and length of stay with count, mean, median, population standard deviation, minimum, maximum, and quartiles.
  * Reports counts for selected categorical variables.
  * Records cleaning metrics and missing-value counts.
* **Patient-name pseudonymization**

  * Replaces the `Name` column with a keyed, HMAC-derived `Patient_ID`.
  * Uses the Fernet key material for HMAC-based IDs.
* **Symmetric encryption**

  * Encrypts the complete cleaned, pseudonymized patient-level CSV with Fernet.
  * Does not write a plaintext patient-level CSV to disk.
  * Writes aggregate statistics to a separate JSON file.

> \*\*Privacy note:\*\* Pseudonymization is not the same as anonymization. Other fields—such as dates, hospitals, clinicians, diagnoses, and room numbers—may still identify a person. Treat the encrypted data, encryption key, and potentially the statistics as sensitive information.

## Requirements

* Python 3.10 or newer is recommended.
* `pandas`
* `numpy`
* `cryptography`

Install dependencies:

```bash
python -m pip install pandas numpy cryptography
```

## Expected input

By default, the script expects a file named `healthcare_dataset.csv` in the current working directory. The input CSV must contain these columns:

```text
Name
Age
Gender
Blood Type
Medical Condition
Date of Admission
Doctor
Hospital
Insurance Provider
Billing Amount
Room Number
Admission Type
Discharge Date
Medication
Test Results
```

Column-header whitespace is trimmed, but the column names otherwise need to match. Extra columns are retained in the cleaned data. The script removes `Name` only after generating `Patient_ID`.

## Usage

Run with the default input and output paths:

```bash
python clean_encrypt_healthcare.py
```

Specify the input file and output directory:

```bash
python clean_encrypt_healthcare.py \\
  --input healthcare_dataset.csv \\
  --outdir secure_output
```

Specify a key file stored outside the output directory:

```bash
python clean_encrypt_healthcare.py \\
  --input healthcare_dataset.csv \\
  --outdir secure_output \\
  --key-file /secure/location/healthcare_fernet.key
```

On Windows PowerShell, the same command can be entered on one line:

```powershell
python clean_encrypt_healthcare.py --input healthcare_dataset.csv --outdir secure_output
```

## Output files

A successful run creates the output directory and writes:

|File|Contents|
|-|-|
|`patient_data.csv.fernet`|Fernet-encrypted CSV containing all retained patient records and all input columns except `Name`, which is replaced by `Patient_ID`.|
|`summary_statistics.json`|Aggregate descriptive statistics, cleaning counts, and missing-value counts.|
|`fernet.key`|Fernet secret key, created if the specified key file does not already exist.|

The key file is only placed inside `secure_output/` when `--key-file` is not supplied. If a key file already exists, the script uses it instead of overwriting it.

## What the cleaning rules mean

* **Invalid values are not automatically imputed.** They are converted to missing values (`NaN`/`NaT`) and reflected in the missing-value counts.
* **Age:** values outside `0–120` are marked missing; remaining values are rounded to whole years.
* **Billing amount:** negative or non-finite values are marked missing.
* **Room number:** negative or fractional values are marked missing.
* **Dates:** unparseable dates become missing. A discharge date earlier than admission is marked missing.
* **Duplicates:** only exact duplicate rows after whitespace normalization are removed. Similar-looking records are not assumed to be duplicates.
* **Categorical values:** selected categories are converted to title case. Review this behavior if capitalization carries meaning in your source data.

The script does not infer missing clinical values, validate diagnoses, or establish that records are clinically accurate.

## Statistics

`summary_statistics.json` includes:

* Original and retained row counts
* Number of exact duplicate rows removed
* Counts of selected invalid values
* Missing values per column
* Numeric summaries for age and billing amount
* Numeric summaries of length of stay, calculated from records with valid admission and discharge dates
* Frequency counts for gender, blood type, medical condition, insurance provider, admission type, medication, and test results

The standard deviation is calculated as a **population standard deviation** (`numpy.std` with `ddof=0`). Statistics are computed from the cleaned data before the `Name` column is removed.

## Decrypting the dataset

Only decrypt the file in an access-controlled environment. The key used for encryption must be available. Do not print decrypted records to shared logs or notebooks.

```python
from pathlib import Path
from cryptography.fernet import Fernet
import pandas as pd
from io import BytesIO

key = Path("secure_output/fernet.key").read_bytes().strip()
encrypted = Path("secure_output/patient_data.csv.fernet").read_bytes()

plaintext_csv = Fernet(key).decrypt(encrypted)
df = pd.read_csv(BytesIO(plaintext_csv))

print(df.shape)
print(df.columns.tolist())
```

This example loads the decrypted data into memory. Avoid writing the plaintext CSV to disk unless necessary and approved for your environment.

## Security and operational considerations

1. **Protect the key.** Anyone who obtains it can decrypt the dataset. Store it separately from the encrypted data, restrict access, and maintain a secure backup.
2. **Do not commit secrets.** Keep the key and patient data out of source control, public repositories, shared logs, and unapproved cloud storage. Add the output directory and key file to `.gitignore` where appropriate.
3. **Key loss is permanent data loss.** If the key is lost, Fernet-encrypted data cannot be recovered.
4. **Back up securely.** Back up the key and encrypted data under your organization's approved procedures, ideally with separate access controls.
5. **Pseudonymous IDs are not universal patient identifiers.** The current ID-generation method includes each row's position and name. IDs can change if row order changes, and records with the same name can receive different IDs. Do not use these IDs to link records across independently reordered files.
6. **Review access to statistics.** Aggregate counts can still expose sensitive information, especially for small groups or rare conditions.
7. **Check institutional requirements.** For real patient data, follow applicable privacy laws, IRB/ethics approvals, data-use agreements, and institutional security policies.

Fernet provides authenticated symmetric encryption. In the current implementation, the key is stored with restrictive file permissions on systems that support them, but filesystem permissions alone are not a complete security boundary. Consider using an approved secrets manager or key-management system for production workflows.

## Troubleshooting

* **Missing required columns:** Check spelling and column names in the input CSV.
* **Module not found:** Install dependencies in the same Python environment used to run the script.
* **Invalid Fernet key:** Verify that the key file is intact and is the same key used to encrypt the data.
* **Decryption fails:** Confirm the file has not been corrupted and that the correct key is being used.
* **Unexpected missing values:** Inspect the source values and the cleaning rules above; invalid or unparseable values are intentionally marked missing.

## License and intended use

No license is specified by this script. Confirm the appropriate license before redistributing it. This utility is a data-processing example, not a substitute for a formal privacy, security, or clinical-data validation review.

