"""PWInput
By Al Sweigart al@inventwithpython.com

A cross-platform Python module that displays **** for password input. Works on Windows, unlike getpass.
Formerly called stdiomask."""

__version__ = '1.0.2'  # type: str

import sys

import keyboard
from win32api import GetKeyState
from win32con import VK_CAPITAL

"""Notes about making this code backwards-compatible with Python 2:
sys.stdout.write() can only write unicode strings, not Python 2 str strings.
I create STR_TYPE to use for isinstance() checks. Also, the u prefix for
unicode strings causes syntax errors on Python 3.1 and 3.2, so instead I
pass those strings to STR_TYPE, which is set to unicode() on Python 2,
which effectively does the same thing as the u prefix.
"""
STR_TYPE = str  # type: type
RUNNING_PYTHON_2 = sys.version_info[0] == 2  # type: bool
if RUNNING_PYTHON_2:
    STR_TYPE = unicode  # Ignore the pyflakes warning on this line.

try:
    from typing import List
except ImportError:
    pass  # There is no typing module on Python 2, but that's fine because we use the comment-style of type hints.

if sys.platform == 'win32':
    # For some reason, mypy reports that msvcrt doesn't have getch, ignore this warning:
    from msvcrt import getch  # type: callable

else:  # macOS and Linux
    import tty
    import termios


    def getch():
        # type: () -> str
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def pwinput(prompt='Password: ', mask='*'):
    # type: (str, str) -> str

    if RUNNING_PYTHON_2:
        # On Python 2, convert `prompt` and `mask` from str to unicode because sys.stdout.write requires unicode.
        if isinstance(prompt, str):
            # Mypy in Python 3 mode (the default mode) will complain about the following line:
            prompt = prompt.decode('utf-8')  # type: ignore
        if isinstance(mask, str):
            # Mypy in Python 3 mode (the default mode) will complain about the following line:
            mask = mask.decode('utf-8')  # type: ignore

    if not isinstance(prompt, STR_TYPE):
        raise TypeError('prompt argument must be a str, not %s' % type(prompt).__name__)

    if not isinstance(mask, STR_TYPE):
        raise TypeError('mask argument must be a zero- or one-character str, not %s' % type(prompt).__name__)

    if len(mask) > 1:
        raise ValueError('mask argument must be a zero- or one-character str')

    if mask == '' or sys.stdin is not sys.__stdin__:
        # Fall back on getpass if a mask is not needed.
        import getpass as gp
        return gp.getpass(prompt)

    entered_password = []  # type: List[str]
    sys.stdout.write(prompt)
    sys.stdout.flush()

    while True:
        keyboard_key = keyboard.read_key()
        key = ord(getch())

        if key == 13: # Enter key pressed.
            if RUNNING_PYTHON_2:
                sys.stdout.write(STR_TYPE('\n'))
            else:
                sys.stdout.write('\n')

            return ''.join(entered_password)
        elif key in (8, 127):  # Backspace/Del key erases previous output.
            if len(entered_password) > 0:
                # Erases previous character.
                if RUNNING_PYTHON_2:
                    sys.stdout.write(
                        STR_TYPE('\b \b'))  # \b doesn't erase the character, it just moves the cursor back.
                else:
                    sys.stdout.write('\b \b')  # \b doesn't erase the character, it just moves the cursor back.
                sys.stdout.flush()
                entered_password = entered_password[:-1]
        elif 0 <= key <= 31:
            # Do nothing for unprintable characters.
            pass
        elif keyboard_key in ['clear', 'down', 'end', 'home', 'insert', 'left', 'page down', 'page up', 'right', 'up'] \
                and not GetKeyState(VK_CAPITAL):
            # Do nothing if user tries to use num pad without num lock activated
            pass
        else:
            # Key is part of the password; display the mask character.
            char = chr(key)
            sys.stdout.write(mask)
            sys.stdout.flush()
            entered_password.append(char)


if __name__ == "__main__":
    var = pwinput(prompt="Password: ", mask="*")
    print(f"=> {var}")
