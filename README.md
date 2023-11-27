# DEPRECATED AND ARCHIVED
# SEE https://github.com/PretendoNetwork/archival-tools FOR THE LATEST UPDATES

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
    "is_official_maker_course": false,
    "world_record": {
        "best_time_pid": 1789569249,
        "first_complete_pid": 1745762670,
        "time_milliseconds": 32224,
        "created_time": 135504152813,
        "updated_time": 135581212346
    },
    "miis": {
        "creator": {
            "nnid": "lokh-cel",
            "mii_data": "QlBGQwAAAAEAAAAAAAAAAAAAAAAAAQAAAwAAQAoEukWgJJCg1y2zTRLuST2wjAAAKSNMAG8AawBoADQAAABFAAAAAAAAAD4uAEBUBlRpRRrANEYUgRIBaA0AACnBUUhQQwDpAGMA6QAAAAAAAAAAAAAAAAAAAEnAAAAAAAAAAAAAAAAAAAAAAAAAAAU="
        },
        "world_record": {
            "nnid": "cmiles1",
            "mii_data": "QlBGQwAAAAEAAAAAAAAAAAAAAAAAAQAAAAAAQICDOaSAxGDw09yOuWjyHfIgOQAAAABtAGkAbABlAHMAAABFAAAAAAAAAEBApABMADEGghQMIoUOgxIIaA4AACmAQUhQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAI+NAAAAAAAAAAAAAAAAAAAAAAAAAAE="
        },
        "first_complete": {
            "nnid": "alesca1984",
            "mii_data": "QlBGQwAAAAEAAAAAAAAAAAAAAAAAAQAAAwAAQKHzISgmB+HS2H8zxTQMTlqSzwAAACxzAGMAYQBnAGwAaQBvADgANAAAAGJEAABrAQJoRBgmNEYUgRIXaA0ABCkAUkhQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0+AAAAAAAAAAAAAAAAAAAAAAAAAAg="
        }
    },
    "stars": 9,
    "upload_time": 135504150772,
    "course_name": "Super Mario One-Screen 1-1",
    "creator_pid": 1752128461,
    "user_plays": 62,
    "clears": 36,
    "total_attempts": 154,
    "failures": 118
}
```

# License
License info is located in `license` as well as at the top of `archive.py`
