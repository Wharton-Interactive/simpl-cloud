=========================
Wharton Interactive Simpl
=========================

Base models and API for Django-based simulations.

Provides an API compatible with the  Wharton Interactive marketplace.

Getting Started
===============

Install simpl-cloud, with the API extras if required::

    pip install simpl-cloud[api]

Add simpl to your project's Django settings module, along with the following
settings::

    INSTALLED_APPS = {
        # ...
        'simpl',
    }
    SIMPL_GAME_EXPERIENCE = "simpl.GameExperience"
    SIMPL_RUN = "simpl.Run"
    SIMPL_INSTANCE = "simpl.Instance"
    SIMPL_CHARACTER = "simpl.Character"
    SIMPL_PLAYER = "simpl.Player"
    SIMPL_LOGOUT_URL_NAME = "logout"

Add the following to your project's URL conf::

    urlpatterns = [
      # ...
      path("simpl/", include("simpl.urls")),
    ]


Architecture Overview
=====================

``Run`` objects provide management and configuration of one or more game instances.

Navigation
----------

Provide a function to the ``SIMPL_SETUP_NAV`` setting. It should accept a Run
object as an argument and return a dictionary of keys as Simpl URL names and the
values as a dictionary with the name, optional hint, and one of the
following statuses:

- ``simpl.nav.DISABLED`` (and unstarted)
- ``simpl.nav.UNSTARTED``
- ``simpl.nav.INCOMPLETE``
- ``simpl.nav.READY``
- ``simpl.nav.COMPLETE``

For example::

    return {
        "config": {
            "name": "Game Configuration",
            "status": nav.UNSTARTED,
        },
        "team": {
            "name": "Manage Teams",
            "status": nav.DISABLED,
        },
        "start": {
            "name": "Start Game",
            "status": nav.DISABLED,
        },
    }

Provide a function to the ``SIMPL_PLAY_NAV`` setting. It should accept a Run
object as an argument and return a dictionary of keys as Simpl URL names and the
values as a dicitonary with the name and one of the following statuses:

- ``simpl.constants.DISABLED``
- ``simpl.constants.READY``

Launching game instances
------------------------

When a player is added to a run, their details are stored in a ``Player``
object.

When they start playing your game, they will be attached to an ``Character``
object in a game ``Instance`` object that will track the progress of their game.

For multiplayer runs, these players will be initially grouped into ``Lobby``
object so they can be assigned to a game Instances. A lobby can be marked as
``ready`` once it is ready to start.

You can use ``Run.prepare`` to create new game ``Instance`` objects or manually
create these.

Game play URL
~~~~~~~~~~~~~

The API uses a customizable url endpoint for players. You can specify this by
using a custom ``Player`` model and overriding ``Player.get_play_url``.

Alternatively, you can specify a ``SIMPL_GET_PLAY_URL`` in your settings as a
dotted path to a function that receives a player instance and returns the
correct url.


Run status
--------------

A run has the following statuses:

* Set up (initial state, until any configuration options are provided)

* Players prepare (optional step to if your game experience if players can
  interact with their Instance before gameplay starts)

* Running (game Instances are running)

* Debrief (optional step if your game experience provides a different interface
  after gameplay finishes)

Game Instance status
--------------------

Each game Instance also has a status:

* Preparing - waiting to start (``Instance.date_start`` unset)

* Playing - game in progress (``Instance.date_start`` set but
  ``Instance.date_end`` unset)

* Ended - game complete (``Instance.date_end`` set)

Player status
-------------

Your app may mark a player as having ``completed`` the game (with a date).


Custom models
=============

Extend the Simpl Django models by overriding the default classes in your
project's Django settings module:

* ``Instance`` via ``SIMPL_INSTANCE = "your_app.YourInstance"``

* ``Character`` via ``SIMPL_CHARACTER = "your_app.YourCharacter"``

* ``GameExperience`` (only if your app provides multiple different game
  experiences)  via ``SIMPL_GAME_EXPERIENCE = "your_app.YourGameExperience"``

More rarely, you may also want to override the run and player:

* ``Run`` via ``SIMPL_RUN = "your_app.YourRun"``

* ``Player`` via ``SIMPL_PLAYER = "your_app.YourPlayer"``

Your overridden classes should subclass the related ``simpl.models.Base*``
abstract models.

The Character class will need two related abstract models, ``BaseCharacterData``
and ``BaseCharacterLinked``. This is to make it possible to have character data
as a template, not linked to a user or instance.
