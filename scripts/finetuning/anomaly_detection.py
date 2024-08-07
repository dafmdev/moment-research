import argparse

import torch

from moment.common import PATHS
from moment.tasks.anomaly_detection_finetune import AnomlayDetectionFinetuning
from moment.utils.config import Config
from moment.utils.utils import control_randomness, make_dir_if_not_exists, parse_config

NOTES = "Supervised finetuning on anomaly detection datasets"

SMALL_DATASETS = [
    "/TimeseriesDatasets/anomaly_detection/TSB-UAD-Public/KDD21/140_UCR_Anomaly_InternalBleeding4_1000_4675_5033.out",
    "/TimeseriesDatasets/anomaly_detection/TSB-UAD-Public/KDD21/176_UCR_Anomaly_insectEPG4_1300_6508_6558.out",
    "/TimeseriesDatasets/anomaly_detection/TSB-UAD-Public/KDD21/180_UCR_Anomaly_ltstdbs30791ES_20000_52600_52800.out",
    "/TimeseriesDatasets/anomaly_detection/TSB-UAD-Public/KDD21/193_UCR_Anomaly_s20101m_10000_35774_35874.out",
]


def control_experiment_arguments(args, finetuning_mode, dataset_names):
    # Setup arguments
    args.finetuning_mode = finetuning_mode
    args.dataset_names = dataset_names

    if args.dataset_names in SMALL_DATASETS:
        args.train_ratio = 0.4
        args.val_ratio = 0.3
        args.test_ratio = 0.3

    return args


def anomaly_detection(
    config_path: str = "configs/anomaly_detection/linear_probing.yaml",
    default_config_path: str = "configs/default.yaml",
    gpu_id: int = 0,
    finetuning_mode: str = "linear-probing",
    dataset_names: str = "/TimeseriesDatasets/anomaly_detection/TSB-UAD-Public/KDD21/163_UCR_Anomaly_apneaecg2_10000_20950_21100.out",
) -> None:
    config = Config(
        config_file_path=config_path, default_config_file_path=default_config_path
    ).parse()

    # Control randomness
    control_randomness(config["random_seed"])

    # Set-up parameters and defaults
    config["device"] = gpu_id if torch.cuda.is_available() else "cpu"
    config["checkpoint_path"] = PATHS.CHECKPOINTS_DIR
    args = parse_config(config)
    make_dir_if_not_exists(config["checkpoint_path"])

    # Control experiment arguments
    args = control_experiment_arguments(args, finetuning_mode, dataset_names)
    print(f"Running experiments with config:\n{args}\n")

    # args.debug = True
    task_obj = AnomlayDetectionFinetuning(args=args)

    # Setup a W&B Logger
    task_obj.setup_logger(notes=NOTES)
    task_obj.train()

    task_obj.test()

    # End the W&B Logger
    task_obj.end_logger()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=str, default="configs/default.yaml", help="Path to config file"
    )
    parser.add_argument("--gpu_id", type=int, default=0, help="GPU ID to use")
    parser.add_argument(
        "--finetuning_mode", type=str, default="linear-probing", help="Fine-tuning mode"
    )  # linear-probing end-to-end-finetuning
    parser.add_argument(
        "--dataset_names",
        type=str,
        help="Name of dataset(s)",
        default="/TimeseriesDatasets/anomaly_detection/TSB-UAD-Public/KDD21/163_UCR_Anomaly_apneaecg2_10000_20950_21100.out",
    )

    args = parser.parse_args()

    anomaly_detection(
        config_path=args.config,
        gpu_id=args.gpu_id,
        finetuning_mode=args.finetuning_mode,
        dataset_names=args.dataset_names,
    )
