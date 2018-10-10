from bidso import file_Core


subject = 'bert'

task_ieeg = file_Core(
    subject=subject,
    session='day02',
    modality='ieeg',
    task='motor',
    run='1',
    acquisition='clinical',
    extension='.eeg',
    )

task_fmri = file_Core(
    subject=subject,
    session='day01',
    modality='bold',
    task='motor',
    run='1',
    extension='.nii.gz',
    )

task_anat = file_Core(
    subject=subject,
    session='day01',
    acquisition='wholebrain',
    modality='T1w',
    extension='.nii.gz',
    )

elec_ct = file_Core(
    subject=subject,
    session='day02',
    modality='electrodes',
    acquisition='ct',
    extension='.tsv',
    )

task_fmri_prf = file_Core(
    subject=subject,
    session='day03',
    modality='bold',
    task='bairprf',
    run='1',
    extension='.nii.gz',
    )

task_ieeg_prf = file_Core(
    subject=subject,
    session='day04',
    modality='ieeg',
    task='bairprf',
    run='1',
    acquisition='clinical',
    extension='.eeg',
    )
