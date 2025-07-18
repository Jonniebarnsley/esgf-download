import requests
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, \
    TaskProgressColumn, TimeRemainingColumn, TaskID
# local imports
from esgf_download.classes import Dataset, File
from esgf_download.console import console, MAX_DISPLAY_ROWS


# Global keyboard_interrupt instance for thread-safe interrupt handling
keyboard_interrupt = False

def download_file(file: File, progress: Progress, task_id: TaskID) -> None:
    
    """
    Downloads a single file from ESGF to a local directory.

    Parameters
    ----------
    file : File
        File object to download from ESGF.
    progress : Progress
        Progress object to track download progress in ui.
    task_id : TaskID
        Pre-created task ID for this file's progress tracking.
    """

    
    # Check if file already exists locally
    if file.exists():
        if len(file.dataset.files) > MAX_DISPLAY_ROWS:
            progress.remove_task(task_id)
            return
        progress.update(task_id, description=f"[yellow]⚠ {file.filename} (already exists)")
        progress.update(task_id, completed=file.size or 100)
        return

    url = file.download_url
    if not url:
        progress.update(task_id, description=f"[red]✗ {file.filename} (no URL)")
        return

    filename = file.filename
    filepath = file.local_path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Update the pre-created task description to show it's starting
    progress.update(task_id, description=f"[cyan]⬇ {filename}")
    
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        chunk_size = 64 * 1024  # 64KB - good balance of speed and progress updates

        # Update task with total size
        progress.update(task_id, total=file.size)

        # download with progress tracking
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if keyboard_interrupt:  # Check for interrupts during download
                    progress.update(task_id, description=f"[red]✗ {filename}")
                    file.remove()
                    return
                if chunk:
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))

        # Mark task as completed
        progress.update(task_id, description=f"[green]✓ {filename}")
        if len(file.dataset.files) > MAX_DISPLAY_ROWS:
            sleep(0.5)
            progress.remove_task(task_id)
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if len(error_msg) > 80:  # Truncate if longer than 50 characters
            error_msg = error_msg[:77] + "..."
        progress.update(task_id, description=f"[red]✗ {filename} - {error_msg}")
        file.remove()



def download_dataset(dataset: Dataset, max_workers: int = 3) -> bool:
    
    """
    Downloads all files in a dataset to a local directory using parallel threads.
    The local directory is created based on the dataset ID.

    Parameters
    ----------
    dataset : Dataset
        ESGF Dataset object whose files will be downloaded.
    max_workers : int, optional
        Number of parallel download threads. Default is 3.
    """

    dataset.local_path.mkdir(parents=True, exist_ok=True)
    dataset_size = len(dataset.files)
    
    # Create rich Progress instance using the shared console
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,  # Use shared console for consistency
        transient=dataset_size > MAX_DISPLAY_ROWS  # Remove completed tasks if true
    ) as progress:
        
        # Pre-create all progress tasks in chronological order
        file_tasks = []
        for file in dataset.files:
            task_id = progress.add_task(f"[dim]{file.filename} (queued)", total=file.size)
            file_tasks.append((file, task_id))
        
        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks with their pre-created task IDs
            futures = [
                executor.submit(download_file, file, progress, task_id) 
                for file, task_id in file_tasks
            ]
            
            try:
                for f in as_completed(futures):
                    f.result()
            except KeyboardInterrupt:
                # Handle keyboard interrupt: cancel remaining tasks
                global keyboard_interrupt
                keyboard_interrupt = True
                for f in futures:
                    f.cancel()

    return keyboard_interrupt