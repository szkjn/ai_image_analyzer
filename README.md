# Generative AI pipeline, from image to audio

## Overview

This application uses 3 different AI models to :

- Describe a given image
- Transform that neutral description into a cynical description
- Create an audio file from that cynical description

When running, the app monitors file creation in given folders to trigger the process. The process starts with the creation of a temporary image file in `tmp` folder, and finishes by the automatic play of the corresponding final result (audio file).

## Dependencies

1.  Create a virtual environment :

        python -m venv virtual

2.  Activate the virtual environment :

    on Linux/Mac:

        source virtual/Scripts/activate

    on Windows:

        .\virtual\Scripts\activate

3.  Install the necessary librairies :

        pip install openai watchdog playsound Pillow

4.  Create empty directories :

        mkdir archive
        mkdir audio
        mkdir image
        mkdir tmp

5.  Replace your API key(s) in `api_calls.py`
