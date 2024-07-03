 # data_processor.py

## ClassDef DataProcessor

The function of the class is to provide methods for processing data and checking the validity of email addresses.

**Attributes**:

None

**Functions**:

- `process_data` (`self`, `data`) -> `list`
    - Parameters:
        - `self`: The instance of the class.
        - `data`: A list of items to be processed. (type: list)
    - Returns:
        - A list of uppercase strings from the input data.

**Code Description**: This method processes a given list of data by converting each item to its uppercase equivalent.

**Note**: The return value is a list of strings in uppercase.

**Input Example**:

```
Input: ["hello", "world"]
Output: ["HELLO", "WORLD"]
```

- `check_emails` (`self`, `emails`) -> `list`
    - Parameters:
        - `self`: The instance of the class.
        - `emails`: A list of email addresses to be validated. (type: list)
    - Returns:
        - A list indicating whether each email address is valid or not.

**Code Description**: This method uses a regular expression pattern to validate each email address in the input list, returning a corresponding boolean value for each one.

**Note**: The return value is a list of booleans where True indicates a valid email and False otherwise.

**Input Example**:

```
Input: ["test@example.com", "invalid"]
Output: [True, False]
```

**Called_functions**:

- `utils::validate_email` (`email`) -> `boolean`: This function validates an email address using a regular expression pattern. If the email matches the pattern, it returns True; otherwise, it returns False.
