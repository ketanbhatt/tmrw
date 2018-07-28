# Changelog
All notable changes to this project will be documented in this file.

## 2018-07-28
### Added
- *New Frontend for tmrw*


## 2018-06-06
### Added
- Autosave if idle for 1 minute
- Some colors to scrum render

### Fixed
- Ordering of day entries on the admin
- Zero padding of minutes


## 2018-05-28
### Added
- Display time in "hh:mm hrs" format

### Changed
- Combined both `StartEndTimeLog` and `ManualTimeLog` in one model
- Made `order` readonly on `ScrumEntry`

### Fixed
- Fixed bug where Day Entry has to be saved twice to calculate total time logged


## 2018-05-27
### Added
- Add Scrum and log time for each task
- Journal your days easily
- Tag your scrum tasks, journal entries and days separately
- Be able to write notes for each day, scrum task and journal entry
- Get total time logged for each day
- Get time logged for each tag for each day
- Define scrum tasks that will automatically get added every time a new day is started
- Define journaling questions that will automatically get added every time a new day is started
- Render the full day on a basic HTML template