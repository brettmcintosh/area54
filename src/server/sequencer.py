import curses
from collections import OrderedDict
from threading import Thread
from time import sleep

from audio_player import AudioPlayer
from mqtt import *


class Sequencer:

    def __init__(self):
        self.mqtt_client = MqttClient.get_client()

    def send_animation(self, address, animation):
        self.mqtt_client.send_animation(address, animation)


class GameSequencer(Sequencer):

    ADDRESSES = {
        'a': BEACON1,
        's': BEACON2,
        'd': BEACON3,
        'f': BEACON4,
        'g': BEACON5,
        'h': BEACON6,
    }

    def __init__(self, window, audio):
        super().__init__()
        self.window = window
        self.audio_sequencer = None
        if audio:
            self.audio_sequencer = AudioPlayer()

    def display_pattern(self, pattern, duration_between=500):
        """Display the pattern with the beacons and in the window."""
        for step in pattern:
            self.play_step(step)
            curses.napms(duration_between)
        self.window.clear()

    def play_step(self, step, animation='fuchsia'):
        """Play the LED animation and audio, and display the step."""
        self.send_animation(self.ADDRESSES[step], animation)
        if self.audio_sequencer:
            self.audio_sequencer.play_audio(step)
        self.write_to_window(step)

    def write_to_window(self, step):
        """Write the step to the window."""
        self.window.clear()
        self.window.addstr(self.format_step(step), curses.A_BOLD)
        self.window.refresh()

    def format_step(self, step):
        """Pad the step for display in the window."""
        return list(self.ADDRESSES).index(step) * ' ' + step

    def game_over(self):
        """Send game over animation to beacons and window."""
        self.window.clear()
        self.window.addstr('GAME OVER')
        # TODO this should send 1 msg to a broadcast topic
        for address in self.ADDRESSES.values():
            self.send_animation(address, 'game_over')
        if self.audio_sequencer:
            self.audio_sequencer.play_game_over()


class BpmSequencer(Sequencer):

    def __init__(self, playlist, bpm=120):
        super().__init__()
        self.playlist = playlist
        self.bpm = bpm
        self.timer_thread = None
        self.reset_timer()
        self._continue_timer = True

    def generate_beats(self):
        for current_sequence, num_cycles in self.playlist.items():
            for _ in range(num_cycles):
                for beat in current_sequence:
                    for cue in beat:
                        for address in cue.addresses:
                            self.send_animation(address, cue.animation)
                        yield

    def _start_timer(self):
        """Play beats from the sequence at the bpm rate."""
        beat_generator = self.generate_beats()
        while self._continue_timer:
            try:
                next(beat_generator)
            except StopIteration:
                beat_generator = self.generate_beats()
                next(beat_generator)
            sleep(60.0 / self.bpm)

    def start(self):
        """Start the timer thread."""
        self.timer_thread.start()

    def stop(self):
        """Stop and reset the timer thread."""
        self._continue_timer = False
        self.timer_thread.join(timeout=1.0)
        self.reset_timer()

    def reset_timer(self):
        self.timer_thread = Thread(target=self._start_timer, name='timer')
        self._continue_timer = True


class PlayList(OrderedDict):
    pass


class BeatSequence(tuple):
    pass


class Beat(tuple):
    pass


class Cue:

    def __init__(self, addresses, animation):
        self.addresses = addresses
        self.animation = animation


def get_test_sequencer():
    even_fuchsia = Cue((BEACON2, BEACON4, BEACON6,), 'fuchsia')
    odd_red = Cue((BEACON1, BEACON3, BEACON5,), 'game_over')
    both_beat = Beat([even_fuchsia, odd_red, ])
    just_fuchsia_beat = Beat([even_fuchsia, ])
    both_seq = BeatSequence((both_beat, just_fuchsia_beat,))
    just_fuchsia_seq = BeatSequence((just_fuchsia_beat,))
    playlist = PlayList({both_seq: 3, just_fuchsia_seq: 1, })
    return BpmSequencer(playlist)


if __name__ == '__main__':
    seq = get_test_sequencer()
    seq.start()
