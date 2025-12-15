# -----------------------------------------------------------------------------
# """Menus (BaseMenu with polymorphism -> SaveMenu, LoadMenu, PresetMenu)"""
# -----------------------------------------------------------------------------
import pygame
from pygame import mixer
import copy

# -------------------------
# """Color and Size Variables"""
# -------------------------
black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)
dark_gray = (50, 50, 50)
light_gray = (170, 170, 170)
blue = (0, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
gold = (212, 175, 55)
WIDTH = 1400
HEIGHT = 800


class BaseMenu:
    """
    Base class for all modal menus (Save, Load, Preset).
    It defines the required interface (draw and handle_click) for polymorphism.
    """
    def __init__(self, screen, label_font, medium_font):
        """Initializes the menu with the screen and fonts."""
        self.screen = screen
        self.label_font = label_font
        self.medium_font = medium_font

    def draw(self):
        """Abstract method: Renders the menu content to the screen."""
        raise NotImplementedError()

    def handle_click(self, pos, app):
        """
        Abstract method: Handles a mouse click event within the menu.

        :param pos: The (x, y) coordinates of the click.
        :param app: The main application object (PyDrumsApp) to modify its state.
        :return: True if the click was processed by the menu, False otherwise.
        """
        raise NotImplementedError()

class SaveMenu(BaseMenu):
    """
    Handles the UI and logic for saving the current beat pattern.
    """
    def __init__(self, screen, label_font, medium_font):
        super().__init__(screen, label_font, medium_font)

        # """Define UI Rectangles for the menu components."""
        self._entry_rect = pygame.Rect(400, 200, 600, 200)
        self._exit_rect = pygame.Rect(WIDTH - 200, HEIGHT - 100, 180, 90)
        self._save_rect = pygame.Rect(WIDTH // 2 - 100, int(HEIGHT * 0.75), 200, 100)

    # -------------------------------------
    # """Draw Menu"""
    # -------------------------------------
    def draw(self, beat_name, typing, app):
        """Draws the save menu, including the text input box, Save button, and error message."""
        pygame.draw.rect(self.screen, black, [0, 0, WIDTH, HEIGHT])

        menu_text = self.label_font.render(
            'SAVE MENU: Give a name of your wonderful beat!', True, white
        )
        self.screen.blit(menu_text, (400, 40))

        # """Exit button"""
        exit_text = self.label_font.render('Close', True, white)
        pygame.draw.rect(self.screen, gray, self._exit_rect, 0, 5)
        self.screen.blit(exit_text, (self._exit_rect.x + 40, self._exit_rect.y + 30))

        # """Save button"""
        saving_text = self.label_font.render('Save Beat', True, white)
        pygame.draw.rect(self.screen, gray, self._save_rect, 0, 5)
        self.screen.blit(saving_text, (self._save_rect.x + 30, self._save_rect.y + 30))

        # """Entry box (text input field)"""
        if typing:
            pygame.draw.rect(self.screen, dark_gray, self._entry_rect, 0, 5)
        pygame.draw.rect(self.screen, gray, self._entry_rect, 5, 5)

        entry_text = self.label_font.render(f'{beat_name}', True, white)
        self.screen.blit(entry_text, (self._entry_rect.x + 30, self._entry_rect.y + 50))

        # """ERROR MESSAGE"""
        if hasattr(app, "save_error") and app.save_error:
            error_text = self.medium_font.render(app.save_error, True, red)
            self.screen.blit(error_text, (self._entry_rect.x, self._entry_rect.y + 170))

    # -------------------------------------
    # """Handle Clicks and Validation"""
    # -------------------------------------
    def handle_click(self, pos, app):
        """Handles mouse clicks for the Save Menu (Close, Text Toggle, Save)."""

        # """Close button"""
        if self._exit_rect.collidepoint(pos):
            app.save_menu = False
            app.typing = False
            app.beat_name = ''
            app.playing = True
            app.save_error = ""  # clear errors on close
            return True

        # """Typing toggle (activates/deactivates text input)"""
        if self._entry_rect.collidepoint(pos):
            app.typing = not app.typing
            return True

        # """SAVE BUTTON CLICK"""
        if self._save_rect.collidepoint(pos):

            # --- VALIDATION ---
            if not isinstance(app.beat_name, str) or len(app.beat_name.strip()) <= 3:
                app.save_error = "Name must be more than 3 characters!"
                return True

            # """Clear old errors on successful validation."""
            app.save_error = ""

            # """Format the beat string and append it to the in-memory list."""
            app.saved_beats.append(
                f'name: {app.beat_name}, beats: {app.beats}, bpm: {app.bpm}, selected: {app.clicked}'
            )

            # """Write the updated list back to the file."""
            try:
                with open('saved_beats.txt', 'w', encoding='utf-8') as file:
                    for item in app.saved_beats:
                        file.write(str(item) + '\n')
            except Exception as exc:
                print("Error saving beats:", exc)

            # """Close menu & reset state."""
            app.save_menu = False
            app.typing = False
            app.beat_name = ''
            app.playing = True
            return True

        return False

class LoadMenu(BaseMenu):
    """
    Handles the UI and logic for loading and deleting saved beat patterns.
    """
    def __init__(self, screen, label_font, medium_font):
        super().__init__(screen, label_font, medium_font)
        # """Define UI Rectangles for the menu components."""
        self._exit_rect = pygame.Rect(WIDTH - 200, HEIGHT - 100, 180, 90)
        self._load_btn_rect = pygame.Rect(WIDTH // 2 - 100, int(HEIGHT * 0.87), 200, 100)
        self._delete_btn_rect = pygame.Rect(WIDTH // 2 - 400, int(HEIGHT * 0.87), 200, 100)
        self._entry_rect = pygame.Rect(190, 90, 1000, 600)
        

    def draw(self, app_index, saved_beats):
        """Draws the load menu, listing saved beats and highlighting the selected one."""
        pygame.draw.rect(self.screen, black, [0, 0, WIDTH, HEIGHT])
        self.screen.blit(self.label_font.render('LOAD MENU: Select a beat to load in', True, white), (400, 40))
        
        # """Close button"""
        pygame.draw.rect(self.screen, gray, self._exit_rect, 0, 5)
        self.screen.blit(self.label_font.render('Close', True, white), (self._exit_rect.x + 40, self._exit_rect.y + 30))
        
        # """Load button"""
        pygame.draw.rect(self.screen, gray, self._load_btn_rect, 0, 5)
        self.screen.blit(self.label_font.render('Load Beat', True, white), (self._load_btn_rect.x + 30, self._load_btn_rect.y + 30))
        
        # """Delete button"""
        pygame.draw.rect(self.screen, gray, self._delete_btn_rect, 0, 5)
        self.screen.blit(self.label_font.render('Delete Beat', True, white), (self._delete_btn_rect.x + 15, self._delete_btn_rect.y + 30))
        
        # """Highlight selected beat"""
        if 0 <= app_index < len(saved_beats):
            pygame.draw.rect(self.screen, light_gray, (190, 100 + app_index * 50, 1000, 50))
            
        # """Draw the list of saved beats."""
        for i, raw in enumerate(saved_beats):
            if i < 20:  # """Limit to first 10 entries as per original logic."""
                try:
                    # """Attempt to parse the beat name from the structured string."""
                    name_index_start = raw.index('name: ') + 6
                    name_index_end = raw.index(', beats:')
                    name_text = raw[name_index_start:name_index_end]
                except Exception:
                    name_text = raw
                    
                self.screen.blit(self.medium_font.render(f'{i + 1}', True, white), (200, 100 + i * 50))
                self.screen.blit(self.medium_font.render(name_text, True, white), (240, 100 + i * 50))
                
        # """Draw the border around the list area."""
        pygame.draw.rect(self.screen, gray, self._entry_rect, 5, 5)

    def handle_click(self, pos, app):
        """Handles mouse clicks for the Load Menu (Close, Select Entry, Delete, Load)."""
        if self._exit_rect.collidepoint(pos):
            app.load_menu = False
            app.playing = True
            app.typing = False
            return True
            
        if self._entry_rect.collidepoint(pos):
            # """Calculate the index based on click y-position."""
            y = pos[1] - 100
            idx = y // 50
            # """Store the selected index if valid."""
            if isinstance(idx, int) and 0 <= idx < len(app.saved_beats):
                app.index = idx
            return True
            
        if self._delete_btn_rect.collidepoint(pos):
            # """Delete the currently selected beat."""
            if 0 <= app.index < len(app.saved_beats):
                app.saved_beats.pop(app.index)
            return True
            
        if self._load_btn_rect.collidepoint(pos):
            if 0 <= app.index < len(app.saved_beats):
                # """Attempt to parse and apply the selected beat data."""
                loaded_tuple = self._parse_saved_line(app.saved_beats[app.index])
                if loaded_tuple:
                    new_beats, new_bpm, new_grid = loaded_tuple
                    # """Apply data safely, preserving old values if parsing fails."""
                    app.beats = new_beats or app.beats
                    app.bpm = new_bpm or app.bpm
                    if new_grid:
                        app.clicked = new_grid
                        
                app.index = 100
                app.save_menu = False
                app.load_menu = False
                app.playing = True
                app.typing = False
            return True
            
        return False

    def _parse_saved_line(self, raw_line):
        """
        Tries to extract beats (int), bpm (int), and the clicked grid (list of lists)
        from the saved string format.
        """
        try:
            # """Find and parse integer values (beats and bpm)."""
            name_index_end = raw_line.index(', beats:')
            beats_index_end = raw_line.index(', bpm:')
            bpm_index_end = raw_line.index(', selected:')
            loaded_beats = int(raw_line[name_index_end + 8:beats_index_end])
            loaded_bpm = int(raw_line[beats_index_end + 6:bpm_index_end])
            
            # """Extract and parse the 2D list string for the grid."""
            loaded_clicks_string = raw_line[bpm_index_end + 14: -1]
            rows = []
            s = loaded_clicks_string.strip()
            
            # """Strip outer brackets if present."""
            if s.startswith('[') and s.endswith(']'):
                s = s[1:-1]
                
            # """Split the string into individual instrument rows."""
            if '], [' in s:
                row_strs = s.split('], [')
            else:
                row_strs = s.split('],')
                
            for r in row_strs:
                r = r.strip().lstrip('[').rstrip(']').strip()
                if not r:
                    continue
                # """Split row into individual step values and convert to int (1 or -1)."""
                items = [it.strip() for it in r.split(',')]
                row = []
                for it in items:
                    if it in ('1', '-1'):
                        row.append(int(it))
                if row:
                    rows.append(row)
                    
            return loaded_beats, loaded_bpm, rows
            
        except Exception:
            # """Return None if parsing fails due to bad file format."""
            return None

class PresetMenu(BaseMenu):
    """
    Handles the UI and logic for loading predefined beat patterns (Presets).
    """
    def __init__(self, screen, label_font, medium_font, preset_manager):
        super().__init__(screen, label_font, medium_font)
        # """Define UI Rectangles for the menu components."""
        self._exit_rect = pygame.Rect(WIDTH - 200, HEIGHT - 100, 180, 90)
        self._preset_buttons = []  # """Stores a list of (rect, preset_name) tuples."""
        self._preset_manager = preset_manager

    def draw(self):
        """Draws the preset menu, listing available presets as clickable buttons."""
        pygame.draw.rect(self.screen, black, [0, 0, WIDTH, HEIGHT])
        self.screen.blit(self.label_font.render('PRESETS: Select a preset to launch', True, white), (400, 40))
        
        # """Close button"""
        pygame.draw.rect(self.screen, gray, self._exit_rect, 0, 5)
        self.screen.blit(self.label_font.render('Close', True, white), (self._exit_rect.x + 40, self._exit_rect.y + 30))
        
        # """Draw buttons for each preset."""
        self._preset_buttons = []
        y = 140
        for name in self._preset_manager.get_preset_names():
            btn_rect = pygame.Rect(350, y, 700, 60)
            pygame.draw.rect(self.screen, gray, btn_rect, 0, 5)
            self.screen.blit(self.medium_font.render(name, True, white), (370, y + 15))
            self._preset_buttons.append((btn_rect, name))
            y += 90

    def handle_click(self, pos, app):
        """Handles mouse clicks for the Preset Menu (Close and loading a preset)."""
        if self._exit_rect.collidepoint(pos):
            app.load_preset = False
            app.playing = True
            return True
            
        # """Check if any preset button was clicked."""
        for btn_rect, name in self._preset_buttons:
            if btn_rect.collidepoint(pos):
                # """Load the pattern data from the PresetManager."""
                preset = self._preset_manager.load_preset_by_name(name)
                if preset:
                    new_beats, new_bpm, new_pattern = preset
                    
                    # """Safely transform the loaded pattern to match the app's instrument count."""
                    pattern = []
                    for r in range(app.instruments):
                        if r < len(new_pattern):
                            row = list(new_pattern[r])
                            # """Ensure all values are strictly 1 or -1."""
                            row = [1 if x == 1 else -1 for x in row]
                            
                            # """Adjust row length to match the preset's beat count."""
                            if len(row) < new_beats:
                                row += [-1] * (new_beats - len(row))
                            elif len(row) > new_beats:
                                row = row[:new_beats]
                            pattern.append(row)
                        else:
                            # """Fill missing instrument rows with an empty pattern."""
                            pattern.append([-1] * new_beats)
                            
                    # """Apply the new beat, bpm, and grid to the main app."""
                    app.beats = int(new_beats)
                    app.bpm = int(new_bpm)
                    app.clicked = copy.deepcopy(pattern)
                    
                app.load_preset = False
                app.playing = True
                return True
                
        return False