import multiprocessing

# We have known incompatibilities with the "forkserver" start method.
# The "fork" method is expected to work, but can potentially lead to
# strange failure modes because of things being inherited by our monitor
# process that shouldn't have been. Use "spawn" unconditionally instead.
MP_CTX = multiprocessing.get_context("spawn")
