# Selection and Mechanism of Foam Stabilizers in Alkali-Activated Slag Foam Concrete
Simple, transparent Python implementation of **TOPSIS** using **pure entropy-based objective weights** (no subjective weighting, no AHP-style multipliers).

**Designed exclusively** for ranking concrete mix designs presented in the paper  
**Selection and Mechanism of Foam Stabilizers in Alkali-Activated Slag Foam Concrete**  
(or whichever exact title/reference your work uses)

**Not intended** for general-purpose MCDM, other datasets, or unrelated research questions.  
No support provided. No responsibility taken for misuse or adaptation.

## Features

- Vector (L2/unit) normalization  
- Objective entropy weights (data-driven, from vector-normalized matrix)  
- Classical TOPSIS (Euclidean distances to PIS/NIS)  
- Closeness coefficient ranking  
- All output duplicated to console + log file  
- Basic input validation & clear error messages  
- Verbose step-by-step output for auditing

## Requirements

```bash
pip install numpy pandas
```

## Usage

Run the script from the command line.

```bash
python topsis.py --file <path> --benefits <flags>
```

### Command-line arguments

| Argument Name       | Required | Type    | Default | Description                                                                                  |
|--------------|----------|---------|---------|----------------------------------------------------------------------------------------------|
| `--file`     | yes      | string  | —       | Path to input CSV file (relative or absolute). Must exist and be readable.                   |
| `--benefits` | yes      | string  | —       | Comma-separated list of benefit flags (`True`/`False`). Order must match CSV criteria columns (excluding name column). Example: `False,True,False` |

### Examples

**1200 kg/m³ dataset**

```bash
python topsis.py \
  --file "concrete 1200.csv" \
  --benefits "False,True,False"
```

**700 kg/m³ dataset**

```bash
python topsis.py \
  --file "concrete 700.csv" \
  --benefits "False,True,False"
```

### Expected input CSV format

- **Delimiter**: comma (standard CSV)
- **Header row**: present
- **Columns** (in exact order):
  1. Mix name / description (string) – used only for display
  2. Density (kg/m³) – numeric
  3. Average compressive strength σ (MPa) – numeric
  4. Average thermal conductivity (mW/(m·K)) – numeric
- All numeric columns must contain **non-negative values** (entropy method requirement)

### Output files

For each run, a log file is created in the **same directory** as the script:

- `<input_filename_without_extension>_topsis.log`  
  Examples:  
  `concrete 1200_topsis.log`  
  `concrete 700_topsis.log`

The log file contains **exactly the same content** as printed to the terminal (including any error tracebacks).

## Important notes

- **Non-negative values required** in all numeric columns (entropy weights will be meaningless or crash otherwise)
- Number of `--benefits` flags **must exactly match** number of criteria columns (excluding name)
- Script assumes exactly 3 criteria in the order shown above (paper-specific)

## Already handled edge cases

| Issue                              | Handling in code                                      |
|------------------------------------|-------------------------------------------------------|
| Input file does not exist          | Early exit with clear error message                   |
| Wrong number of benefit flags      | ValueError + shows both lists                         |
| Zero-norm column (all zeros)       | Norm set to 1 → safe division                         |
| Zero in entropy proportions        | Column receives zero weight                           |
| All criteria identical             | Falls back to equal weights                           |
| Log file cannot be created         | Error message + exit                                  |
| Any runtime exception              | Full traceback to console **and** log file            |

## Citations / References

Classical TOPSIS:

- Hwang, C. L., & Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*. Springer-Verlag.
- Hwang, C. L., & Yoon, K. (1981). *Multiple attribute decision making – methods and applications: a state-of-the-art survey*. Lecture Notes in Economics and Mathematical Systems, 186. Springer.

Modern reviews:

- Behzadian, M., Otaghsara, S. K., Yazdani, M., & Ignatius, J. (2012). A state-of the-art survey of TOPSIS applications. *Expert Systems with Applications*, 39(17), 13051–13069. https://doi.org/10.1016/j.eswa.2012.05.056
- Zavadskas, E. K., Turskis, Z., & Kildienė, S. (2014). State of art surveys of overviews on MCDM/MADM methods. *Technological and Economic Development of Economy*, 20(1), 165–179. https://doi.org/10.3846/20294913.2014.892037
- Tzeng, G.-H., & Huang, J.-J. (2011). *Multiple Attribute Decision Making: Methods and Applications*. CRC Press.

Cite at minimum Hwang & Yoon (1981) when publishing results obtained with this code.

## License

MIT License

Copyright (c) 2025 Ms. Joelle Wong

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.

---

Use at your own risk.  
Research-specific tool — not a general-purpose library.

Good luck with your foam concrete optimisation.
