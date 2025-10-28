FaceFusion
==========

> Industry leading face manipulation platform.

[![Build Status](https://img.shields.io/github/actions/workflow/status/facefusion/facefusion/ci.yml.svg?branch=master)](https://github.com/facefusion/facefusion/actions?query=workflow:ci)
[![Coverage Status](https://img.shields.io/coveralls/facefusion/facefusion.svg)](https://coveralls.io/r/facefusion/facefusion)
![License](https://img.shields.io/badge/license-OpenRAIL--AS-green)


Preview
-------

![Preview](https://raw.githubusercontent.com/facefusion/facefusion/master/.github/preview.png?sanitize=true)


Installation
------------

Be aware, the [installation](https://docs.facefusion.io/installation) needs technical skills and is not recommended for beginners. In case you are not comfortable using a terminal, our [Windows Installer](http://windows-installer.facefusion.io) and [macOS Installer](http://macos-installer.facefusion.io) get you started.


Usage
-----

Run the command:

```
python facefusion.py [commands] [options]

options:
  -h, --help                                      show this help message and exit
  -v, --version                                   show program's version number and exit

commands:
    run                                           run the program
    headless-run                                  run the program in headless mode
    batch-run                                     run the program in batch mode
    force-download                                force automate downloads and exit
    benchmark                                     benchmark the program
    job-list                                      list jobs by status
    job-create                                    create a drafted job
    job-submit                                    submit a drafted job to become a queued job
    job-submit-all                                submit all drafted jobs to become a queued jobs
    job-delete                                    delete a drafted, queued, failed or completed job
    job-delete-all                                delete all drafted, queued, failed and completed jobs
    job-add-step                                  add a step to a drafted job
    job-remix-step                                remix a previous step from a drafted job
    job-insert-step                               insert a step to a drafted job
    job-remove-step                               remove a step from a drafted job
    job-run                                       run a queued job
    job-run-all                                   run all queued jobs
    job-retry                                     retry a failed job
    job-retry-all                                 retry all failed jobs
    repo-init                                     initialize face repository
    repo-add                                      add face to repository
    repo-list                                     list persons in repository
    repo-execute                                  execute face swap with repository
```


Repository System
-----------------

FaceFusion now supports a repository-based face swapping system that automatically selects the optimal face for each video frame based on 3D pose similarity. 

Store multiple face orientations per person and let the system dynamically choose the best match for each frame:

```bash
# Initialize repository
python facefusion.py repo-init

# Add multiple face orientations
python facefusion.py repo-add --person "john" --source john_front.jpg
python facefusion.py repo-add --person "john" --source john_profile.jpg

# Process video with optimal face selection
python facefusion.py repo-execute --person "john" --target video.mp4 --output result.mp4
```

See [REPOSITORY_GUIDE.md](REPOSITORY_GUIDE.md) for detailed documentation.


Documentation
-------------

Read the [documentation](https://docs.facefusion.io) for a deep dive.
