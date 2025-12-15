# -----------------------------------------------------------------------------
# """PresetManager: A small manager around the preset dictionary"""
# -----------------------------------------------------------------------------
import os
import copy
from pygame import mixer


class PresetManager:
    """
    Manages access to predefined beat patterns stored in an internal dictionary.
    Ensures safe loading of presets by validating input and returning copies of data.
    """
    def __init__(self, preset_dictionary):
        """
        Initializes the manager with a deep copy of the preset data dictionary.

        :param preset_dictionary: A dictionary containing preset names as keys 
                                  and beat data (beats, bpm, pattern) as values.
        :raises TypeError: If the input is not a dictionary.
        """
        if not isinstance(preset_dictionary, dict):
            raise TypeError("preset_dictionary must be a dict")
        self._presets = copy.deepcopy(preset_dictionary)

    def get_preset_names(self):
        """
        Retrieves a list of all available preset names.

        :return: A list of strings (preset keys).
        """
        return list(self._presets.keys())

    def load_preset_by_name(self, name):
        """
        Loads the beat data associated with a specific preset name.

        :param name: The string name of the preset to load.
        :return: A tuple (beats: int, bpm: int, pattern: list of lists) if the 
        preset is found, or None otherwise. Data is deep-copied to 
        prevent external mutation of the internal state.
        :raises TypeError: If the input name is not a string.
        """
        # Input validation
        if not isinstance(name, str):
            raise TypeError("preset name must be a str")

        data = self._presets.get(name)
        if data is None:
            return None
            
        # Return copies so consumers don't mutate internal state
        return int(data["beats"]), int(data["bpm"]), copy.deepcopy(data["pattern"])