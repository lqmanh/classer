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
`~$ classer manuel -c '*.docx' '*.epub' Downloads Downloads/Documents`

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
`classer$ classer auto ./config/criteria.json`

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


### NOTES
- In command-line mode (aka `manuel` subcommand), always put quote marks around `EXPRS`
so as not to confligs with the system.
- Criteria files are in *json* format. It is advisable to use a clone of the file in
`classer/config/criteria.json`.
- Because *click* does not support options with infinite values like arguments, you
must explicitly add as many `-x`/`--exclude` as you need.
*eg:* `classer manuel -x NO_TOUCH -x .ignore '*.txt' . .`


### INSTALLATION
***Compatible with Python >=3.6***

```
$ git clone https://github.com/lqmanh/classer.git
$ cd classer
$ pip install -r requirements.txt
$ pip install .
```
