Change log for Simpl Cloud
==========================

A list of notable changes to the Simpl-Cloud library included in each release.

0.44 (unreleased)
=================

- Nothing changed yet.


0.43 (20 October 2021)
======================

- CSS fix.


0.42 (19 October 2021)
======================

- Hide messages after 5s.


0.41 (18 October 2021)
======================

- Fix missing JS file.


0.40 (18 October 2021)
======================

- Add close button to messages component.


0.39 (18 October 2021)
======================

- Copy revisions for incorrect status on Players screen


0.38 (8 October 2021)
=====================

- Admin interface copy revisions


0.37 (6 October 2021)
=====================

- Add inactive players list to run API.

- Add Class resource to API.

- Remove unused user mutation from API.


0.36 (4 October 2021)
=====================

- Add gameId to SimplRun type in API schema.

- Fix logic in prepare form template displaying copy for prepare status.


0.35 (29 September 2021)
========================

- Copy changes.


0.34 (27 September 2021)
========================

- Text changes for Players page


0.33 (24 September 2021)
========================

- Fix logic for ending and restarting runs.


0.32 (23 September 2021)
========================

- Show correct button to end game in form.

- Fix status arrow showing debrief as current step when run ended.


0.31.3 (22 September 2021)
==========================

- Fix game id query parameter in game API.


0.31.2 (21 September 2021)
==========================

- Add missing message for non continuous runs in players list.


0.31.1 (20 September 2021)
==========================

- Fix condition to display status arrow for debrief.


0.31 (20 September 2021)
========================

- Add optional name to APIToken.

- Templates cleanup
  - remove unused includes
  - use correct form includes in status change pages

- Use new players template layout with includes to allow overrides on smaller elements.

- Allow configuring Run transition steps
  - Run.use_status_prepare
  - Run.use_status_debrief
  - Run.can_end
  - Run.can_restart

- Change class mutation name to avoid reserved word.


0.30 (16 September 2021)
=================

- Dropdown groups added to report styling

- Layout fix on Teams page and UI changes on Status page


0.29 (14 September 2021)
========================

- Add continuous field to game in API.

- Add continuous open field to run in API.

- Fix get play URL method in Run model.


0.28 (13 September 2021)
========================

- Progress UI fixes.


0.27 (13 September 2021)
========================

- Charting UI revisions

- Add classId field to Run in API schema

- Add continuous field to Run in schema

- Remove continuous condition from status arrows template
