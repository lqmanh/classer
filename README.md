# classer
> 'classify' in French

Organize a directory by classifying files into different places.


## USAGE
Use `--help` for more detail information.

```
$ classer --help
Usage: classer [OPTIONS] COMMAND [ARGS]...

  Organize a directory by classifying files into different places.

Options:
  --help  Show this message and exit.

Commands:
  auto    Automatically classify files based on a...
  manuel  Manually classify files.
```

```
$ classer manuel --help
Usage: classer manuel [OPTIONS] [EXPRS]... SRC DST

  Manually classify files.

Options:
  -c, --autoclean                 Automatically remove empty directories.
  -r, --recursive / -R, --no-recursive
                                  Recursively/No-recursively scan directories.
  --since TEXT                    Oldest modification time.
  --until TEXT                    Latest modification time.
  --larger INTEGER                Minimum size in bytes.
  --smaller INTEGER               Maximum size in bytes.
  -x, --exclude TEXT              Glob pattern to exclude directories.
  --ask                           Ask for action on duplicate.
  --rename                        Always rename on duplicate.
  --overwrite                     Always overwrite on duplicate.
  --ignore                        Always ignore on duplicate.
  --help                          Show this message and exit.
```

- `EXPRS` -- One or more *glob* pattern as a file filter.
- `SRC` -- Top directory to start classifying files.
- `DST` -- Destination directory to save filtered files.

***Examples:***
```
$ cd ~/Downloads
$ classer manuel -c -x NO_TOUCH -x .ignore '*.py' '*.pyc' . ./Python
```

```
$ classer auto --help
Usage: classer auto [OPTIONS] PATH

  Automatically classify files based on a criteria file.

Options:
  --help  Show this message and exit.
```

- `PATH` -- Path to a criteria file.

***Examples:***
```
$ classer auto ~/.config/my_criteria.json
```


## NOTES

- Always put quote marks around `EXPRS` so as not to confligs with the system.
- Criteria file is in *json* format. You can use a clone of the example file in
`classer/config/criteria.json`.
- Because *click* does not support options with infinite values like arguments,
you must explicitly add as many `-x`/`--exclude` as you need like in the example above.


## INSTALLATION
```
$ cd classer
$ pip install -r requirements.txt
$ pip install .
```
