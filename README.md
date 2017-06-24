# classer
> 'classify' in French

Organize a directory by classifying files into different places.


### USAGE
*Example directory:*
```
Downloads
├── a_document.docx
├── a_draft.txt
├── a_picture.jpg
├── a_song.mp3
├── a_video.mp4
├── mydocs
│   ├── a_book.epub
│   └── a_document.docx
└── mypodcasts
    └── a_podcast.wav
```

##### USING `MANUEL`
```
$ classer manuel -c '*.docx' '*.epub' Downloads Downloads/Documents
```

```
Downloads
├── a_draft.txt
├── a_picture.jpg
├── a_song.mp3
├── a_video.mp4
├── mypodcasts
│   └── a_podcast.wav
└── Documents
    ├── a_book.epub
    ├── a_document (2).docx
    └── a_document.docx
```

##### USING `AUTO`
```
$ classer auto classer/config/sample_criteria.json
```

```
Downloads
├── Documents
│   ├── a_book.epub
│   ├── a_document (2).docx
│   ├── a_document.docx
│   └── a_draft.txt
├── Music
│   └── a_song.mp3
├── mypodcasts
│   └── a_podcast.wav
├── Pictures
│   └── a_picture.jpg
└── Videos
    └── a_video.mp4
```

##### USING `UNDO`
```
$ classer auto classer/config/sample_criteria.json
$ classer undo --autoclean
```

```
Downloads
├── a_document.docx
├── a_draft.txt
├── a_picture.jpg
├── a_song.mp3
├── a_video.mp4
├── mydocs
│   ├── a_book.epub
│   └── a_document.docx
└── mypodcasts
    └── a_podcast.wav
```


### NOTES
- Use `--help` option for more further information.
- To work with history, use `histoire` command.
- In command-line mode aka `manuel` command, *ALWAYS* put quote marks around `EXPRS` so as not to confligs with the os.
- Criteria files are in *json* format. Check out the sample file in `config/sample_criteria.json`.
- Because *click* does not support options with infinite values like arguments, you must explicitly add as many `-x`/`--exclude` as you need.
*eg:* `classer manuel -x NO_TOUCH -x .ignore '*.txt' . .`


### INSTALLATION
***Compatible with Python >=3.6***

```
$ git clone https://github.com/lqmanh/classer.git
$ cd classer
$ pip install -r requirements.txt
$ pip install .
```
