 # user.py

## ClassDef User

The function of the User class is to create user objects with unique IDs, names, and emails.

**Attributes**:

- `id` (`uuid.uuid4`): A unique identifier for each user generated using the uuid library.
- `name` (`str`): The name of the user.
- `email` (`str`): The email address of the user.

**Functions**:

- `__init__`(self, name: str, email: str) -> None
    - Parameters:
        - self (User): A reference to the current User object.
        - `name` (str): The name of the user.
        - `email` (str): The email address of the user.
    - Returns:
        - None: Initializes a new User object with provided name and email.

- `__str__(self) -> str`
    - Parameters:
        - self (User): A reference to the current User object.
    - Returns:
        - `str`: A string representation of the User object, including its ID, name, and email.

- `update_email`(self, new_email: str)
    - Parameters:
        - self (User): A reference to the current User object.
        - `new_email` (str): The new email address for the user.
    - Returns:
        - None: Updates the email address of the user.

**Code Description**: 
The User class uses the uuid library to generate unique IDs for each user. The `__init__` method initializes a new User object with provided name and email, while the `__str__` method provides a string representation of the User object. The `update_email` method allows updating the email address of a user.

**Note**: 
When using the User class, note that the ID is generated uniquely for each user and cannot be changed. Also, when calling the `update_email` method, ensure to provide a valid new email address.

**Input Example**: 

No specific input example is required as this is a class definition.

**Output Example**: 
```
User [ID: 123e4567-e89b-12d3-a456-426655440000, Name: John Doe, Email: johndoe@example.com]
```

This output shows the string representation of a User object with its unique ID, name, and email.
