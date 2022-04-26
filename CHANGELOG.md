Change log for Simpl Cloud
==========================

A list of notable changes to the Simpl-Cloud library included in each release.

1.0.8 (26 April 2022)
=====================

- Radio button visual bug fix.

1.0.7 (26 April 2022)
=====================

- Style updates.


1.0.6 (6 April 2022)
====================

- Merged v0.58 hotfix.


1.0.5 (28 March 2022)
=====================

- UI revisions for players list and management.


1.0.4 (9 March 2022)
====================

- UI revisions for Team Management on non-continuous games
- UI revisions for Player Management on continuous games
- Copy changes and UI revisions for Game Status page and modals


1.0.3 (18 February 2022)
========================

- Fix instance API schema to allow application to override status field.


1.0.2 (23 December 2021)
========================

- Fix CSS issue with SVG image again.


1.0.1 (23 December 2021)
========================

- Fix CSS issue with SVG image.


1.0 (23 December 2021)
======================

- Add players CSV download.

- Add instructions to manage teams page.

- Redesign UI.


0.60 (26 April 2022)
====================

- Fix visual bug on radio button.


0.59 (26 April 2022)
====================

- Style updates.


0.58 (6 April 2022)
===================

- Fix error building players initials when name has weird characters.


0.57 (6 December 2021)
======================

- Add fields to API:
  - run.instances.dateEnd
  - user.runs.instance.dateEnd
  - user.runs.instance.playerFinished

- Add and fix tests.

- Run tests in GitHub actions.

0.56 (1 December 2021)
======================

- Consider character complete if instance is ended.


0.55 (30 November 2021)
=======================

- Add status property to Character.


0.54 (30 November 2021)
=======================

- Improve the BalanceTeams mutation flexibility some more.

- Better formatting for summary page.

- Fix badges for unfinished session groups, and add a bit of tab styling.


0.53.2 (30 November 2021)
=========================

- Fix issue with initial data loading failure.


0.53.1 (30 November 2021)
=========================

- Update JS static files from v0.53 changes.


0.53 (29 November 2021)
=======================

- Improve sessions handling (don't require times, any string will do).

- Fix bug with auto-balance.

- Add some flexibility to the BalanceTeams graphQL mutation.


0.52 (24 November 2021)
=======================

- Fix run managers API mutation not returning run.


0.51 (22 November 2021)
=======================

- Fix user instance status field on API.

- Fix run setting status correctly when ending non continuous runs.


0.50.1 (15 November 2021)
=========================

- Fix method to finish characters to accept multiple characters.


0.50 (9 November 2021)
======================

- Add date finished field to Character and ability to finish a character from the instance.


0.49 (5 November 2021)
======================

- CSS changes.


0.48 (3 November 2021)
======================

- Remove unnecessary highcharts container styles.


0.47 (2 November 2021)
======================

- Use BooleanField insted of NullBooleanField.


0.46 (28 October 2021)
======================

- Change toggle JS component to work with multiple targets.


0.45 (28 October 2021)
======================

- Text revisions.


0.44 (27 October 2021)
======================

- Add fields to Game and Run to toggle facilitator's ability to disable continuous enrollment.


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
