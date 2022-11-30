import json
import os
from typing import List, Optional

import config

ROI_NAMES = []
SUBJECTS = ['100610',
            '102311']


class StaticData:
    ROI_NAMES: Optional[List]
    SUBJECTS: Optional[List]

    @classmethod
    def inhabit_class_members(cls):
        """
        load json file
        set class attr
        """
        data_path = os.path.join(config.STATIC_DATA_PATH, 'static_data.json')
        io = open(data_path)
        data = json.load(io)

        for attr, values in data.items():
            setattr(cls, attr, values)
