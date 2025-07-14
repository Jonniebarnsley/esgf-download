import os
import re
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
        Searches ESGF for files in the dataset and returns a list of File objects
        sorted by start date in chronological order.
        Caches the files in the instance variable _files.
        """

        if self._files is None:
            search = self.file_context().search(ignore_facet_check=True)
            file_objects = [File(item, self) for item in search]
            # Sort files by start_date (chronological order)
            self._files = sorted(file_objects, key=lambda f: f.start_date)
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
        self._start_date: Optional[str] = None  # cache for start_date
        self._end_date: Optional[str] = None  # cache for end_date

    def exists(self) -> bool:
        return self.local_path.exists()
    
    def remove(self) -> None:
        """Delete the downloaded file if it exists."""
        if self.exists():
            os.remove(self.local_path)
    
    def _date_range(self) -> tuple[str, str]:
        """
        Extract the start and end dates from the filename.
        
        ESGF filenames follow the pattern:
        variable_table_model_experiment_variant_grid_DATES.nc

        Depending on the frequency, the DATES part of the filename will be different.
        - For yearly data, it will be YYYY-YYYY.
        - For monthly data, it will be YYYYMM-YYYYMM.
        - For daily data, it will be YYYYMMDD-YYYYMMDD.
        - For 3-hourly data, it will be YYYYMMDDhhmm-YYYYMMDDhhmm.
        
        Returns:
            tuple[int, int]: Start date and end date as integers
            
        Raises:
            ValueError: If the date range cannot be extracted from the filename
        """
        # Remove .nc extension and split by underscores
        filename_without_ext = os.path.splitext(self.filename)[0]
        parts = filename_without_ext.split('_')
        
        # The date range should be the last part
        date_part = parts[-1]
        
        # Match various date range patterns:
        # Order matters - longer patterns first to avoid partial matches
        patterns = [
            r'(\d{12})-(\d{12})',   # YYYYMMDDhhmm-YYYYMMDDhhmm (3-hourly)
            r'(\d{8})-(\d{8})',     # YYYYMMDD-YYYYMMDD (daily)
            r'(\d{6})-(\d{6})',     # YYYYMM-YYYYMM (monthly)
            r'(\d{4})-(\d{4})',     # YYYY-YYYY (annual)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_part)
            if match:
                start, end = match.groups()
                return start, end
        
        raise ValueError(f"Could not extract date range from filename: {self.filename}")
    
    @property
    def start_date(self) -> str:
        """Get the start date of the file."""
        if self._start_date is None:
            self._start_date, self._end_date = self._date_range()
        return self._start_date
    
    @property
    def end_date(self) -> str:
        """Get the end date of the file."""
        if self._end_date is None:
            self._start_date, self._end_date = self._date_range()
        return self._end_date