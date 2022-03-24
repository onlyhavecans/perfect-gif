# perfect-gif

A wrapper to moviepy optimized for bulk extraction of perfect loop gifs from animation

## Usage

```bash
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip wheel
python3 -m pip install -r requirements.txt
./env/bin/python3 gifit.py [--outdir dir] video [video ...]
```

When run it will create a folder for every video and put it's gifs in that folder.

Default base output dir is cwd
