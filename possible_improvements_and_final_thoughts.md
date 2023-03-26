# Possible improvements
* The CLI retrieves the metadata for a given `entity`, and then filters the file urls for a given `form`, and the then the metadata is not used anymore. On a second command, with a different `form` the whole metadata is retrieved again. A way to improve this workflow is to store the metadata either on a database, or a file.


* The CLI bypasses the SEC limit of 10 requests / second per user, by generating users just in time. However, the best way to truly scale the CLI would be to register our company with the SEC, so we can have a higher limit, or unlimited requests per unit of time.


* The CLI stores the files locally. However, a better solution is to store the files in the cloud, such as an s3 bucket (AWS), and retrieve it when needed.


* The CLI only allows one SEC form type per command. A way to extend the functionality by allowing several forms without diminishing readability and maintainability is to leave the CLI as it is and create a separate script that calls several commands (one per form), and execute that script. The CLI would have to be modified to avoid calling the commands with the current just in time generated users (instead of adding integers to the email, a randomly generated string could be added).


* The current solution does not have unit tests. A way to approach creating a test suite for the CLI is to do the following:
  * Move `click.ClickException` in `main.py` to the classes, so the logic can be tested
  * Mock the methods that make requests to ensure independence, and speed.
  * Store and modify a copy of the one of the company's metadata to mock the response of a request, and use its content to test the parts of the code that come after the request call.
  * Generate SetUp and TearDown methods that handle all the directory creations and file dumps, deleting all the generated directories and files after the tests are done (by means of using a context manager, so the files are deleted even if the tests are not successful).


* The `Base` class currently contains several things all put together. It is reasonable for the current solution due to the size of the project, but if it were to be expanded, the variables within the class should be moved into a config file.


* The classes have all been put into one file due to the size of the project, but if it were to be expanded, a better project file system should be developed, putting each class in a separate file (with the exception of `Entity` and `Filing`, that could go in the same file).
