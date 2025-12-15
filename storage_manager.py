import os

# -----------------------------------------------------------------------------
# """StorageManager: handles reading/writing saved beats (text format kept for compat)"""
# -----------------------------------------------------------------------------
class StorageManager:
    """
    Manages reading from and writing to the saved beats file (saved_beats.txt).
    It is designed to handle file I/O operations, ensuring the file exists 
    and providing error-safe methods for loading and saving line-oriented data.
    """

    def __init__(self, filename="saved_beats.txt"):
        """
        Initializes the StorageManager with a specified filename.
        Attempts to create an empty file if it does not already exist.

        :param filename: The name of the text file used for persistent storage.
        """
        self._filename = filename
        # Ensure file exists
        try:
            if not os.path.exists(self._filename):
                with open(self._filename, 'w') as f:
                    f.write('')
        except Exception as exc:
            print("Warning: Could not ensure save file exists:", exc)

    def load_all_lines(self):
        """
        Reads all non-empty lines from the file, stripping whitespace and 
        newline characters.

        :return: A list of strings, where each string is a stripped line 
        from the saved beats file. Returns an empty list on errors 
        or if the file is not found.
        """
        lines = []
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        lines.append(line.rstrip('\n'))
        except FileNotFoundError:
            # Return empty list if file not present
            lines = []
        except Exception as exc:
            print("Warning: Error loading saved beats:", exc)
        return lines

    def write_all_lines(self, lines):
        """
        Overwrites the entire file content with the provided list of lines.

        :param lines: A list of strings (beat entries) to write to the file.
        :return: True if the write operation was successful, False otherwise.
        """
        try:
            with open(self._filename, 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(str(line) + '\n')
            return True
        except Exception as exc:
            print("Error writing saved beats:", exc)
            return False