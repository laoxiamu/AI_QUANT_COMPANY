from argparse import Namespace

from carry.cli import authorization_errors


def test_real_data_cli_fails_closed_without_review_and_seal_confirmations() -> None:
    missing = Namespace(
        confirm_prereg_approved=False,
        confirm_holdout_sealed=False,
        confirm_preholdout_only=False,
    )
    approved = Namespace(
        confirm_prereg_approved=True,
        confirm_holdout_sealed=True,
        confirm_preholdout_only=True,
    )

    assert len(authorization_errors(missing)) == 3
    assert authorization_errors(approved) == []
