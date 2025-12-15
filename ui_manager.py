import pygame


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


class UIManager:
    """
    Handles drawing the entire user interface for the digital beat workstation, 
    including the step sequencer grid and all control buttons.
    """
    
    def __init__(self, screen, label_font, medium_font):
        """Initializes the UIManager with the Pygame screen object and required fonts."""
        self.screen = screen
        self.label_font = label_font
        self.medium_font = medium_font

    def draw_grid(self, clicks, beat_index, actives, instruments_count, beats_count):
        """
        Draws the main drum pattern grid, including instrument names and the active beat marker.

        :param clicks: 2D array representing note placements (1=on, -1=off).
        :param beat_index: Index of the current step in the sequence.
        :param actives: 1D array indicating which instruments are muted (1=active, -1=muted).
        :param instruments_count: Total number of instrument rows (fixed at 6 in the app).
        :param beats_count: Total number of beat columns (measure length).
        :return: A list of (pygame.Rect, (step_i, instr_j)) for clickable grid cells.
        """
        boxes = []
        
        # """Draw the side panel for instrument names and the bottom control panel."""
        pygame.draw.rect(self.screen, gray, [0, 0, 200, HEIGHT - 200], 5) 
        pygame.draw.rect(self.screen, gray, [0, HEIGHT - 200, WIDTH, 200], 5) 
        
        # """Draw horizontal lines to separate instrument rows on the side panel."""
        for i in range(instruments_count + 1):
            pygame.draw.line(self.screen, gray, (0, i * 100), (200, i * 100), 3) 


        # """Define colors for instrument text based on their active/muted state."""
        colors = [gray, white, gray]
        
        # """Draw instrument names and reflect mute status in text color."""
        hi_hat_text = self.label_font.render('Hi Hat', True, colors[actives[0]])
        self.screen.blit(hi_hat_text, (30, 30)) 
        snare_text = self.label_font.render('Snare', True, colors[actives[1]])
        self.screen.blit(snare_text, (30, 130))
        kick_text = self.label_font.render('Bass Drum', True, colors[actives[2]])
        self.screen.blit(kick_text, (30, 230))
        crash_text = self.label_font.render('Crash', True, colors[actives[3]])
        self.screen.blit(crash_text, (30, 330))
        clap_text = self.label_font.render('Clap', True, colors[actives[4]])
        self.screen.blit(clap_text, (30, 430))
        tom_text = self.label_font.render('Floor Tom', True, colors[actives[5]])
        self.screen.blit(tom_text, (30, 530))
        
        
        # """Calculate grid cell properties."""
        if beats_count <= 0:
            beats_count = 1
        step_width = (WIDTH - 200) // beats_count 
        
        # """Draw individual grid cells."""
        for i in range(beats_count):
            for j in range(instruments_count):
                if clicks[j][i] == -1: # Note is OFF
                    color = gray
                else: # Note is ON
                    if actives[j] == 1: # Instrument is active
                        color = white
                    else: # Instrument is muted
                        color = dark_gray
                        
                # """Draw the inner colored rectangle (the note indicator)."""
                rect = pygame.draw.rect(self.screen, color, 
                                        [i * step_width + 205, (j * 100) + 5, step_width - 10, 90], 0, 3)
                # """Draw the gold border around the cell."""
                pygame.draw.rect(self.screen, gold, [i * step_width + 200, j * 100, step_width, 100], 5, 5)
                # """Draw the black inner border."""
                pygame.draw.rect(self.screen, black,
                                 [i * step_width + 200, j * 100, step_width, 100],2, 5)
                boxes.append((rect, (i, j)))

        # """Draw the active beat column marker (the moving blue rectangle)."""
        active_rect = pygame.draw.rect(self.screen, blue, 
                                       [beat_index * ((WIDTH - 200) // beats_count) + 200, 0,
                                        ((WIDTH - 200) // beats_count), instruments_count * 100], 5, 3)
        return boxes

    def draw_bottom_menu(self, beats_count, bpm_value, playing):
        """
        Draws the interactive controls located at the bottom of the screen.

        :param beats_count: The current number of beats in the loop.
        :param bpm_value: The current beats per minute value.
        :param playing: Boolean state of playback (True if running).
        :return: A dictionary of control names mapped to their pygame.Rect objects for click handling.
        """
        # """Play/Pause button area."""
        play_pause = pygame.draw.rect(self.screen, gray, [50, HEIGHT - 150, 200, 100], 0, 5)
        play_text = self.label_font.render('Play/Pause', True, white)
        self.screen.blit(play_text, (70, HEIGHT - 130))
        if playing:
            play_text2 = self.medium_font.render('Playing', True, dark_gray)
        else:
            play_text2 = self.medium_font.render('Paused', True, dark_gray)
        self.screen.blit(play_text2, (70, HEIGHT - 100))
        
        # """BPM (Beats Per Minute) display and adjustment buttons."""
        bpm_rect = pygame.draw.rect(self.screen, gray, [300, HEIGHT - 150, 200, 100], 5, 5)
        bpm_text = self.medium_font.render('Beats Per Minute', True, white)
        self.screen.blit(bpm_text, (308, HEIGHT - 130))
        bpm_text2 = self.label_font.render(f'{bpm_value}', True, white)
        self.screen.blit(bpm_text2, (370, HEIGHT - 100))
        
        bpm_add_rect = pygame.draw.rect(self.screen, gray, [510, HEIGHT - 150, 48, 48], 0, 5)
        bpm_sub_rect = pygame.draw.rect(self.screen, gray, [510, HEIGHT - 100, 48, 48], 0, 5)
        self.screen.blit(self.medium_font.render('+5', True, white), (520, HEIGHT - 140))
        self.screen.blit(self.medium_font.render('-5', True, white), (520, HEIGHT - 90))
        
        # """Beats in Loop display and adjustment buttons."""
        beats_rect = pygame.draw.rect(self.screen, gray, [600, HEIGHT - 150, 200, 100], 5, 5)
        beats_text = self.medium_font.render('Beats In Loop', True, white)
        self.screen.blit(beats_text, (612, HEIGHT - 130))
        beats_text2 = self.label_font.render(f'{beats_count}', True, white)
        self.screen.blit(beats_text2, (670, HEIGHT - 100))
        
        beats_add_rect = pygame.draw.rect(self.screen, gray, [810, HEIGHT - 150, 48, 48], 0, 5)
        beats_sub_rect = pygame.draw.rect(self.screen, gray, [810, HEIGHT - 100, 48, 48], 0, 5)
        self.screen.blit(self.medium_font.render('+1', True, white), (820, HEIGHT - 140))
        self.screen.blit(self.medium_font.render('-1', True, white), (820, HEIGHT - 90))
        
        # """Clear Board button."""
        clear = pygame.draw.rect(self.screen, gray, [1150, HEIGHT - 150, 200, 100], 0, 5)
        self.screen.blit(self.label_font.render('Clear Board', True, white), (1160, HEIGHT - 130))
        
        # """Save / Load / Presets buttons."""
        save_button = pygame.draw.rect(self.screen, gray, [900, HEIGHT - 150, 200, 48], 0, 5)
        self.screen.blit(self.label_font.render('Save Beat', True, white), (920, HEIGHT - 140))
        load_button = pygame.draw.rect(self.screen, gray, [900, HEIGHT - 98, 200, 48], 0, 5)
        self.screen.blit(self.label_font.render('Load Beat', True, white), (920, HEIGHT - 90))
        preset_button = pygame.draw.rect(self.screen, gray, [900, HEIGHT - 200, 200, 48], 0, 5)
        self.screen.blit(self.label_font.render('Presets', True, white), (920, HEIGHT - 190))
        
        # """Return all clickable rectangles."""
        return {
            "play_pause": play_pause,
            "bpm_add_rect": bpm_add_rect,
            "bpm_sub_rect": bpm_sub_rect,
            "beats_add_rect": beats_add_rect,
            "beats_sub_rect": beats_sub_rect,
            "clear": clear,
            "save_button": save_button,
            "load_button": load_button,
            "preset_button": preset_button
        }