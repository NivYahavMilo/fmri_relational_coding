import numpy as np

from arithmetic_operations.correlation_and_standartization import z_score


class CustomTemporalRelationalCodingUtils:

    @staticmethod
    def get_rest_window_slides_vectors(data_rest, clip_i, window_size_rest):
        drop_columns = []

        rest_ct = data_rest[data_rest['y'] == clip_i]
        start, end = window_size_rest

        if 'Subject' in rest_ct.columns:
            drop_columns.append('Subject')
        drop_columns.extend(['y', 'timepoint'])

        rest_ct_window = rest_ct[rest_ct['timepoint'].isin(range(start, end))].drop(drop_columns, axis=1)
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
            clip_window = range(init_timepoint - window_size_task+1, init_timepoint+1)

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