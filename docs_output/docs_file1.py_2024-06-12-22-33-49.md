**Project Name: Policy Search Management**

**Description**
The project is designed to manage policy searches, providing a view for users to access and analyze their search results. This view displays information on the searches performed by each user, including grouped data by country and policy.

**Classes and Functions**

### manage_searches_view(request)

* **Attributes**: None
* **Functions**
	+ Called functions:
		- PolicySearch.objects.filter(account=request.user).order_by('-created_at'): Retrieves search results for the authenticated user.
		- parse_content(row['Content']): Parses the content of a file to extract relevant information and sources.
		- static(file_path_excel): Returns a URL path for an Excel file based on the request user's ID.

### parse_content(content)

* **Parameters**: content (str)
* **Returns**: A list of entries, each containing information about a source
* **Called functions**:
	+ re.compile(): Compiles a regular expression pattern to match INFORMATION and SOURCE lines in a file.
	+ re.findall(pattern, content): Finds all matches for the pattern in the given content.
	+ urlparse(source_url): Parses a URL to extract its scheme and netloc (domain).
	+ uuid.uuid4(): Generates a universally unique identifier.

This view is responsible for rendering the "manage_searches.html" template with the search results data. The data includes information on each search, grouped by country and policy.