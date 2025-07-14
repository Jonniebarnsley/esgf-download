import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, \
    TaskProgressColumn, TimeRemainingColumn, TaskID

# local imports
from esgf_download.classes import Dataset, File


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
    if file.exists():
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
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        chunk_size = 8192

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
        
    except requests.exceptions.RequestException as e:
        progress.update(task_id, description=f"[red]✗ {filename} - {e}")
        file.remove()



def download_dataset(dataset: Dataset) -> bool:
    
    """
    Downloads all files in a dataset to a local directory using parallel threads.
    The local directory is created based on the dataset ID.

    Parameters
    ----------
    dataset : Dataset
        ESGF Dataset object whose files will be downloaded.
    """

    dataset.local_path.mkdir(parents=True, exist_ok=True)
    
    # Use ThreadPoolExecutor for parallel downloads
    max_workers = 3  # Adjust this number based on your network and server limits
    
    # Create rich Progress instance
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=None,  # Use default console
        transient=False  # Keep completed tasks visible
    ) as progress:
        
        # Pre-create all progress tasks in chronological order
        file_tasks = []
        for file in dataset.files:
            task_id = progress.add_task(f"[dim]{file.filename} (queued)", total=file.size)
            file_tasks.append((file, task_id))
        
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