Running the Application
Start the banking system by running main function:
python main.py
You'll see the main menu:

Welcome to AwesomeGIC Bank! What would you like to do?
[T] Input transactions
[I] Define interest rules
[P] Print statement
[Q] Quit
>
Testing the System
Run all unit tests:
python -m unittest discover -s tests

Run specific test groups:
# Unit tests only
python -m unittest discover -s tests/unit

# Integration tests only
python -m unittest discover -s tests/integration

# With verbose output
python -m unittest discover -s tests -v