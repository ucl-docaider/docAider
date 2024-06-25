# utils.py

## FunctionDef validate_email

The function of the function is to validate email addresses using regular expressions.

**Parameters**:

- `email` (`str`): The email address to be validated.

**Returns**:

- `bool`: Returns True if the email address is valid, False otherwise.

**Code Description**: This function uses a regular expression pattern to match the given email address. If the pattern matches, the function returns True, indicating that the email address is valid. Otherwise, it returns False.

**Note**: When using this function, ensure that the input email addresses conform to the expected format to avoid false positives or negatives.

**Input Example**: 

```
email = "test@example.com"
if validate_email(email):
    print("Email is valid")
else:
    print("Email is not valid")
```

**Output Example**:

```
If the input email address is "test@example.com", the output will be "Email is valid". If the input email address is invalid, the output will be "Email is not valid".
```