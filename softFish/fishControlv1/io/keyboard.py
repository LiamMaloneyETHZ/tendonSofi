# fishControlv1/io/keyboard.py
import sys, os, tty, termios, select, time

class RawKeyboard:
    def __init__(self):
        self._fd = None
        self._old = None
        self._posix = (os.name != 'nt')

    def __enter__(self):
        if self._posix:
            self._fd = sys.stdin.fileno()
            self._old = termios.tcgetattr(self._fd)
            tty.setraw(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._posix and self._old:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)

    # ---- cooked input helpers (so input() works) ----
    def _enter_cooked(self):
        if self._posix and self._old:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)

    def _enter_raw(self):
        if self._posix and self._fd is not None:
            cur = termios.tcgetattr(self._fd)
            tty.setraw(self._fd)

    def input_line(self, prompt=""):
        """Temporarily leave raw mode to read a normal line."""
        if self._posix:
            self._enter_cooked()
            try:
                return input(prompt)
            finally:
                self._enter_raw()
        else:
            return input(prompt)

    # ---- nonblocking key read ----
    def _posix_read_nonblock(self, timeout):
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if not r:
            return None
        return sys.stdin.read(1)

    def read_key(self, timeout=0.05):
        if not self._posix:
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                return '\n' if ch == '\r' else ch
            return None

        ch = self._posix_read_nonblock(timeout)
        if ch is None:
            return None

        if ch == '\x1b':  # ESC: try to collect a full sequence
            seq = ch
            t_end = time.time() + 0.04  # collect up to 40 ms
            while time.time() < t_end:
                nxt = self._posix_read_nonblock(0.003)
                if not nxt:
                    break
                seq += nxt
                # Common arrow forms: ESC [ A  or ESC O A
                if len(seq) >= 3 and (seq.startswith('\x1b[') or seq.startswith('\x1bO')):
                    return seq[:3]
            return '\x1b'  # lone ESC
        return ch
