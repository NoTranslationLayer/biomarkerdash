# filename: test_parse_reference_range.py
# Unit tests for parsing reference range values

# Copyright (c) 2023, No Translation Layer LLC
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import pandas as pd
import unittest
import biomarkerdash.utils as util


class TestParseReferenceRange(unittest.TestCase):
    def test_nan(self):
        self.assertEqual(util.parse_ref_range("nan"), (None, None))
        self.assertEqual(util.parse_ref_range("NAN"), (None, None))
        self.assertEqual(util.parse_ref_range("NaN"), (None, None))

    def test_zero(self):
        self.assertEqual(util.parse_ref_range("0"), (0.0, 0.0))

    def test_less_than_format(self):
        self.assertEqual(util.parse_ref_range("<5.7"), (None, 5.7))
        self.assertEqual(util.parse_ref_range("<130"), (None, 130.0))

    def test_greater_than_format(self):
        self.assertEqual(util.parse_ref_range(">5.7"), (5.7, None))
        self.assertEqual(util.parse_ref_range(">130"), (130.0, None))

    def test_or_equal_format(self):
        self.assertEqual(util.parse_ref_range("> OR = 60"), (60.0, None))
        self.assertEqual(util.parse_ref_range(">=125"), (125.0, None))
        self.assertEqual(util.parse_ref_range("< OR = 80"), (None, 80.0))

    def test_or_less_format(self):
        self.assertEqual(util.parse_ref_range("0.2 OR LESS"), (None, 0.2))

    def test_standard_format(self):
        self.assertEqual(util.parse_ref_range("3.5-5.3"), (3.5, 5.3))
        self.assertEqual(util.parse_ref_range("135-146"), (135.0, 146.0))

    def test_special_format(self):
        self.assertEqual(util.parse_ref_range("-2.0 - +2.0"), (-2.0, 2.0))

    def test_fail_format(self):
        self.assertEqual(util.parse_ref_range("unparsable"), (None, None))
        self.assertEqual(util.parse_ref_range(""), (None, None))


class TestParseWellnessFxRefRanges(unittest.TestCase):
    def setUp(self):
        # This method will be called before each test in this test class

        self.data_standard_format = pd.DataFrame(
            {
                "Marker Name": ["Test1", "Test2", "Test3"],
                "Draw Date": ["10/25/13", "10/25/13", "10/25/13"],
                "Reference Range": ["0.2-5.0", "<150", ">60"],
                "Units": ["mg/dL", "mmol/L", "mg/dL"],
            }
        )

        self.data_error_format = pd.DataFrame(
            {
                "Marker Name": ["TestError1", "TestError2"],
                "Draw Date": ["10/25/13", "10/25/13"],
                "Reference Range": ["nan", "unexpected-format"],
                "Units": ["mg/dL", "mmol/L"],
            }
        )

        self.expected_standard_format = {
            "Test1": (0.2, 5.0),
            "Test2": (None, 150.0),
            "Test3": (60.0, None),
        }

        self.data_correction_needed = pd.DataFrame(
            {
                "Marker Name": [
                    "Lymphocyte Count (absolute)",
                    "Monocytes (absolute)",
                    "Neutrophil Count (ANC)",
                    "Basophil (absolute)",
                    "Eosinophil (absolute)",
                    "Platelet Count",
                ],
                "Draw Date": ["10/25/13"] * 6,
                "Reference Range": [
                    "850.0-3900.0",
                    "200.0-950.0",
                    "1500.0-7800.0",
                    "0.0-200.0",
                    "15.0-500.0",
                    "140-400",
                ],
                "Units": ["x10E3/μL"] * 6,
            }
        )

        self.expected_correction_needed = {
            "Lymphocyte Count (absolute)": (0.85, 3.9),
            "Monocytes (absolute)": (0.2, 0.95),
            "Neutrophil Count (ANC)": (1.5, 7.8),
            "Basophil (absolute)": (0.0, 0.2),
            "Eosinophil (absolute)": (0.015, 0.5),
            "Platelet Count": (140, 400),  # Ensure it's not scaled
        }

    def test_standard_format(self):
        # Testing the function with standard reference range formats
        result = util.parse_wellnessfx_ref_ranges(self.data_standard_format)
        self.assertEqual(result, self.expected_standard_format)

    def test_error_format(self):
        # Testing the function with non-standard reference range formats
        # It should print error messages, but we're not capturing stdout here.
        # Just testing if the function can handle these inputs without crashing.
        result = util.parse_wellnessfx_ref_ranges(self.data_error_format)
        self.assertTrue("TestError1" not in result)
        self.assertTrue("TestError2" not in result)

    def test_correction_needed(self):
        # Testing the function for correcting reference ranges for blood cell
        # counts
        result = util.parse_wellnessfx_ref_ranges(self.data_correction_needed)
        self.assertEqual(result, self.expected_correction_needed)


if __name__ == "__main__":
    unittest.main()
