# PyDrums_Python Digital Beatmaker

A Pygame-based personalized beatmaker.

## Description

PyDrums is a Python and Pygame-based desktop beatmaker.
It emulates a step sequencer akin to professional Digital Audio Workstations (DAW)
such as Ableton, FL Studio, etc. Users can create custom drum patterns by toggling a grid,
set their own tempo (BPM), adjust the length of the beat, mute/enable a specific instrument track,
load presets, and save or load their own beat.

## How to Run the Program
1. Make sure Python is installed
* Python 3.13 is recommended
2. Install dependencies
``` pip install pygame ```
3. Project structure
  Make sure the following files and folders exist:
  
```
PyDrums/
├── main.py
├── sequencer.py
├── ui_manager.py
├── sound_manager.py
├── preset_manager.py
├── storage_manager.py
├── menus.py
├── sounds/
│   ├── hi hat.wav
│   ├── snare.wav
│   ├── kick.wav
│   ├── crash.wav
│   ├── clap.wav
│   └── tom.wav
└── saved_beats.txt
```

4. Run the application
   ``` python main.py```


