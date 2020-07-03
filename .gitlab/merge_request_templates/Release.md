Developer checklist
===================

Developer acts as Releaser and goes thru this list of items before, during, and after the development of this new version.

- [ ] Release branch (named `next-release`) from `develop` have been created when the sprint was started
- [ ] This merge request is created for release branch `next-release` to master
  - [ ] Setting `Delete source branch when merge request is accepted` enabled in the MR.
- [ ] Sysop notified that a release is coming
- [ ] Feature implementation happens in Feature branches and Feature branches merged to develop
  - [ ] All branches and changes have been reviewed OR
  - [ ] Some branches and major changes have been reviewed OR
  - [ ] Releaser chose not to review changes properly
- [ ] Infra implementation happens in Salt-repo, (e.g. changes for local_settings.py), and issues linked to in this MR (listed below)
  - [ ] All branches and changes have been reviewed by a sysop OR
  - [ ] Some branches and major changes have been reviewed by a sysop OR
  - [ ] Releaser or sysop chose not to review changes properly
- [ ] Release notes (listed below)
  - [ ] Updated to match changes to be released OR
  - [ ] Releaser chose not to do this properly and only lists the titles of issues OR
  - [ ] Releaser chose not to do this at all
- [ ] Release branch rebased to a commit in develop from where the release is to be made
- [ ] New translations checked
  - [ ] No new translations OR
  - [ ] New translations exists but they are not translated to all supported languages OR
  - [ ] New translations exists and translated to all supported languages OR
  - [ ] Releaser chose not to check new translations
- [ ] New migrations checked (and mentioned in this MR when something special is to be considered)
  - [ ] No new migrations OR
  - [ ] Migrations tested with local database OR
  - [ ] Migrations tested with staging database OR
  - [ ] Releaser chose not to check new migrations
- [ ] Static file generators (compress/collectstatic) checked
  - [ ] Nothing to run OR
  - [ ] Static file generators run successfully in local env OR
  - [ ] Static file generators run successfully in staging env OR
  - [ ] Static file generators run successfully in Gitlab CI OR
  - [ ] Releaser chose not to run static file generators
- [ ] Release branch (this MR) merged to master
  - Release branch `next-release` deleted automatically
- [ ] Build of release revision passed
  - [ ] Locally OR
  - [ ] Gitlab CI OR
  - [ ] Releaser chose not to run build
- [ ] Automatic tests passed
  - [ ] Locally OR
  - [ ] Gitlab CI OR
  - [ ] Releaser chose not to run tests
- [ ] Boilerplate text has been replaced in following four sections below: release notes, changes for infra and local_settings.py, smoke test, and notes.
- [ ] Planned release date is updated
- [ ] To be deployed version number written as the title of this MR
- [ ] Sysop notified that the release is a go

When all top-level boxes above are checked sysop takes over at the planned release date and continues below.


Sysop checklist
===============

- [ ] Sysop confirms all above top-level boxes are checked (deployment is not possible without this and more work and discussions are needed before this gate is passed)
- [ ] Changes to infra and local_settings.py made according to issues linked in this MR
- [ ] Salt applied to server environment
- [ ] Deployment made (code changes)
  - [ ] Everything went smoothly
  - [ ] Works, but there are comments in this MR
  - [ ] Did not work fully, but it is running, and there are comments in this MR
  - [ ] Did not work at all, had to revert back, and there are comments in this MR
- [ ] Backup taken from database
- [ ] Migrations checked and applied
  - [ ] There was nothing to do
  - [ ] Applied, everything went smoothly
  - [ ] Works, but there are comments in this MR
  - [ ] Did not work fully, but it is running, and there are comments in this MR
  - [ ] Did not work at all, had to revert back, and there are comments in this MR
- [ ] Executed data import scripts mentioned in release notes
  - [ ] There was nothing to do
  - [ ] Executed, everything went smoothly
  - [ ] Works, but there are comments in this MR
  - [ ] Did not work fully, but it is running, and there are comments in this MR
  - [ ] Did not work at all, had to revert back, and there are comments in this MR
- [ ] Smoke test
  - [ ] Everything went smoothly
  - [ ] Works, but there are comments in this MR
  - [ ] Did not work fully, but it is running, and there are comments in this MR
  - [ ] Did not work at all, had to revert back, and there are comments in this MR
- [ ] Release tagged in master (`git tag -a -m vX.Y.Z vX.Y.Z master`) as per title of this MR


Release notes
=============

Developers replace this text with human-understandable list of changes introduced in this release.


Changes for infra and local_settings.py
=======================================

Developers replace this text with a list of changes introduced in this release, or comment there are no changes.


Smoke test
==========

Developers replace this text with human-understandable steps how to test that the system is still running after changes introduced in this release.


Notes
=====

Developers replace this text with some important notes, or comment there are no notes.

