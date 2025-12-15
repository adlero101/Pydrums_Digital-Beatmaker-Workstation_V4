from ui_manager import *
from sound_manager import SoundManager #this class loads and plays the drum sound
from preset_manager import PresetManager #this class deals with the "Preset" feature
from storage_manager import StorageManager #Whenever you store your beat, it's in this class
from sequencer import Sequencer #the machine; the core of this program
from menus import SaveMenu, LoadMenu, PresetMenu #the superclass that handles the save, load, and preset menus in the UI

import pygame
import copy #duplicate lists without affecting the original


class PyDrumsApp:
    """
    The main application class. It acts as the logics, managing the Sequencer (beat engine), 
    UIManager (drawing), SoundManager (audio playback), and all persistent data (Storage and Presets).
    """

    def __init__(self):
        """Initializes the core components, state variables, and managers."""
        
        # """this prevents the app from crashing if the font is not found"""
        try:
            self.label_font = pygame.font.Font('Roboto-Bold.ttf', 32)
            self.medium_font = pygame.font.Font('Roboto-Bold.ttf', 24)
        except Exception:
            self.label_font = pygame.font.SysFont(None, 32)
            self.medium_font = pygame.font.SysFont(None, 24)

        # """responsible for the timing"""
        self.sequencer = Sequencer(instruments_count=6, initial_beats=8, initial_bpm=240)
        
        
        self.beats = self.sequencer.beats
        self.bpm = self.sequencer.bpm
        self.instruments = self.sequencer.instruments
        
        # """clicked and active_list are aliases (deep copies managed when changing)"""
        self.clicked = self.sequencer.grid
        self.active_list = self.sequencer.active_list
        self.active_beat = self.sequencer.active_beat
        self.active_length = self.sequencer.active_length

        # """Other app-level state variables""" 
        self.beat_changed = True
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.playing = True

        # """menus state""" 
        self.save_menu = False
        self.load_menu = False
        self.load_preset = False

        # """saved beats (list of lines)"""
        self.saved_beats = StorageManager().load_all_lines()

        # """save/load UI state"""
        self.beat_name = ''
        self.typing = False
        self.index = 100

        # """rect placeholder to avoid NameError"""
        self.exit_button = pygame.Rect(0, 0, 0, 0)
        self.saving_button = pygame.Rect(0, 0, 0, 0)
        self.loading_button = pygame.Rect(0, 0, 0, 0)
        self.delete_button = pygame.Rect(0, 0, 0, 0)
        self.entry_rect = pygame.Rect(0, 0, 0, 0)
        self.preset_buttons = []
        self.save_error = ""

        # """Create screen"""
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption('PyDrums - Digital Beatmaker Workstation')

        # """Managers"""
        sound_paths = [
            'sounds/hi hat.wav',
            'sounds/snare.wav',
            'sounds/kick.wav',
            'sounds/crash.wav',
            'sounds/clap.wav',
            'sounds/tom.wav',
        ]
        self.sound_manager = SoundManager(sound_paths)
        # """responsible for the presets"""
        self.preset_manager = PresetManager({
            "Rock Beat": {
                "beats": 8,
                "bpm": 120,
                "pattern": [
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [-1, -1, 1, -1, -1, 1, -1, -1],
                    [1, -1, -1, 1, -1, -1, 1, -1],
                    [-1, -1, -1, -1, 1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                ]
            },
            "Trap Beat": {
                "beats": 8,
                "bpm": 140,
                "pattern": [
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [1, -1, 1, -1, 1, -1, 1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [1, -1, -1, 1, -1, -1, 1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                ]
            },
            "Lo-fi Groove": {
                "beats": 8,
                "bpm": 90,
                "pattern": [
                    [1, -1, 1, -1, 1, -1, 1, -1],
                    [-1, -1, 1, -1, -1, 1, -1, -1],
                    [1, -1, -1, 1, -1, -1, 1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                    [-1, -1, -1, -1, -1, -1, -1, -1],
                ]
            }
        })

        self.ui_manager = UIManager(self.screen, self.label_font, self.medium_font)

        # """Menus (polymorphic)"""
        self._save_menu = SaveMenu(self.screen, self.label_font, self.medium_font)
        self._load_menu = LoadMenu(self.screen, self.label_font, self.medium_font)
        self._preset_menu = PresetMenu(self.screen, self.label_font, self.medium_font, self.preset_manager)

    # ---------------------------
    # """Utilities to sync alias attributes with sequencer authoritative state"""
    # ---------------------------
    def _sync_from_sequencer(self):
        """Make sure attribute aliases reflect sequencer state."""
        self.beats = self.sequencer.beats
        self.bpm = self.sequencer.bpm
        self.instruments = self.sequencer.instruments
        self.clicked = self.sequencer.grid
        self.active_list = self.sequencer.active_list
        self.active_beat = self.sequencer.active_beat
        self.active_length = self.sequencer.active_length

    def _sync_to_sequencer(self):
        """If we mutated alias attributes directly, push them to the sequencer (not used often)."""
        try:
            self.sequencer.beats = int(self.beats)
            self.sequencer.bpm = int(self.bpm)
            self.sequencer.grid = self.clicked
            self.sequencer.active_list = self.active_list
            self.sequencer.active_beat = int(self.active_beat)
            self.sequencer.active_length = int(self.active_length)
        except Exception:
            pass

    # ---------------------------
    # """Play"""
    # ---------------------------
    def play_notes(self):
        """Plays the sounds for the current active_beat according to clicked and active_list."""
        for i in range(len(self.clicked)):
            try:
                if self.clicked[i][self.active_beat] == 1 and self.active_list[i] == 1:
                    if i == 0:
                        self.sound_manager.play_instrument_index(0)  # hi_hat
                    elif i == 1:
                        self.sound_manager.play_instrument_index(1)  # snare
                    elif i == 2:
                        self.sound_manager.play_instrument_index(2)  # kick
                    elif i == 3:
                        self.sound_manager.play_instrument_index(3)  # crash
                    elif i == 4:
                        self.sound_manager.play_instrument_index(4)  # clap
                    elif i == 5:
                        self.sound_manager.play_instrument_index(5)  # tom
            except Exception:
                # Defensive: ignore audio errors
                pass

    # ---------------------------
    # """Main loop"""
    # ---------------------------
    def run(self):
        run_flag = True
        while run_flag:
            # """tick clock"""
            self.timer.tick(self.fps)

            # """fill background"""
            self.screen.fill(red)

            # """sync attribute aliases before drawing"""
            self._sync_from_sequencer()

            # """Draw grid and receive interactive boxes"""
            boxes = self.ui_manager.draw_grid(self.clicked, self.active_beat, self.active_list, self.instruments, self.beats)

            # """draw bottom menu and get control rects"""
            controls = self.ui_manager.draw_bottom_menu(self.beats, self.bpm, self.playing)

            # """If beat changed flag: play notes then clear flag (original semantics)"""
            if self.beat_changed:
                self.play_notes()
                self.beat_changed = False

            # """draw menus if active (the actual drawing of modal menus is handled when requested)"""
            if self.save_menu:
                self._save_menu.draw(self.beat_name, self.typing, self)
            elif self.load_menu:
                self._load_menu.draw(self.index, self.saved_beats)
            elif self.load_preset:
                self._preset_menu.draw()

            # """Event processing"""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run_flag = False
                    break

                # """clicking on grid boxes (only when no menu open)"""
                if event.type == pygame.MOUSEBUTTONDOWN and not (self.save_menu or self.load_menu or self.load_preset):
                    for rect, coords in boxes:
                        if rect.collidepoint(event.pos):
                            # """coords = (step_i, instr_j) as returned by UI"""
                            step_i, instr_j = coords
                            # """toggle same as original: clicked[instr][step] *= -1"""
                            try:
                                self.clicked[instr_j][step_i] *= -1
                                # """update sequencer authoritative grid"""
                                self.sequencer.grid = self.clicked
                            except Exception:
                                pass

                # """primary mouse up handling (main UI controls) when no menu open"""
                if event.type == pygame.MOUSEBUTTONUP and not (self.save_menu or self.load_menu or self.load_preset):
                    pos = event.pos

                    # """play/pause toggle area"""
                    play_pause_rect = controls["play_pause"]
                    if play_pause_rect.collidepoint(pos) and self.playing:
                        self.playing = False
                    elif play_pause_rect.collidepoint(pos) and not self.playing:
                        self.playing = True
                        self.active_beat = 0
                        self.active_length = 0

                        # """push to sequencer"""
                        self.sequencer.active_beat = 0
                        self.sequencer.active_length = 0

                    # """beats change + adjusting clicked grid length"""
                    if controls["beats_add_rect"].collidepoint(pos):
                        self.beats += 1
                        for row in self.clicked:
                            row.append(-1)
                        # """push to sequencer"""
                        self.sequencer.set_beats(self.beats)
                    elif controls["beats_sub_rect"].collidepoint(pos):
                        if self.beats > 1:
                            self.beats -= 1
                            for row in self.clicked:
                                if len(row) > 0:
                                    row.pop(-1)
                            self.sequencer.set_beats(self.beats)

                    # """bpm adjustments"""
                    if controls["bpm_add_rect"].collidepoint(pos):
                        self.bpm += 5
                        self.sequencer.set_bpm(self.bpm)
                    elif controls["bpm_sub_rect"].collidepoint(pos):
                        self.bpm = max(1, self.bpm - 5)
                        self.sequencer.set_bpm(self.bpm)
                    # """clear board"""
                    if controls["clear"].collidepoint(pos):
                        self.clicked = [[-1 for _ in range(self.beats)] for _ in range(self.instruments)]
                        self.sequencer.grid = self.clicked
                    # """instrument rectangles: toggle active_list entries"""
                    instrument_rects = [pygame.Rect((0, i * 100), (200, 100)) for i in range(self.instruments)]
                    for i_rect_i in range(len(instrument_rects)):
                        if instrument_rects[i_rect_i].collidepoint(pos):
                            self.active_list[i_rect_i] *= -1
                            self.sequencer.active_list = self.active_list
                    # """Save/Load/Preset buttons"""
                    if controls["save_button"].collidepoint(pos):
                        self.save_menu = True
                    if controls["load_button"].collidepoint(pos):
                        self.load_menu = True
                        self.playing = False
                    if controls["preset_button"].collidepoint(pos):
                        self.load_preset = True
                        self.playing = False
                # """menu-specific mouse up for exit and menu controls"""
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = event.pos
                    # """universal exit handling"""
                    if hasattr(self, "exit_button") and self.exit_button and isinstance(self.exit_button, pygame.Rect):
                        if self.exit_button.collidepoint(pos):
                            self.save_menu = False
                            self.load_menu = False
                            self.load_preset = False
                            self.playing = True
                            self.typing = False
                            self.beat_name = ''
                    # """entry rect interactions (save/load selection)"""
                    if hasattr(self, "entry_rect") and self.entry_rect and isinstance(self.entry_rect, pygame.Rect):
                        if self.entry_rect.collidepoint(pos):
                            if self.save_menu:
                                self.typing = not self.typing
                            if self.load_menu:
                                # """replicate original index calculation"""
                                self.index = (pos[1] - 100) // 50
                    # """delegate to specific menu handlers (polymorphism)"""
                    if self.save_menu:
                        handled = self._save_menu.handle_click(pos, self)
                        if handled:
                            # """ensure sequencer reflects changes"""
                            self.sequencer.grid = self.clicked
                    elif self.load_menu:
                        handled = self._load_menu.handle_click(pos, self)
                        if handled:
                            self.sequencer.grid = self.clicked
                            self.sequencer.set_beats(self.beats)
                    elif self.load_preset:
                        handled = self._preset_menu.handle_click(pos, self)
                        if handled:
                            self.sequencer.grid = self.clicked
                            self.sequencer.set_beats(self.beats)
                # """text input"""
                if event.type == pygame.TEXTINPUT and self.typing:
                    self.beat_name += event.text
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE and len(self.beat_name) > 0 and self.typing:
                        self.beat_name = self.beat_name[:-1]
            # """beat timing - runs the tempo logics"""
            if self.playing:
                advanced = self.sequencer.timing_advance()
                if advanced:
                    # """sync aliases then play notes"""
                    self._sync_from_sequencer()
                    self.play_notes()
                    self.beat_changed = False
                    # """update attribute aliases"""
                    self.active_beat = self.sequencer.active_beat
            # """flip display"""
            pygame.display.flip()
        # """on exit: write saved_beats back to file (preserve original behaviour)"""
        try:
            with open('saved_beats.txt', 'w', encoding='utf-8') as file:
                for i in range(len(self.saved_beats)):
                    file.write(str(self.saved_beats[i]) + '\n')
        except Exception as exc:
            print("Error writing saved beats on exit:", exc)
        pygame.quit()


# -----------------------------------------------------------------------------
# """Run application"""
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # """Provide helpful console message for missing assets"""
    print("Starting PyDrums - Digital Beat Workstation.")
    pygame.init() # Initialise pygame before creating app
    app = PyDrumsApp()

    # """enable text input events when typing is toggled through GUI"""
    pygame.key.start_text_input()
    app.run()
