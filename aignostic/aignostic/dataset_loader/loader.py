import pandas as pd
from typing import Optional
import os


class DatasetLoader:
    def __init__(self, dataset_path: str, dataset_type: str = "csv"):
        self.dataset_path = dataset_path
        self.dataset_type = dataset_type
        self._dataset: Optional[pd.DataFrame] = None

    def load_dataset(self):
        """
        Load the dataset into memory if it's not already loaded.
        """
        if self._dataset is None:
            if not os.path.exists(self.dataset_path):
                raise RuntimeError(f"Dataset file not found: {self.dataset_path}")

            try:
                if self.dataset_type == "csv":
                    self._dataset = pd.read_csv(self.dataset_path)
                elif self.dataset_type == "json":
                    self._dataset = pd.read_json(self.dataset_path)
                else:
                    raise ValueError("Unsupported dataset type")

                # Validate the dataset (e.g., check for non-empty)
                if self._dataset.empty:
                    raise ValueError("Loaded dataset is empty")

            except Exception as e:
                raise RuntimeError(f"Error loading dataset: {e}")

        return self._dataset

    def reload_dataset(self):
        """
        Force reload the dataset from the file.
        """
        self._dataset = None
        return self.load_dataset()

    def get_dataset(self):
        """
        Get the loaded dataset without reloading.
        """
        if self._dataset is None:
            self.load_dataset()
        return self._dataset
