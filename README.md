# classer
> 'classify' in French

Organize a directory by classifying files into different places.

## USAGE
Use `--help` for more detail information.

```
$ classer --help
Usage: classer [OPTIONS] [EXPRS]... SRC DST COMMAND [ARGS]...

  Organize a directory by classifying files into different places.

Options:
  -c, --autoclean                 Automatically remove empty directories.
  -r, --recursive / -R, --no-recursive
                                  Recursively/No-recursively scan directories.
  --since TEXT                    Oldest modification time.
  --until TEXT                    Latest modification time.
  --larger INTEGER                Minimum size in bytes.
  --smaller INTEGER               Maximum size in bytes.
  -x, --exclude TEXT              Glob pattern to exclude directories.
  --help                          Show this message and exit.

Commands:
  auto  Automatically classify files based on a...
```

- `EXPRS` -- One or more *glob* pattern as a file filter.
- `SRC` -- Top directory to start classifying files.
- `DST` -- Destination directory to save filtered files.

***Examples:***
```
$ cd Downloads
$ classer -c --since 2017-01-01 -x NOT_TOUCH -x .ignore '*.py' '*.pyc' . ./PythonScripts
```

***Notes:***

- Remember to put quote marks around `EXPRS` so as not to confligs with the system.

## INSTALLATION
```
$ cd classer
$ pip install -r requirements.txt
$ pip install .
```
