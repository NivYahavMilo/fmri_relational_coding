import os

import config
import data_normalizer.utils as utils
from enums import Mode
from relational_coding.relational_coding_base import RelationalCodingBase


class FmriRelationalCoding(RelationalCodingBase):

    def get_clip_vectors(self, rest_data, task_data, timepoint):
        tr_vec = {}
        for clip_i in range(1, 15):
            clip_name = self.get_clip_name_by_index(clip_i)

            task_vector = self.get_single_tr_vector(data=task_data, clip_i=clip_i)
            tr_vec[clip_name + '_task'] = task_vector

            rest_vector = self.get_single_tr_vector(data=rest_data, clip_i=clip_i, timepoint=timepoint)
            tr_vec[clip_name + '_rest'] = rest_vector

        return tr_vec

    def relation_distance(self, d_rest, d_task, shuffle):
        sub_rc_dis = []
        sub_rc_corr = []
        for tr in self.rest_between_tr_generator():
            timepoint_clip_matrix = self.get_clip_vectors(
                rest_data=d_rest,
                task_data=d_task,
                timepoint=tr)

            rc_distance, corr_df = self.correlate_current_timepoint(data=timepoint_clip_matrix, shuffle_rest=shuffle)
            sub_rc_dis.append(rc_distance)
            sub_rc_corr.append(corr_df)
        return sub_rc_dis, sub_rc_corr

    def avg_data_flow(self, roi, res_path, group, shuffle):
        data = {}
        roi_avg_task = self.load_avg_data(roi_name=roi, mode=Mode.CLIPS, group=group)
        roi_avg_rest = self.load_avg_data(roi_name=roi, mode=Mode.REST, group=group)
        sub_rc_dis, df_corr = self.relation_distance(d_rest=roi_avg_rest, d_task=roi_avg_task, shuffle=shuffle)
        # store results in subject id key
        data['avg'] = sub_rc_dis
        data['avg correlation'] = df_corr
        # save subject result
        utils.dict_to_pkl(data, res_path.replace('.pkl', ''))
        print(f'Saved roi {roi}')

    def subject_flow(self, roi, res_path, shuffle):
        data = {}
        for sub_id in self.yield_subject_generator():
            roi_sub_data_task = self.load_roi_data(roi_name=roi, subject=sub_id, mode=Mode.CLIPS)
            roi_sub_data_rest = self.load_roi_data(roi_name=roi, subject=sub_id, mode=Mode.REST)
            sub_rc_dis, _ = self.relation_distance(d_rest=roi_sub_data_rest, d_task=roi_sub_data_task, shuffle=shuffle)
            # store results in subject id key
            data[sub_id] = sub_rc_dis
        # save subject result
        utils.dict_to_pkl(data, res_path.replace('.pkl', ''))
        print(f'Saved roi {roi}')

    def run(self, roi: str, *args, **kwargs):
        avg_data = kwargs['avg_data']
        group = kwargs['group']
        shuffle_rest = kwargs['shuffle']

        if avg_data:
            save_path = os.path.join(config.FMRI_RELATION_CODING_RESULTS_AVG.format(group=group.lower()), f"{roi}.pkl")
            if shuffle_rest:
                save_path = os.path.join(os.path.join(config.FMRI_RELATION_CODING_SHUFFLE_REST_RESULTS, f"{roi}.pkl"))
                if os.path.isfile(save_path):
                    return
            self.avg_data_flow(roi, save_path, group, shuffle_rest)

        else:
            save_path = os.path.join(config.FMRI_RELATION_CODING_RESULTS, f"{roi}.pkl")
            if shuffle_rest:
                save_path = os.path.join(os.path.join(config.FMRI_RELATION_CODING_SHUFFLE_REST_RESULTS, f"{roi}.pkl"))
                if os.path.isfile(save_path):
                    return
            self.subject_flow(roi, save_path, shuffle_rest)
