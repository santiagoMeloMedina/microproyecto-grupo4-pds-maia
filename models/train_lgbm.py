from __future__ import annotations

import argparse

import mlflow
import mlflow.lightgbm
import pandas as pd
import yaml
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

from features import CATEGORICAL_COLUMNS, TARGET_COLUMN, prepare_dataset

SCENARIO_KEYS = [
    "data_path",
    "experiment_name",
    "test_size",
    "random_state",
    "n_estimators",
    "learning_rate",
    "num_leaves",
    "max_depth",
    "min_child_samples",
    "reg_alpha",
    "reg_lambda",
    "is_unbalance",
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-path", default="data/airlines.csv")
    parser.add_argument("--experiment-name", default="airlines-delay-lgbm")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-estimators", type=int, default=300)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--num-leaves", type=int, default=63)
    parser.add_argument("--max-depth", type=int, default=8, help="-1 = sin límite (default de LightGBM)")
    parser.add_argument("--min-child-samples", type=int, default=50)
    parser.add_argument("--reg-alpha", type=float, default=0.5)
    parser.add_argument("--reg-lambda", type=float, default=0.5)
    parser.add_argument(
        "--is-unbalance",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Ajusta automáticamente el peso de las clases para compensar el desbalance de Delay "
        "(default: activado; usar --no-is-unbalance para desactivarlo).",
    )
    parser.add_argument(
        "--scenarios-file",
        default=None,
        help="Archivo YAML con una lista de escenarios a correr.",
    )
    return parser.parse_args()


def load_scenarios(scenarios_file: str) -> list[dict]:
    with open(scenarios_file) as f:
        scenarios = yaml.safe_load(f) or []
    if not isinstance(scenarios, list):
        raise ValueError(f"{scenarios_file} debe contener una lista de escenarios")
    return scenarios


def split_time_ordered(df: pd.DataFrame, test_size: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_idx = int(len(df) * (1 - test_size))
    return df.iloc[:split_idx], df.iloc[split_idx:]


def run_scenario(params: dict, run_name: str | None = None) -> dict:
    df = prepare_dataset(params["data_path"])
    train_df, test_df = split_time_ordered(df, params["test_size"])

    X_train = train_df.drop(columns=[TARGET_COLUMN])
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df.drop(columns=[TARGET_COLUMN])
    y_test = test_df[TARGET_COLUMN]

    model_params = {
        "n_estimators": params["n_estimators"],
        "learning_rate": params["learning_rate"],
        "num_leaves": params["num_leaves"],
        "max_depth": params["max_depth"],
        "min_child_samples": params["min_child_samples"],
        "reg_alpha": params["reg_alpha"],
        "reg_lambda": params["reg_lambda"],
        "is_unbalance": params["is_unbalance"],
        "random_state": params["random_state"],
    }

    mlflow.set_experiment(params["experiment_name"])
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(model_params)
        mlflow.log_param("test_size", params["test_size"])

        model = LGBMClassifier(**model_params)
        model.fit(X_train, y_train, categorical_feature=CATEGORICAL_COLUMNS)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }
        mlflow.log_metrics(metrics)
        mlflow.lightgbm.log_model(model, artifact_path="model")

        label = run_name or "default"
        print(f"Escenario '{label}':")
        for name, value in metrics.items():
            print(f"  {name}: {value:.4f}")

        return metrics


def main() -> None:
    args = parse_args()
    base_params = {key: getattr(args, key) for key in SCENARIO_KEYS}

    if args.scenarios_file:
        for scenario in load_scenarios(args.scenarios_file):
            run_name = scenario.pop("name", None)
            params = {**base_params, **scenario}
            run_scenario(params, run_name=run_name)
    else:
        run_scenario(base_params)


if __name__ == "__main__":
    main()
