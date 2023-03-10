import numpy as np
import pandas as pd

from arithmetic_operations.correlation_and_standartization import z_score
from relational_coding.relational_coding_base import RelationalCodingBase


class CustomTemporalRelationalCodingUtils(RelationalCodingBase):

    def custom_temporal_relational_coding(
            self,
            *,
            data_task,
            data_rest,
            window_size_rest,
            init_window_task,
            window_size_task,
            **kwargs
    ):

        custom_temporal_window_vec = {}
        for clip_i in range(1, 15):
            clip_name = self.get_clip_name_by_index(clip_i)
            task_window_avg = self.get_task_window_slides_vectors(data_task, clip_i, init_window_task, window_size_task)
            rest_window_avg = self.get_rest_window_slides_vectors(data_rest, clip_i, window_size_rest,
                                                                  clip_data=data_task)
            custom_temporal_window_vec[clip_name + '_task'] = task_window_avg
            custom_temporal_window_vec[clip_name + '_rest'] = rest_window_avg

        rc_distance, _ = self.correlate_current_timepoint(data=custom_temporal_window_vec, **kwargs)

        custom_temporal_window_vec = pd.DataFrame(custom_temporal_window_vec)
        return rc_distance, custom_temporal_window_vec

    @staticmethod
    def _add_tr_from_next_clip(window_indices, **kwargs):
        clip_data = kwargs.pop('clip_data')
        next_clip = kwargs.pop('next_clip')
        if next_clip == 15:
            next_clip = 1
        clip_data = clip_data[clip_data['y'] == next_clip]
        if clip_data.empty:
            return pd.DataFrame()

        drop_columns = []
        if 'Subject' in clip_data.columns:
            drop_columns.append('Subject')
        drop_columns.extend(['y', 'timepoint'])

        start_tr, end_tr = window_indices
        new_end_of_clip = end_tr - kwargs['max_rest_tr']

        if start_tr <= kwargs['max_rest_tr']:
            tr_range = range(0, new_end_of_clip)

        else:
            new_start_of_clip = start_tr - kwargs['max_rest_tr']
            tr_range = range(new_start_of_clip, new_end_of_clip)

        clip_data_window = clip_data[clip_data['timepoint'].isin(tr_range)].drop(drop_columns, axis=1)
        return clip_data_window

    def get_rest_window_slides_vectors(self, data_rest, clip_i, window_size_rest, **kwargs):
        drop_columns = []

        rest_ct = data_rest[data_rest['y'] == clip_i]
        start, end = window_size_rest

        if 'Subject' in rest_ct.columns:
            drop_columns.append('Subject')
        drop_columns.extend(['y', 'timepoint'])

        rest_ct_window = rest_ct[rest_ct['timepoint'].isin(range(start, end))].drop(drop_columns, axis=1)

        max_timepoint = max(rest_ct['timepoint'])
        if max_timepoint < end:
            kwargs['max_rest_tr'] = max_timepoint
            extra_clip_window = self._add_tr_from_next_clip(window_indices=window_size_rest, next_clip=clip_i + 1,
                                                            **kwargs)
            rest_ct_window = pd.concat([rest_ct_window, extra_clip_window])

        rest_window_avg = np.mean(rest_ct_window.values, axis=0)
        rest_window_avg_z = z_score(rest_window_avg)

        return rest_window_avg_z

    @staticmethod
    def get_task_window_slides_vectors(data_task, clip_i, init_window, window_size_task):
        drop_columns = []

        clip_ct = data_task[(data_task['y'] == clip_i)]

        if init_window == 'start':
            init_timepoint = clip_ct['timepoint'].min()
            clip_window = range(init_timepoint, window_size_task)

        elif init_window == 'end':
            init_timepoint = clip_ct['timepoint'].max()
            clip_window = range(init_timepoint - window_size_task + 1, init_timepoint + 1)

        elif init_window == 'middle':
            init_timepoint = clip_ct['timepoint'].min() + (clip_ct['timepoint'].max() - clip_ct['timepoint'].min()) // 2
            clip_window = range(init_timepoint - window_size_task // 2, init_timepoint + window_size_task // 2)

        else:
            raise ValueError('init_window value wrong')

        if 'Subject' in clip_ct.columns:
            drop_columns.append('Subject')
        drop_columns.extend(['y', 'timepoint'])

        clip_ct_window = clip_ct[clip_ct['timepoint'].isin(clip_window)].drop(drop_columns, axis=1)
        task_window_avg = np.mean(clip_ct_window.values, axis=0)
        task_window_avg_z = z_score(task_window_avg)

        return task_window_avg_z
