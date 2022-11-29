import glob
import os
from typing import Optional

import pandas as pd

import config
from data_normalizer.utils import _load_pkl, _info
from enums import Mode


class Voxel2Roi:

    def __init__(self, mode: Mode):

        self.mode: Mode = mode
        self.network_mapping: pd.DataFrame = Optional[pd.DataFrame]
        self.voxel_mapping: pd.DataFrame = Optional[pd.DataFrame]

    def load_voxel_mapping_file(self, roi: int, nw: int, mm: int = 1):
        self.network_mapping = pd.read_csv(os.path.join(config.MAPPING_FILES,
                                                        config.NETWORK_MAPPING_TEMPLATE_FILE.format(roi=roi, nw=nw,
                                                                                                    mm=mm)))

        self.voxel_mapping = pd.read_csv(os.path.join(config.MAPPING_FILES,
                                                      config.VOXEL_MAPPING_FILE.format(roi=roi, nw=nw)))
        self.voxel_mapping['ROI'].astype(int)

    def _get_voxels_by_roi(self, data: pd.DataFrame, roi: str):
        ROI = self.network_mapping[self.network_mapping['ROI Name'] == roi][['ROI Name', 'ROI Label']]
        roi_i = ROI['ROI Label'].apply(lambda x: x - 1).values[0]
        sub_net = ROI['ROI Name'].values[0]

        voxel_indices = self.voxel_mapping[self.voxel_mapping['ROI'] == roi_i].index.tolist()
        voxel_indices = [f'feat_{str(i)}' for i in voxel_indices]
        voxel_indices.extend(['timepoint', 'y', 'Subject'])
        masked_roi = data.loc[:, voxel_indices]
        return masked_roi

    def _save_roi_file(self, data: pd.DataFrame, roi_name: str, subject: str):
        roi_name = roi_name.replace('7Networks_', '')
        sub_path = os.path.join(config.SUBNET_DATA_DF.format(mode=self.mode.value), subject)
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)

        file_name = os.path.join(sub_path, f"{roi_name}.pkl")
        data.to_pickle(file_name)

    def load_data_per_subject(self):
        subjects_voxel_data = glob.glob(os.path.join(config.VOXEL_DATA_DF.format(mode=self.mode.value), '*.pkl'))

        for sub_file in subjects_voxel_data:
            sub_id = sub_file.split('.pkl')[0][-6:]
            sub_data = _load_pkl(sub_file)
            ROIS = self.network_mapping['ROI Name'].unique()
            for r in ROIS:
                roi_data = self._get_voxels_by_roi(data=sub_data, roi=r)
                self._save_roi_file(data=roi_data, roi_name=r, subject=sub_id)
            _info(f"Subject {sub_id} saved")

    def flow(self):
        self.load_voxel_mapping_file(roi=300, nw=7)
        self.load_data_per_subject()


if __name__ == '__main__':
    v2r = Voxel2Roi(mode=Mode.REST)
    v2r.flow()
    del v2r
    v2r = Voxel2Roi(mode=Mode.CLIPS)
    v2r.flow()
