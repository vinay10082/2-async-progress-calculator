import argparse
import asyncio
import random

from progress_tracker import ProgressSnapshot, ProgressTracker


async def simulate_io_operation(task_id: int, duration: float) -> str:
    """Stand-in for a real non-blocking I/O call (network request, disk read, etc.)."""
    await asyncio.sleep(duration)
    if random.random() < 0.05:
        raise RuntimeError(f"task-{task_id} failed after {duration:.2f}s")
    return f"task-{task_id} completed in {duration:.2f}s"


def render_progress(snapshot: ProgressSnapshot) -> None:
    bar_width = 30
    filled = int(bar_width * snapshot.percentage / 100)
    bar = "#" * filled + "-" * (bar_width - filled)
    print(
        f"\r[{bar}] {snapshot.percentage:5.1f}%  "
        f"({snapshot.completed}/{snapshot.total} done, {snapshot.failed} failed, "
        f"{snapshot.elapsed_seconds:.1f}s elapsed)",
        end="",
        flush=True,
    )


async def run(num_tasks: int, min_duration: float, max_duration: float) -> None:
    tasks = [
        asyncio.create_task(
            simulate_io_operation(i, random.uniform(min_duration, max_duration))
        )
        for i in range(num_tasks)
    ]

    tracker = ProgressTracker(tasks)
    final = await tracker.track(on_update=render_progress)
    print()

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"Error: {result}")

    print(
        f"\nDone: {final.completed}/{final.total} succeeded, "
        f"{final.failed} failed, in {final.elapsed_seconds:.2f}s"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Async progress calculator demo")
    parser.add_argument("--tasks", type=int, default=20, help="Number of simulated I/O tasks")
    parser.add_argument("--min-duration", type=float, default=0.2, help="Minimum task duration in seconds")
    parser.add_argument("--max-duration", type=float, default=3.0, help="Maximum task duration in seconds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args.tasks, args.min_duration, args.max_duration))


if __name__ == "__main__":
    main()
