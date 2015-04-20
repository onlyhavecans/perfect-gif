# perfect-gif

A wrapper to moviepy optimized for bulk extraction of perfect loop gifs from animation

# Usage
I recommend virtualenv

* virtualenv env
* source venv/bin/activate
* pip install -r requirements.txt
* ./venv/bin/python gifit.py [--outdir dir] video [video ...]

When run it will create a folder for every video and put it's gifs in that folder.

Default base output dir is cwd
