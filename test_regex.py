import re

# Test text that simulates a document with eligibility and benefits sections
test_text = """
In Network Coverage Frequency
Exam Available
Frame Available
Lenses Available

In Network Coverage
Exam $10.00
Frame $50.00
Polycarbonate Lenses $33.00 for Ages 19+
Polycarbonate Lenses Covered-in-Full for Ages 0-18
"""

# Test the eligibility section regex
eligibility_pattern = re.compile(
    r"(In\s+Network\s+Coverage\s+Frequency\s*\n)(.*?)(?=\s*In\s+Network\s+Coverage\s*\n|\Z)", 
    re.IGNORECASE | re.DOTALL
)
eligibility_match = eligibility_pattern.search(test_text)

if eligibility_match:
    print("Eligibility section regex PASSED")
    print("Extracted content:")
    print(eligibility_match.group(2))
else:
    print("Eligibility section regex FAILED")

# Test the benefit row regex
row_patterns = ["Exam", "Frame", "Polycarbonate Lenses"]

for pattern in row_patterns:
    combined_pattern = rf"({pattern})[:\s\.]+([^\n]+)"
    match = re.search(combined_pattern, test_text, re.IGNORECASE)
    if match:
        print(f"\nRow pattern '{pattern}' PASSED")
        print(f"Service: {match.group(1)}")
        print(f"Value: {match.group(2)}")
    else:
        print(f"\nRow pattern '{pattern}' FAILED")

# Test for polycarbonate with age patterns
poly_child_pattern = r"(Polycarbonate Lenses).*?((?:Covered|Covered-in-Full).*?for Ages 0-18)"
poly_adult_pattern = r"(Polycarbonate Lenses).*?(\$\d+\.\d+.*?for Ages 19\+)"

poly_child_match = re.search(poly_child_pattern, test_text, re.IGNORECASE)
if poly_child_match:
    print(f"\nPolycarbonate child pattern PASSED")
    print(f"Service: {poly_child_match.group(1)}")
    print(f"Value: {poly_child_match.group(2)}")
else:
    print(f"\nPolycarbonate child pattern FAILED")

poly_adult_match = re.search(poly_adult_pattern, test_text, re.IGNORECASE)
if poly_adult_match:
    print(f"\nPolycarbonate adult pattern PASSED")
    print(f"Service: {poly_adult_match.group(1)}")
    print(f"Value: {poly_adult_match.group(2)}")
else:
    print(f"\nPolycarbonate adult pattern FAILED") 