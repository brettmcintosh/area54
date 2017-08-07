import curses
import random

from sequencer import Sequencer

random = random.SystemRandom()
DELAY_INTERVAL = 1000


class Simon:

    def __init__(self, window):
        self.window = window
        self.sequencer = Sequencer(window)
        self.pattern = []
        self.add_step()

    @classmethod
    def play_simon(cls, window):
        """Create a Simon instance then play forever."""
        simon = cls(window)
        # set a 20 second timeout
        curses.halfdelay(200)
        while True:
            simon.play_level()

    def play_level(self):
        """Play a level using the current pattern."""
        self.sequencer.display_pattern(self.pattern)
        for step in self.pattern:
            if step != self.get_user_input():
                self.game_over()
                self.reset()
                return
        self.reward()
        self.add_step()
        self.window.clear()

    def add_step(self):
        """Add a step to the pattern."""
        step = random.choice(list(self.sequencer.ADDRESSES))
        self.pattern.append(step)

    def get_user_input(self):
        """Get a keypress event and check that it's valid."""
        step = self.window.getkey()
        if step in self.sequencer.ADDRESSES.keys():
            self.sequencer.send_animation(step)
            self.sequencer.write_to_window(step)
            return step

    def reward(self):
        """Play a reward animation then briefly wait."""
        # TODO add reward animation
        curses.napms(500)

    def reset(self):
        """Reset the pattern."""
        self.pattern = []
        curses.napms(500)

    def game_over(self):
        """Display game over animation then wait for a button press."""
        self.sequencer.display_game_over()
        # press any key to continue
        self.window.getkey()


    

if __name__ == '__main__':
    curses.wrapper(Simon.play_simon)