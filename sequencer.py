# -----------------------------------------------------------------------------
# Sequencer: holds beats, timing, grid, and provides methods to step & mutate
# -----------------------------------------------------------------------------
import pygame
class Sequencer:
    """
This module encapsulates all essential timing and pattern data,
including the tempo (BPM), measure structure (beats), and the sequence of notes/events (grid, active beat). 
It acts as the central state manager, utilizing different data structures like lists of lists (for the grid) and integers (for beats and BPM). 
The logic within this module is responsible for accurately driving the timing and playback of the entire musical sequence.
    """
    def __init__(self, instruments_count=6, initial_beats=8, initial_bpm=240):
        self.instruments = int(instruments_count)
        self.beats = max(1, int(initial_beats))
        self.bpm = max(1, int(initial_bpm))
        # grid: instruments x beats, default -1
        self.grid = [[-1 for _ in range(self.beats)] for _ in range(self.instruments)]
        self.active_list = [1 for _ in range(self.instruments)] 
        # timing
        self.active_beat = 0
        self.active_length = 0
        self._fps = 60
        self._accumulator = 0
        # Ensure mixer channels (defensive)
        try:
            pygame.mixer.set_num_channels(self.instruments * 3)
        except Exception:
            pass

    """Sets the target Frames Per Second (FPS) for the application's drawing/update loop. 
    fps_value (int/str): The desired FPS value. 
    Must be a positive integer. 
    Invalid or non-positive values are silently ignored."""

    def set_fps(self, fps_value):
        try:
            v = int(fps_value)
            if v > 0:
                self._fps = v
        except Exception:
            pass

            """Toggles the state of a single cell (note) in the sequencer grid by multiplying its value by -1. 
            This effectively switches a note ON/OFF. 
            The operation is guarded by index bounds checking."""

    def toggle_cell(self, instrument_index, beat_index):
        if 0 <= instrument_index < self.instruments and 0 <= beat_index < self.beats:
            self.grid[instrument_index][beat_index] *= -1


            """Toggles the active/mute state of an entire instrument track 
                by multiplying its value in self.active_list by -1."""
    def toggle_instrument_active(self, instrument_index):
        if 0 <= instrument_index < self.instruments:
            self.active_list[instrument_index] *= -1

    """Resets the entire sequencer grid, setting every cell back to the default inactive state (-1)."""
    def clear_grid(self):
        self.grid = [[-1 for _ in range(self.beats)] for _ in range(self.instruments)]

    def increase_beats(self):
        self.set_beats(self.beats + 1)

    def decrease_beats(self):
        if self.beats > 1:
            self.set_beats(self.beats - 1)

    def set_beats(self, new_beats):
        # keep existing data where possible
        new_beats = max(1, int(new_beats))
        for row in self.grid:
            if len(row) < new_beats:
                row.extend([-1] * (new_beats - len(row)))
            elif len(row) > new_beats:
                del row[new_beats:]
        self.beats = new_beats
        # normalize rows
        self.grid = [row[:new_beats] if len(row) >= new_beats else row + [-1] * (new_beats - len(row)) for row in self.grid]
        if self.active_beat >= self.beats:
            self.active_beat = 0

    def increase_bpm(self, step=5):
        self.set_bpm(self.bpm + int(step))

    def decrease_bpm(self, step=5):
        self.set_bpm(max(1, self.bpm - int(step)))

    def set_bpm(self, new_bpm):
        new_bpm = max(1, int(new_bpm))
        self.bpm = new_bpm

    def timing_advance(self, fps_clock_tick=1):
        """
        This is the timing logic from the  active_length / beat_length method.
        Returns True when we've advanced to the next beat step (so audio should play).
        """
    
        try:
            beat_length = 3600 // self.bpm if self.bpm > 0 else 1
        except Exception:
            beat_length = 1
        # Use integer 
        if self.active_length < beat_length:
            self.active_length += 1
            return False
        else:
            self.active_length = 0
            if self.active_beat < self.beats - 1:
                self.active_beat += 1
            else:
                self.active_beat = 0
            return True
