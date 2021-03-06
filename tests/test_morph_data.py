from google_drive_downloader import GoogleDriveDownloader as gdd
import pytest
from pathlib2 import Path

import ephys.core
import ephys.rigid_pandas

TEST_FOLDER = Path(__file__).resolve().parent
TEST_DATA = TEST_FOLDER / 'test_data'
MORPH_DATA = TEST_DATA / 'morph_data'


@pytest.mark.run(order=0)
def test_download_ephys_data():
    MORPH_DATA.mkdir(parents=True, exist_ok=True)
    dest_path = MORPH_DATA / 'B1096_cat_P04_S02_1.kwik'
    gdd.download_file_from_google_drive(file_id='12bp8fHCC51PWOiX8QxziY7oM7sOxQetA',
                                        dest_path=dest_path.as_posix())
    assert dest_path.exists()


@pytest.mark.run(order=1)
def test_rigid_pandas():
    block_path = MORPH_DATA.as_posix()
    spikes = ephys.core.load_spikes(block_path)

    stims = ephys.rigid_pandas.load_acute_stims(block_path)
    assert len(stims) > 0

    fs = ephys.core.load_fs(block_path)
    stims['stim_duration'] = stims['stim_end'] - stims['stim_start']
    ephys.rigid_pandas.timestamp2time(stims, fs, 'stim_duration')

    stim_ids = stims['stim_name']
    stim_ids = stim_ids.str.replace(b'_rec', '')
    stim_ids = stim_ids.str.replace(b'_rep\d\d', '')
    stims['stim_id'] = stim_ids

    ephys.rigid_pandas.count_events(stims, index='stim_id')

    spikes = spikes.join(ephys.rigid_pandas.align_events(spikes, stims,
                                                         columns2copy=['stim_id',
                                                                       'stim_presentation', 'stim_start', 'stim_duration']))

    spikes['stim_aligned_time'] = (spikes['time_samples'].values.astype('int') -
                                   spikes['stim_start'].values)
    ephys.rigid_pandas.timestamp2time(spikes, fs, 'stim_aligned_time')


@pytest.mark.run(order=1)
def test_kwik2rigid_pandas():
    block_path = MORPH_DATA.as_posix()
    spikes, stims = ephys.rigid_pandas.kwik2rigid_pandas(block_path)
