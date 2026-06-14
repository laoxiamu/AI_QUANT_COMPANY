import numpy as np
import pandas as pd
import pytest

from carry.metrics import (
    cluster_bootstrap_pvalue,
    compute_metrics,
    moving_block_bootstrap_pvalue,
    three_way_walk_forward,
)


def test_metric_calculator_reports_frozen_acceptance_inputs() -> None:
    index = pd.date_range("2021-01-01", periods=8, freq="180D", tz="UTC")
    returns = pd.Series(
        [0.10, -0.04, 0.08, 0.02, -0.01, 0.05, 0.03, 0.01],
        index=index,
    )

    metrics = compute_metrics(returns)
    wf = three_way_walk_forward(returns)

    assert metrics["net_expected_return"] == pytest.approx(returns.mean())
    assert metrics["profit_factor"] == pytest.approx(5.8)
    assert metrics["positive_year_ratio"] > 0.5
    assert metrics["geometric_growth"] > 0.0
    assert metrics["max_drawdown"] < 0.0
    assert len(wf) == 3
    assert [segment["segment"] for segment in wf] == [1, 2, 3]


def test_block_bootstrap_one_sided_pvalue_detects_positive_mean() -> None:
    positive = np.tile([0.010, 0.020, 0.015, 0.025], 50)
    result = moving_block_bootstrap_pvalue(
        positive,
        block_size=8,
        iterations=2_000,
        seed=20260615,
    )

    assert result["observed_mean"] == pytest.approx(0.0175)
    assert 0.0 < result["p_value"] < 0.05


def test_cluster_bootstrap_handles_known_null_distribution() -> None:
    values = np.repeat(np.tile([-0.01, 0.01], 10), 2)
    clusters = np.repeat(np.arange(20), 2)
    result = cluster_bootstrap_pvalue(
        values,
        clusters,
        iterations=2_000,
        seed=20260615,
    )

    assert result["observed_mean"] == pytest.approx(0.0)
    assert 0.20 < result["p_value"] < 0.80
