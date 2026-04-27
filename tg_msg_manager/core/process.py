import os
import signal
import logging
import asyncio
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ProcessManager:
    """
    Manages process-level concerns: file locking and signal handling.
    """

    def __init__(self, lock_path: str = ".tg_msg_manager.lock"):
        self.lock_path = lock_path
        self.lock_fd: Optional[int] = None
        self.shutdown_requested = False
        self._sig_count = 0

    def acquire_lock(self) -> bool:
        """
        Attempts to acquire the process lock. Returns True if successful, False otherwise.
        """
        try:
            # Create lock file exclusively
            self.lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            # Write current PID to the lock file
            os.write(self.lock_fd, str(os.getpid()).encode())
            logger.debug(f"Process lock acquired at {self.lock_path}")
            return True
        except FileExistsError:
            # Check if PID is still alive (basic check)
            try:
                with open(self.lock_path, "r") as f:
                    content = f.read().strip()
                if not content:
                    raise ValueError("Empty lock file")
                old_pid = int(content)
                os.kill(old_pid, 0)  # Check if process exists
                return False
            except (OSError, ValueError):
                # Process is dead but lock file exists
                logger.warning("Stale lock file found. Overwriting.")
                try:
                    os.remove(self.lock_path)
                except OSError:
                    pass
                return self.acquire_lock()

    def release_lock(self):
        """
        Releases the process lock and removes the file.
        """
        if self.lock_fd is not None:
            try:
                os.close(self.lock_fd)
            except OSError:
                pass
            self.lock_fd = None
        if os.path.exists(self.lock_path):
            try:
                os.remove(self.lock_path)
            except OSError:
                pass
            logger.debug("Process lock released.")

    def __enter__(self):
        if not self.acquire_lock():
            raise RuntimeError("Could not acquire process lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_lock()

    @staticmethod
    def _signal_name(sig: int) -> str:
        if hasattr(signal, "SIGHUP") and sig == signal.SIGHUP:
            return "SIGHUP"
        if sig == signal.SIGTERM:
            return "SIGTERM"
        return "SIGINT"

    def _handle_sync_signal(
        self,
        sig: int,
        loop_stop_callback: Optional[Callable] = None,
        force_exit: Callable[[int], None] = os._exit,
    ):
        self._sig_count += 1
        sig_name = self._signal_name(sig)

        # Ensure we start on a new line if interrupting a progress bar
        print("\n", end="", flush=True)

        if self._sig_count > 1:
            print(f"🧨 Forceful exit triggered by {sig_name}...")
            force_exit(1)
            return

        logger.warning(
            f"Signal {sig_name} ({sig}) received. Requesting graceful shutdown..."
        )
        self.shutdown_requested = True

        if loop_stop_callback:
            loop_stop_callback()

        # For SIGINT, we raise KeyboardInterrupt to break current await calls
        if sig == signal.SIGINT:
            raise KeyboardInterrupt

        # For HUP or TERM, we usually want to exit immediately but nicely
        hup = getattr(signal, "SIGHUP", None)
        if sig in tuple(s for s in (hup, signal.SIGTERM) if s is not None):
            raise SystemExit(0)

    def setup_signals(self, loop_stop_callback: Optional[Callable] = None):
        """
        Registers handlers for SIGINT, SIGTERM, and SIGHUP.
        Implements a multi-stage shutdown:
        1st Ctrl+C = Graceful KeyboardInterrupt
        2nd Ctrl+C = Hard SystemExit
        """
        self._sig_count = 0

        def handler(sig, frame):
            self._handle_sync_signal(sig, loop_stop_callback=loop_stop_callback)

        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, handler)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def setup_async_signals(
        self,
        loop: asyncio.AbstractEventLoop,
        on_interrupt_callback: Optional[Callable] = None,
    ):
        """
        Registers async-aware handlers for SIGINT using the event loop.
        This is more reliable for async apps than signal.signal.
        """
        self._sig_count = 0

        def handle_async_sig():
            self._sig_count += 1
            # Ensure we start on a new line
            print("\n", end="", flush=True)

            if self._sig_count > 1:
                print("🧨 Forceful exit triggered...")
                os._exit(1)

            logger.warning("SIGINT received. Requesting graceful shutdown...")
            self.shutdown_requested = True

            # Schedule the async callback into the loop
            if on_interrupt_callback:
                if asyncio.iscoroutinefunction(on_interrupt_callback):
                    asyncio.create_task(on_interrupt_callback())
                else:
                    on_interrupt_callback()

        try:
            loop.add_signal_handler(signal.SIGINT, handle_async_sig)
            logger.debug("Async SIGINT handler registered.")
        except NotImplementedError:
            # Fallback for platforms that don't support add_signal_handler (like Windows)
            logger.debug(
                "add_signal_handler not supported on this platform, falling back to setup_signals."
            )
            self.setup_signals()

    def should_stop(self) -> bool:
        return self.shutdown_requested
