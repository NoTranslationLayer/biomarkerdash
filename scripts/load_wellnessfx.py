#!/usr/bin/env python3

import pandas as pd
import sys
import biomarkerdash.utils as util
import biomarkerdash.biomarker as bm
from typing import List, Dict, Optional, Tuple


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 load_wellnessfx.py path_to_csv_file")
        sys.exit(1)

    csv_path: str = sys.argv[1]
    biomarkers = util.load_wellnessfx_biomarkers(csv_path)
