from __future__ import annotations

import argparse
import datetime
from argparse import BooleanOptionalAction
from pathlib import Path
from textwrap import dedent
    GroupCommand,
    add_auth_token_to_all_commands,
    json_dict_type,
    iso_datetime_type,
    merge_commands,
    safe_call_command,
)
        with pytest.raises(argparse.ArgumentTypeError, match="invalid JSON object"):
            json_dict_type("{not valid json}")

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2026-07-01", datetime.datetime(2026, 7, 1, 0, 0)),
            ("2026-07-01T14:30:00", datetime.datetime(2026, 7, 1, 14, 30, 0)),
        ],
    )
    def test_iso_datetime_type_parses_valid_values(self, value, expected):
        """Valid ISO datetime strings are parsed into datetime objects."""
        assert iso_datetime_type(value) == expected

    def test_iso_datetime_type_rejects_invalid_datetime(self):
        """Invalid datetime strings raise an ArgumentTypeError."""
        with pytest.raises(
            argparse.ArgumentTypeError,
            match="invalid datetime value",
        ):
            iso_datetime_type("not-a-datetime")

    @pytest.mark.parametrize(
        "value",
        ["[]", '"string"', "123", "true", "null"],
