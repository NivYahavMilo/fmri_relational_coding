import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import config
from data_center.static_data.static_data import StaticData


def plot_snr_measurement(group_i, **kwargs):
    if not getattr(StaticData, 'ROI_NAMES'):
        StaticData.inhabit_class_members()

    main_path = config.SNR_RELATIONAL_CODING_RESULTS
    figure_path = config.SNR_RELATIONAL_CODING_RESULTS_FIGURES
    subjects_groups = range(1, 70)
    roi_mean_score = {}
    correlation_matrix_max = {}
    task_range = 10
    w_s = 0
    w_e = 5

    temporal_scores = {}

    for roi in ['RH_Default_pCunPCC_1', 'LH_Default_PFC_15', 'RH_Default_Par_1']:
        temporal_scores[roi] = {}
        correlation_matrix_max[roi] = {}
        rc_integral_score = {}
        for group_amount in subjects_groups:
            temporal_scores[roi][group_amount] = []
            correlation_matrix_max[roi][group_amount] = []

            rc_score = []
            while w_e < 19:
                _range = f'task_end_{task_range}_tr_rest_{w_s}-{w_e}_tr'
                res_path = main_path.format(group_amount=group_amount, group_index=group_i, range=_range)
                roi_path = os.path.join(res_path, f"{roi}.pkl")
                data = pd.read_pickle(roi_path)
                rc_score.append(data['relational_coding_distance'])
                temporal_scores[roi][group_amount].append(data['relational_coding_distance'])

                w_s += 1
                w_e += 1
                correlation_matrix_max[roi][group_amount].append(data['feature_matrix'])

            score = 0
            if kwargs.get('integral'):
                score = np.trapz(rc_score)

            if kwargs.get('mean'):
                score = np.mean(rc_score)

            if kwargs.get('max'):
                score = np.max(rc_score)

            rc_integral_score[group_amount] = score
            w_s = 0
            w_e = 5

        roi_mean_score[roi] = rc_integral_score

    for roi in roi_mean_score.keys():
        plt.plot(roi_mean_score[roi].keys(), roi_mean_score[roi].values(), linewidth=5)
        plt.title(f'SNR Measurement as Subject Group (i={group_i}) function')
        plt.xticks([*range(1, 70, 4)])
        plt.xlabel('Subject Groups')
        plt.ylabel('Average Correlation Window Value')
        plt.ylim([0, .8])
        if kwargs.get('plot_combined_groups'):
            continue

    fig1 = plt.gcf()
    plt.legend([*roi_mean_score.keys()])
    plt.title(f'SNR Measurement as Subject Group (i={group_i}) function')
    plt.show()
    plt.draw()
    fig_dir_path = figure_path.format(group_index=group_i)
    save_fig_path = os.path.join(fig_dir_path, f'{roi}.png')
    if not os.path.exists(fig_dir_path):
        os.makedirs(fig_dir_path)

    if kwargs.get('save_figure'):
        fig1.savefig(save_fig_path, dpi=300)

    if kwargs.get('plot_heatmap'):
        max_corr_key = max(roi_mean_score[roi].values())
        subject_group_max_value = list(roi_mean_score[roi].values()).index(max_corr_key)
        corr_matrix_index = temporal_scores[roi][subject_group_max_value+1].index(max_corr_key)

        max_corr_matrix = correlation_matrix_max[roi][subject_group_max_value+1][corr_matrix_index]

        max_corr_matrix.to_csv(f'clips_voxel_matrix_{roi}_group_{group_i}.csv.')
        sns.heatmap(max_corr_matrix,
                    xticklabels=max_corr_matrix.columns,
                    cmap='hot'
                    )

        fig1 = plt.gcf()
        plt.show()
        plt.draw()
        save_fig_path = os.path.join(fig_dir_path, 'clips_voxel_matrix.png')
        fig1.savefig(save_fig_path, dpi=300)
