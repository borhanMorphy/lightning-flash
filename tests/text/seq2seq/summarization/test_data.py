# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from pathlib import Path

import pytest

from flash.text import SummarizationData
from tests.helpers.utils import _TEXT_TESTING

TEST_BACKBONE = "sshleifer/tiny-mbart"  # super small model for testing

TEST_CSV_DATA = """input,target
this is a sentence one,this is a summarized sentence one
this is a sentence two,this is a summarized sentence two
this is a sentence three,this is a summarized sentence three
"""

TEST_JSON_DATA = """
{"input": "this is a sentence one","target":"this is a summarized sentence one"}
{"input": "this is a sentence two","target":"this is a summarized sentence two"}
{"input": "this is a sentence three","target":"this is a summarized sentence three"}
"""

TEST_JSON_DATA_FIELD = """{"data": [
{"input": "this is a sentence one","target":"this is a summarized sentence one"},
{"input": "this is a sentence two","target":"this is a summarized sentence two"},
{"input": "this is a sentence three","target":"this is a summarized sentence three"}]}
"""


def csv_data(tmpdir):
    path = Path(tmpdir) / "data.csv"
    path.write_text(TEST_CSV_DATA)
    return path


def json_data(tmpdir):
    path = Path(tmpdir) / "data.json"
    path.write_text(TEST_JSON_DATA)
    return path


def json_data_with_field(tmpdir):
    path = Path(tmpdir) / "data.json"
    path.write_text(TEST_JSON_DATA_FIELD)
    return path


@pytest.mark.skipif(os.name == "nt", reason="Huggingface timing out on Windows")
@pytest.mark.skipif(not _TEXT_TESTING, reason="text libraries aren't installed.")
def test_from_csv(tmpdir):
    csv_path = csv_data(tmpdir)
    dm = SummarizationData.from_csv(
        "input", "target", backbone=TEST_BACKBONE, train_file=csv_path, batch_size=1, src_lang="en_XX", tgt_lang="ro_RO"
    )
    batch = next(iter(dm.train_dataloader()))
    assert "labels" in batch
    assert "input_ids" in batch


@pytest.mark.skipif(os.name == "nt", reason="Huggingface timing out on Windows")
@pytest.mark.skipif(not _TEXT_TESTING, reason="text libraries aren't installed.")
def test_from_files(tmpdir):
    csv_path = csv_data(tmpdir)
    dm = SummarizationData.from_csv(
        "input",
        "target",
        backbone=TEST_BACKBONE,
        train_file=csv_path,
        val_file=csv_path,
        test_file=csv_path,
        batch_size=1,
        src_lang="en_XX",
        tgt_lang="ro_RO",
    )
    batch = next(iter(dm.val_dataloader()))
    assert "labels" in batch
    assert "input_ids" in batch

    batch = next(iter(dm.test_dataloader()))
    assert "labels" in batch
    assert "input_ids" in batch


@pytest.mark.skipif(not _TEXT_TESTING, reason="text libraries aren't installed.")
def test_postprocess_tokenizer(tmpdir):
    """Tests that the tokenizer property in ``SummarizationPostprocess`` resolves correctly when a different
    backbone is used."""
    backbone = "sshleifer/bart-tiny-random"
    csv_path = csv_data(tmpdir)
    dm = SummarizationData.from_csv(
        "input", "target", backbone=backbone, train_file=csv_path, batch_size=1, src_lang="en_XX", tgt_lang="ro_RO"
    )
    pipeline = dm.data_pipeline
    pipeline.initialize()
    assert pipeline._postprocess_pipeline.backbone_state.backbone == backbone
    assert pipeline._postprocess_pipeline.tokenizer is not None


@pytest.mark.skipif(os.name == "nt", reason="Huggingface timing out on Windows")
@pytest.mark.skipif(not _TEXT_TESTING, reason="text libraries aren't installed.")
def test_from_json(tmpdir):
    json_path = json_data(tmpdir)
    dm = SummarizationData.from_json(
        "input",
        "target",
        backbone=TEST_BACKBONE,
        train_file=json_path,
        batch_size=1,
        src_lang="en_XX",
        tgt_lang="ro_RO",
    )
    batch = next(iter(dm.train_dataloader()))
    assert "labels" in batch
    assert "input_ids" in batch


@pytest.mark.skipif(os.name == "nt", reason="Huggingface timing out on Windows")
@pytest.mark.skipif(not _TEXT_TESTING, reason="text libraries aren't installed.")
def test_from_json_with_field(tmpdir):
    json_path = json_data_with_field(tmpdir)
    dm = SummarizationData.from_json(
        "input",
        "target",
        backbone=TEST_BACKBONE,
        train_file=json_path,
        batch_size=1,
        field="data",
        src_lang="en_XX",
        tgt_lang="ro_RO",
    )
    batch = next(iter(dm.train_dataloader()))
    assert "labels" in batch
    assert "input_ids" in batch
