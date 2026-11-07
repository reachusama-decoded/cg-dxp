# Airflow Plugins

Use this directory for custom Airflow extensions. The assigned v2 DAGs do not require a new plugin.

## What belongs here

- Custom Operators, Hooks, Sensors, and Timetables
- Flask AppBuilder view/menu extensions
- Macros and other reusable plugin-level utilities
- Lightweight helper modules shared by plugin classes

## Suggested structure

Keep plugins grouped by domain so they stay easy to discover and test.

```text
plugins/
	my_domain/
		operators/
			my_operator.py
		hooks/
			my_hook.py
		__init__.py
	my_plugin.py
```

## Development guidelines

- Keep business logic in importable modules and keep plugin registration files thin.
- Prefer explicit imports and avoid heavy side effects at import time.
- Add unit tests for non-trivial plugin behavior.
- Document required Airflow Connections, Variables, and external dependencies in the relevant module docstring.

## Local validation

After adding or updating plugin code:

- Run tests from the `data_products/` folder in a vended repo.
- Start the local Airflow environment and confirm the plugin loads without import errors.
- Verify UI extensions in the supplied runtime, where supported.
