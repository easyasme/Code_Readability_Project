""" File for tokenization and event creation """
 
import json
from typing import List
from pathlib import Path
import polars as pl
import pyarrow.dataset as ds
 
from tokenizer import create_vocab
from utils import get_pnrs
from features import (
    create_cls_source,
    create_tokenized_events,
)
 

class DataPipeline:
    """Class for handling everything related to data processing of the Datamodule"""
 
    def __init__(
        self,
        cls_token: bool,
        sep_token: bool,
        segment: bool,
        fill_nulls: bool = False,
        subset_background: bool = False,
    ):
        self.cls_token = cls_token
        self.sep_token = sep_token
        self.segment = segment
        self.fill_nulls = fill_nulls
        self.subset_background = subset_background
 
        # Assigned during __call__
        self.dir_path = None
        self.vocab = None
 
    def __call__(
        self, sources: List[ds.Dataset], background: pl.DataFrame, dir_path: Path = None
    ):
        """Does all data processing required to create features"""
        assert {"person_id", "date_col"}.issubset(
            background.columns
        ), "Required cols: person_id, date_col"
        self.dir_path = dir_path
 
        # Subset background on sources
        if self.subset_background:
            background = self.get_background_subset(sources, background)
        birthdates = background.select("person_id", birthday="date_col")
 
        # Prepend background to sources
        if len(background.columns) > 2:
            sources = [ds.dataset(background.to_arrow())] + sources
 
        # Get cls_token dataframe and prepend to sources
        if self.cls_token:
            cls_source = create_cls_source(birthdates.rename({"birthday": "date_col"}))
            sources = [ds.dataset(cls_source.to_arrow())] + sources
 
        # Get vocab if not computed
        self.vocab = self.get_vocab(sources)
 
        # Get tokenized event Dataset
        tokenized_event = self.get_tokenized_event(sources, self.vocab, birthdates)
 
        return tokenized_event
 
    @staticmethod
    def _load_if_exists(path: Path, backend=None):
        if path.exists():
            print("Loading", path.stem)
            if path.suffix == ".parquet":
                if backend == "arrow":
                    return ds.dataset(path, format="parquet")
                elif backend == "polars":
                    return pl.read_parquet(path)
                else:
                    raise ValueError(
                        "Only 'arrow' or 'polars' backend supported", backend
                    )
            elif path.suffix == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                raise ValueError("Only .parquet and .json files allowed")
        else:
            print("Creating", path.stem)
            return None
 
    def get_background_subset(
        self, sources: List[ds.Dataset], background_df: pl.DataFrame
    ) -> pl.DataFrame:
        """Load or subset background with pnrs of sources"""
        background_subset_path = self.dir_path / "background_subset.parquet"
 
        # Load or subset background
        if (
            background_subset := self._load_if_exists(
                background_subset_path, backend="polars"
            )
        ) is None:
            sources_pnrs = get_pnrs(sources)
            background_subset = background_df.join(
                pl.DataFrame({"person_id": sources_pnrs.tolist()}), on="person_id"
            )
            background_subset.write_parquet(background_subset_path)
        return background_subset
 
    def get_vocab(self, sources: List[ds.Dataset]) -> dict:
        """Load or create the vocabulary"""
        vocab_path = self.dir_path / "vocab.json"
 
        if (vocab := self._load_if_exists(vocab_path)) is None:
            vocab = create_vocab(sources)
            with open(vocab_path, "w", encoding="utf-8") as f:
                json.dump(vocab, f)
        return vocab
 
    def get_tokenized_event(
        self, sources: List[ds.Dataset], vocab: dict, birthdates: pl.DataFrame
    ) -> ds.Dataset:
        """Load or create the tokenized event dataframe"""
 
        tokenized_path = self.dir_path / "tokenized.parquet"
 
        if (
            tokenized_event := self._load_if_exists(tokenized_path, backend="arrow")
        ) is None:
            tokenized_event = create_tokenized_events(
                sources=sources,
                vocab=vocab,
                birthdates=birthdates,
                sep_token=self.sep_token,
                dir_path=self.dir_path,
                segment=self.segment,
                fill_nulls=self.fill_nulls,
            )  # tokenized_event is saved within create_tokenized_events function
        return tokenized_event

