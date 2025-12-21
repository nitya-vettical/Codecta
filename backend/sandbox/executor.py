import multiprocessing
import sys
import io
import traceback
import time

TIME_LIMIT = 2  # seconds


def _runner(code, queue):
    try:
        # Redirect stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        start = time.time()

        # Restricted builtins
        safe_builtins = {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
        }

        # Execute user code
        exec(code, {"__builtins__": safe_builtins})

        output = sys.stdout.getvalue()
        execution_time_ms = int((time.time() - start) * 1000)

        # Restore stdout
        sys.stdout = old_stdout

        queue.put({
            "status": "success",
            "output": output,
            "error": None,
            "execution_time_ms": execution_time_ms,
            "lines_of_code": len(code.splitlines()),
        })

    except Exception:
        queue.put({
            "status": "error",
            "output": "",
            "error": traceback.format_exc(),
            "execution_time_ms": None,
            "lines_of_code": len(code.splitlines()),
        })


def safe_execute(code: str):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=_runner,
        args=(code, queue)
    )

    process.start()
    process.join(TIME_LIMIT)

    if process.is_alive():
        process.terminate()
        return {
            "status": "timeout",
            "output": "",
            "error": "Execution timed out",
            "execution_time_ms": None,
            "lines_of_code": len(code.splitlines()),
        }

    if not queue.empty():
        return queue.get()

    return {
        "status": "error",
        "output": "",
        "error": "Unknown execution error",
        "execution_time_ms": None,
        "lines_of_code": len(code.splitlines()),
    }
