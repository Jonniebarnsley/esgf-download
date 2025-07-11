import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, \
    TaskProgressColumn, TimeRemainingColumn

# Clean imports now that package is installed
from esgf_download.classes import Dataset, File


# Global keyboard_interrupt instance for thread-safe interrupt handling
keyboard_interrupt = False

def download_file(file: File, progress: Progress) -> None:
    
    """
    Downloads a single file from ESGF to a local directory.

    Parameters
    ----------
    file : File
        File object to download from ESGF.
    progress : Progress
        Progress object to track download progress in ui.
    """
    if file.exists():
        print(f"File {file.filename} already exists, skipping download.")
        return

    url = file.download_url
    if not url:
        print(f"No download URL for file {file.filename}, skipping.")
        return

    filename = file.filename
    filepath = file.local_path
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a task for this file
    task_id = progress.add_task(f"[cyan]{filename}", total=None)
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        chunk_size = 8192

        # Update task with total size
        progress.update(task_id, total=file.size)

        # download with progress tracking
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if keyboard_interrupt:  # Check for shutdown during download
                    progress.update(task_id, description=f"[red]✗ {filename}")
                    file.remove()
                    return
                if chunk:
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))

        # Mark task as completed with speed
        progress.update(task_id, description=f"[green]✓ {filename}")
        file.download_complete = True
        
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
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            futures = [
                executor.submit(download_file, file, progress) 
                for file in dataset.files
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