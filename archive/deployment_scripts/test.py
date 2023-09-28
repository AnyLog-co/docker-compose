import re

# List of words
word_list = ["hour", "day", "month"]

# Create a pattern by joining the words with | for alternation
pattern = r"\b(" + "|".join([word + "s?" for word in word_list]) + r")\b"

# Test string
test_string = "There are 2 hours, 1 day, and 3 months in a year."

# Find all matches in the test string
output = re.search(pattern, test_string)


# Print the matches
# print(matches)
