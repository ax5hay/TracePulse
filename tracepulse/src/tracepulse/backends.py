import json
import queue
import atexit
import threading
from pathlib import Path
from typing import Dict, Any, List
from abc import ABC, abstractmethod

# Sentinel object to signal the worker to stop
_STOP_SIGNAL = object()

class BaseBackend(ABC):
    """Abstract base class for all trace backends."""
    @abstractmethod
    def emit(self, event: Dict[str, Any]):
        pass

class ConsoleBackend(BaseBackend):
    """Simple backend that prints traces to stdout."""
    def emit(self, event: Dict[str, Any]):
        print(json.dumps(event, default=str))

class AsyncFileBackend(BaseBackend):
    """
    Writes events to a file using a background thread and a queue.
    This ensures the tracer never blocks the main application execution.
    """
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Queue size limit prevents memory leaks if writer is too slow
        self._queue: queue.Queue = queue.Queue(maxsize=10000)
        
        # Start background worker
        self._thread = threading.Thread(target=self._worker, name="tracepulse-worker", daemon=True)
        self._thread.start()
        
        # Ensure clean shutdown
        atexit.register(self.shutdown)

    def _worker(self):
        """Background loop to process queue items."""
        while True:
            item = self._queue.get()
            if item is _STOP_SIGNAL:
                self._queue.task_done()
                break
            
            try:
                # Append to file
                line = json.dumps(item, default=str, separators=(',', ':'))
                with open(self.file_path, 'a', encoding='utf-8') as f:
                    f.write(line + "\n")
            except Exception:
                # Never crash the worker thread
                pass
            finally:
                self._queue.task_done()

    def emit(self, event: Dict[str, Any]):
        """Non-blocking emit. Drops event if queue is full."""
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            # In high load, drop trace rather than slow down app
            pass

    def shutdown(self):
        """Signal worker to stop and wait for it to finish."""
        self._queue.put(_STOP_SIGNAL)
        self._thread.join(timeout=2.0)

# -- Global Registry --
_backends: List[BaseBackend] = []

def add_backend(backend: BaseBackend):
    """Register a new backend."""
    _backends.append(backend)

def clear_backends():
    """Remove all registered backends."""
    _backends.clear()

def export(event: Dict[str, Any]):
    """Distribute event to all registered backends."""
    for b in _backends:
        try:
            b.emit(event)
        except Exception:
            pass