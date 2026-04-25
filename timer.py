class Timer:
    def __init__(self, duration=1500):
        self.duration = duration
        self.time_left = duration
        self.running = False
        self.elapsed = 0
        self.after_id = None

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):
        self.time_left = self.duration
        self.elapsed = 0
        self.running = False
        self.after_id = None

    def tick(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            self.elapsed = self.duration - self.time_left
        return self.time_left