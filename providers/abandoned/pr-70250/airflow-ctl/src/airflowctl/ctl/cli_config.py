    return parsed


def iso_datetime_type(val: str) -> datetime.datetime:
    """Parse an ISO-8601 datetime string."""
    try:
        return datetime.datetime.fromisoformat(val)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"invalid datetime value: {val!r}"
        ) from e


def _load_help_texts_yaml() -> dict[str, dict[str, str]]:
    """Load the help texts yaml for the auto-generated commands."""
    help_texts_path = Path(__file__).parent / "help_texts.yaml"
            "dict": json_dict_type,
            "tuple": tuple,
            "set": set,
            "datetime.datetime": iso_datetime_type,
            "dict[str, typing.Any]": json_dict_type,
        }
        # Default to ``str`` to preserve previous behaviour for any unrecognised
