# Youtube LID Data

Scripts for collecting audio data from Youtube for building language identification models.


## 🛠 Setup

### 📃 Requirements

* Python 3.7
* `Wikiextractor.py` (dowload from https://github.com/attardi/wikiextractor)

Install the other required packages with pip.

```bash
pip install -r requirements.txt
```

Make the scripts executable

```
chmod +x *.py *.sh
```

## 💻 Usage

### Step 1 - Wikipedia dumps

Download Wikipedia dumps, that can be used to generate search phrases for Youtube. Edit the file `download_extract_wikis.sh` and set correct values in the config section (choose dumps url, which dumps to download, output path and dumps date). Then run the script.

```bash
./download_extract_wikis.sh
```

### Step 2 - Search phrases

Using the extracted Wikipeadia dumps generate search phrases. For example:

```bash
./generate_search_phrases.py -i ./INPUT_FOLDER -o ./OUTPUT_FOLDER --phrase-length 3 --document-limit 10000 --document-top-phrases 5
```

### Step 3 - Youtube links

Using the generated search phrases query Youtube and try to get required video ids.

```bash
./get_youtube_videolinks.py -i ./INPUT_FOLDER -o ./OUTPUT_FOLDER --max-videos 5000 --videos-per-phrase 5
```

### Step 4 - Youtube downloads

Using previously collected video ids download audio from these Youtube videos.

```bash
./download_youtube_audio.py -i ./INPUT_FOLDER -o ./OUTPUT_FOLDER --max-video-duration 3600 --total-duration 360000
```