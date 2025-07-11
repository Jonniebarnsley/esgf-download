import os
from pathlib import Path
from typing import Optional
from pyesgf.search.results import FileResult, DatasetResult # type: ignore

class Dataset(DatasetResult):

    def __init__(self, dataset: DatasetResult, data_home: Path = Path(".")):

        # Copy all attributes from the original DatasetResult
        self.__dict__.update(dataset.__dict__)
        self._files: Optional[list] = None  # Cache for files
        self._local_path: Optional[Path] = None  # Cache for local path
        self.data_home = data_home

    @property
    def files(self) -> list:

        """
        Searches ESGF for files in the dataset and returns a list of File objects. 
        Caches the files in the instance variable _files.
        """

        if self._files is None:
            search = self.file_context().search(ignore_facet_check=True)
            self._files = [File(item, self) for item in search]
        return self._files

    @property
    def local_path(self) -> Path:
        
        """
        Generates a local path for the dataset based on its ID.
        The path is structured as:
        <data_home>/<project>/<activity>/<institute>/<model>/<experiment>/<realisation>/
            <time_resolution>/<variable>/gr/<version>/
        where <data_home> is the path to your local data directory. Caches the path in
        the instance variable _local_path.
        """

        if self._local_path is None:
            dataset_id, _ = self.dataset_id.split('|')
            identifiers = dataset_id.split('.')
            self._local_path = self.data_home / Path(*identifiers)
        return self._local_path


class File(FileResult):

    def __init__(self, file: FileResult, dataset: Dataset):
        self.__dict__.update(file.__dict__)
        self.dataset = dataset
        self.local_path = dataset.local_path / file.filename

    def exists(self) -> bool:
        return self.local_path.exists()
    
    def remove(self) -> None:
        """Delete the downloaded file if it exists."""
        if self.exists():
            os.remove(self.local_path)