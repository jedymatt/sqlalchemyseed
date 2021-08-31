def iter_ref_kwargs(kwargs: dict, ref_prefix: str):
    """Iterate kwargs with name prefix or references"""
    for attr_name, value in kwargs.items():
        if attr_name.startswith(ref_prefix):
            # removed prefix
            yield attr_name[len(ref_prefix):], value


def iter_non_ref_kwargs(kwargs: dict, ref_prefix: str):
    """Iterate kwargs, skipping item with name prefix or references"""
    for attr_name, value in kwargs.items():
        if not attr_name.startswith(ref_prefix):
            yield attr_name, value
