import argparse
from omegaconf import OmegaConf


def process_config():
    parser = argparse.ArgumentParser(description="Process configuration.")
    parser.add_argument(
        "--config", type=str, help="Path to the config file", default="conf/config.yaml"
    )
    args = parser.parse_args()
    conf = OmegaConf.load(args.config)
    return conf
