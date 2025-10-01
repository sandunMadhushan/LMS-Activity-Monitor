# Tests

This folder contains test scripts for the LMS Scraper system.

## Available Tests

### `test_setup.py`
Tests the system setup and configuration:
- Checks if all environment variables are configured
- Verifies Chrome installation
- Tests Python dependencies
- Validates database connection

Run with:
```bash
python tests/test_setup.py
```

### `test_course_names.py`
Tests course scraping functionality:
- Tests OUSL course scraping
- Tests RUSL course scraping
- Validates course name extraction
- Checks activity detection

Run with:
```bash
python tests/test_course_names.py
```

## Running All Tests

To run all tests:
```bash
python tests/test_setup.py
python tests/test_course_names.py
```

## Notes

- Tests may take several minutes as they perform actual scraping
- Make sure your `.env` file is properly configured before running tests
- Tests will create/modify the database, so back up your data if needed
