import os
import pygame
from pygame import mixer


# -----------------------------------------------------------------------------
# """SoundManager: Encapsulate audio loading and playback"""
# -----------------------------------------------------------------------------
class SoundManager:
    """
    Manages the loading and playback of sound samples using pygame.mixer.
    It is designed for stability: if sound files are missing or the mixer 
    fails to initialize, it uses silent placeholder objects to prevent crashes.
    """
    def __init__(self, sound_file_paths, channels_per_sound=3):
        """
        Initializes the SoundManager and loads sounds.

        :param sound_file_paths: A list or tuple of file paths for the audio samples.
        :param channels_per_sound: The number of dedicated mixer channels to reserve 
        for simultaneous playback of each sound type.
        :raises TypeError: If sound_file_paths is not a list or tuple.
        """
        # Validate path list
        if not isinstance(sound_file_paths, (list, tuple)):
            raise TypeError("sound_file_paths must be a list or tuple of file paths.")
            
        self._sound_paths = sound_file_paths[:]
        
        # Initialize mixer safely (may fail on headless systems)
        try:
            mixer.init()
        except Exception as exc:
            print("Warning: pygame.mixer.init() failed:", exc)
            
        self._sounds = []
        self._channels_per_sound = max(1, int(channels_per_sound))
        self._load_sounds()

    def _create_silent(self):
        """
        Creates a simple placeholder object that has a .play() method that does nothing.
        Used when a real sound file fails to load.
        """
        class _Silent:
            def play(self): pass
        return _Silent()

    def _load_sounds(self):
        """
        Loads all sound files specified in self._sound_paths.
        If loading fails for any sound, a silent placeholder is used instead.
        Attempts to set the total number of mixer channels.
        """
        # Attempt to load each provided path; create silent fallback on errors
        for p in self._sound_paths:
            try:
                if os.path.exists(p):
                    snd = mixer.Sound(p)
                else:
                    print(f"Warning: Sound file not found: {p}. Using silent placeholder.")
                    snd = self._create_silent()
                self._sounds.append(snd)
            except Exception as exc:
                print(f"Warning: Failed to load sound {p} -> {exc}. Using silent placeholder.")
                self._sounds.append(self._create_silent())
                
        # Try setting channels for simultaneous sound playback
        try:
            mixer.set_num_channels(len(self._sounds) * self._channels_per_sound)
        except Exception:
            # Not a fatal error
            pass

    def play_instrument_index(self, instrument_index):
        """
        Plays the sound associated with the given index (instrument).

        :param instrument_index: The zero-based index of the sound sample to play.
        :raises TypeError: If instrument_index is not an integer.
        """
        # Validate index
        if not isinstance(instrument_index, int):
            raise TypeError("instrument_index must be int")
            
        if 0 <= instrument_index < len(self._sounds):
            try:
                # The object at this index is either a real Sound or a _Silent object.
                self._sounds[instrument_index].play()
            except Exception as exc:
                # Playback should never crash the app
                print(f"Warning: playback failed for instrument {instrument_index}: {exc}")