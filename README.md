# classer
> 'classify' in French

Organize a directory by classifying files into different places.

## USAGE
```
Usage: classer [OPTIONS] EXPR SRC DST

Options:
  -c, --autoclean                 Automatically remove empty directories.
  -r, --recursive / -R, --no-recursive
                                  Recursively/No-recursively scan directories.
  --since TEXT                    Oldest modification time.
  --until TEXT                    Latest modification time.
  --help                          Show this message and exit.
```

- `EXPR` -- Expression using a *glob* pattern as filter.
- `SRC` -- Top directory to start classifying files.
- `DST` -- Destination directory to save filtered files.

***Examples:***
```
$ cd Downloads
$ classer -c --since 2017-01-01 '*.pyc?' . ./PythonScripts
```

***Notes:***

- Remember to put quote marks around `EXPR` so as not to confligs with the system.

## INSTALLATION
```
$ cd classer
$ pip install -r requirements.txt
$ pip install .
```
