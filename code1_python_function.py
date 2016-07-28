def is_it_python_job(job):
    if "python" in job.title and ("developer" in job.title or "programmer" in job.title):
        job.labels.add("it/developers/python")
