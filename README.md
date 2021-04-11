# SMM1 Course Archive
## Download all courses and metadata uploaded to Super Mario Maker 1

# Usage
Create `config.json` from `example.config.json` and fill in your console and NNID details
Run `python3 archive.py`

# Meta Data
This script will store the course data and metadata in the `courses` directory
The data stored is as follows
```json
{
    "is_event_course": false,
    "is_official_maker_course": true,
    "world_record": {
        "best_time_pid": 1743322661,
        "first_complete_pid": 1796468065,
        "time_milliseconds": 20854,
        "created_time": 135278005253,
        "updated_time": 135547134545
    },
    "upload_time": 135278005109,
    "course_name": "見た目は丸いがハードな奴だぜ!",
    "creator_pid": 1770179640,
    "user_plays": 519869,
    "clears": 89666,
    "total_attempts": 3138349,
    "failures": 3048683
}
```

# License
License info is located in `license` as well as at the top of `archive.py`