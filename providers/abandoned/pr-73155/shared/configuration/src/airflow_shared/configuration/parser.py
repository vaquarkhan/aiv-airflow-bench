        self, section: str, key: str, fallback=None, **kwargs
    ) -> dict | list | str | int | float | None:
        """
        Return a config value parsed from a JSON string or JSON file.

        If no direct config value is given for ``key``, attempts to read from a file path
        specified by ``key + '_file'``.

        ``fallback`` is *not* JSON parsed but used verbatim when no config value or file is given.
        """
        try:
            data = self.get(section=section, key=key, fallback=None, _extra_stacklevel=1, **kwargs)
        except (NoSectionError, NoOptionError):
            data = None

        if data is None or data == "":
            try:
                file_path = self.get(
                    section=section, key=key + "_file", fallback=None, _extra_stacklevel=1, **kwargs
                )
            except (NoSectionError, NoOptionError):
                file_path = None

            if file_path:
                try:
                    with open(file_path) as f:
                        return json.load(f)
                except Exception as e:
                    raise AirflowConfigException(
                        f"Unable to load json from file {file_path!r} for [{section}] {key!r}"
                    ) from e

            return fallback

        try:
