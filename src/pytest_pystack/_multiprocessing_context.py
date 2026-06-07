import multiprocessing

# Ensure the "forkserver" spawn method is never used, because we have
# known incompatibilities with it, while both "fork" and "spawn" work.
MP_CTX = multiprocessing.get_context(
    "fork" if multiprocessing.get_start_method() == "fork" else "spawn"
)
