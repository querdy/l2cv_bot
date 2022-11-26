import threading
from threading import Timer


class TimerReset(Timer):

    def __init__(self, interval, function, daemon=None, args=None, kwargs=None):
        super().__init__(interval, function, args=args, kwargs=kwargs)

        if daemon is not None:
            self.daemon = daemon

    def start(self):
        super().start()
        self._started.clear()

    def run(self):
        if self._started.is_set():
            self.finished.clear()
        super().run()

# class TimerReset(Timer):
#
#     def __init__(self, interval, function, args=None, kwargs=None):
#         super().__init__(interval, function, args=args, kwargs=kwargs)
#         self.resetted = False
#
#     def run(self):
#         if self.resetted:
#             self.resetted = False
#             self.finished.clear()
#         super().run()
#
#     def start(self):
#         """Start the thread's activity.
#
#         It must be called at most once per thread object. It arranges for the
#         object's run() method to be invoked in a separate thread of control.
#
#         This method will raise a RuntimeError if called more than once on the
#         same thread object.
#
#         """
#         if not self._initialized:
#             raise RuntimeError("thread.__init__() not called")
#
#         with threading._active_limbo_lock:
#             threading._limbo[self] = self
#         try:
#             threading._start_new_thread(self._bootstrap, ())
#         except Exception:
#             with threading._active_limbo_lock:
#                 del threading._limbo[self]
#             raise
#
#         self.resetted = True