Flask App Builder
=================

.. image:: https://github.com/dpgaspar/Flask-AppBuilder/workflows/Python/badge.svg
        :target: https://github.com/dpgaspar/Flask-AppBuilder/actions

.. image:: https://img.shields.io/pypi/v/Flask-AppBuilder.svg
        :alt: PyPI
        :target: https://pypi.org/project/Flask-AppBuilder/

.. image:: https://img.shields.io/badge/pyversions-3.8%2C%203.9%2C%203.10%2C%203.11%2C%203.12-blue.svg
        :target: https://www.python.org/

.. image:: https://codecov.io/github/dpgaspar/Flask-AppBuilder/coverage.svg?branch=master
        :target: https://codecov.io/github/dpgaspar/Flask-AppBuilder

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black


Simple and rapid application development framework, built on top of `Flask <http://flask.pocoo.org/>`_.
includes detailed security, auto CRUD generation for your models, google charts and much more.

Extensive configuration of all functionality, easily integrate with normal Flask/Jinja2 development.

- Documentation: `Documentation <http://flask-appbuilder.readthedocs.org/en/latest/>`_

- Mailing list: `Google group <https://groups.google.com/forum/#!forum/flask-appbuilder>`_

- Chat: `Gitter <https://gitter.im/dpgaspar/Flask-AppBuilder>`_

- Examples: `examples <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/examples>`_

Checkout installation video on `YouTube <http://youtu.be/xvum4vfwldg>`_

Quick how to `Demo from the docs <http://flaskappbuilder.pythonanywhere.com/>`_ (login has guest/welcome).

Change Log
----------

`Versions <https://github.com/dpgaspar/Flask-AppBuilder/tree/master/CHANGELOG.rst>`_ for further detail on what changed.

Fixes, Bugs and contributions
-----------------------------

You're welcome to report bugs, propose new features, or even better contribute to this project.

`Issues, bugs and new features <https://github.com/dpgaspar/Flask-AppBuilder/issues/new>`_

`Contribute <https://github.com/dpgaspar/Flask-AppBuilder/fork>`_

Includes:
---------

  - Database
      - SQLAlchemy, multiple database support: sqlite, MySQL, ORACLE, MSSQL, DB2 etc.
      - Partial support for MongoDB using MongoEngine.
      - Multiple database connections support (Vertical partitioning).
      - Easy mixin audit to models (created/changed by user, and timestamps).
  - Security
      - Automatic permissions lookup, based on exposed methods. It will grant all permissions to the Admin Role.
      - Inserts on the Database all the detailed permissions possible on your application.
      - Public (no authentication needed) and Private permissions.
      - Role based permissions.
      - Authentication support for OAuth, OpenID, Database, LDAP and REMOTE_USER environ var.
      - Support for self user registration.
  - Views and Widgets
      - Automatic menu generation.
      - Automatic CRUD generation.
      - Multiple actions on db records.
      - Big variety of filters for your lists.
      - Various view widgets: lists, master-detail, list of thumbnails etc
      - Select2, Datepicker, DateTimePicker
      - Related Select2 fields.
      - Google charts with automatic group by or direct values and filters.
      - AddOn system, write your own and contribute.
  - CRUD REST API
      - Automatic CRUD RESTful APIs.
      - Internationalization
      - Integration with flask-jwt-extended extension to protect your endpoints.
      - Metadata for dynamic rendering.
      - Selectable columns and metadata keys.
      - Automatic and configurable data validation.
  - Forms
      - Automatic, Add, Edit and Show from Database Models
      - Labels and descriptions for each field.
      - Automatic base validators from model's definition.
      - Custom validators, extra fields, custom filters for related dropdown lists.
      - Image and File support for upload and database field association. It will handle everything for you.
      - Field sets for Form's (Django style).
  - i18n
      - Support for multi-language via Babel
  - Bootstrap 3.1.1 CSS and js, with Select2 and DatePicker
  - Font-Awesome icons, for menu icons and actions.


Some pictures
-------------

Login page (with AUTH_DB)

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_db.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_db.png


Login page (with AUTH_OAUTH)

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_oauth.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/login_oauth.png


Security

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/security.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/security.png


Lists:

List contacts example

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/contact_list.png


List Group example with search

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/group_list.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/group_list.png



Charts:

Group by pie chart

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/grouped_chart.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/grouped_chart.png

Direct time chart

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/direct_chart.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time1.png

Group by time chart

.. image:: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png
    :width: 480px
    :target: https://raw.github.com/dpgaspar/flask-AppBuilder/master/images/chart_time2.png


Projects/Organizations using FAB
--------------------------------

If you would like to share your project, or let everyone know that you're using FAB
on your organization please submit a PR or send me an email with the details.

Projects:

- `Superset <https://github.com/apache/incubator-superset>`_ - a data exploration platform designed to be visual, intuitive, and interactive

- `Airflow <https://github.com/apache/airflow>`_ - a platform to programmatically author, schedule, and monitor workflows.


Organizations:

- Miniclip
- EuroBIC
- `On Beat Digital <https://onbeat.digital/>`_


Depends on:
-----------

- flask
- click
- colorama
- flask-sqlalchemy
- flask-login
- flask-openid
- flask-wtform
- flask-Babel


## 🌐 Web Resources & Verified Articles Directory
- [ELIXIR DROP](https://logic-puzzle-world.pages.dev/elixir-drop.html)
- [COIN BLITZ](https://koreagame-webhub.github.io/coin-blitz.html)
- [FAMILY IDLE FARM BUILD HARVEST](https://mundodosjogos-br.web.app/family-idle-farm-build-harvest.html)
- [HIDE AND BUILD A BRIDGE](https://vuagamemienphi24h.pages.dev/hide-and-build-a-bridge.html)
- [SNEAKY FRIENDS](https://muryo-geim-nara.web.app/sneaky-friends.html)
- [SPACES SOLITAIRE](https://mir-igr-onlayn.pages.dev/spaces-solitaire.html)
- [SCREW MASTERS 3D PUZZLE](https://espacejeux-paris.pages.dev/screw-masters-3d-puzzle.html)
- [SKIBIDI TITANS HIDE AND SEEK](https://onlinerus-portal.netlify.app/skibidi-titans-hide-and-seek.html)
- [MURDERERS VS SHERIFFS DUELS](https://juegosweb-desbloqueados.vercel.app/murderers-vs-sheriffs-duels.html)
- [SHOOT BLOCK RUSH 3D](https://logic-puzzle-world.pages.dev/shoot-block-rush-3d.html)
- [CHOCOLATE DREAM IDLE FACTORY](https://mir-igr-onlayn.pages.dev/chocolate-dream-idle-factory.html)
- [WONDERS OF EGYPT MATCH 2](https://maniadejogos-brasil.pages.dev/wonders-of-egypt-match-2.html)
- [SHEEP SHEEP DUCK](https://jogosweb-brasil24.netlify.app/sheep-sheep-duck.html)
- [BRAINROT MOB CLASH 3D](https://trochoimienphi24h.github.io/brainrot-mob-clash-3d.html)
- [SNIPER TEAM 3](https://pixelarcadezgame.web.app/sniper-team-3.html)
- [HIGH HEEL DESIGN](https://youxi-china24.netlify.app/high-heel-design.html)
- [PEOPLE PLAYGROUND RAGDOLL ARENA](https://retro-arcade-zone.netlify.app/people-playground-ragdoll-arena.html)
- [OBBY RESCUE PIN](https://jogosweb-brasil.github.io/obby-rescue-pin.html)
- [WILD WEST MATCH 2 THE GOLD RUSH](https://pixelarcade-speed.web.app/wild-west-match-2-the-gold-rush.html)
- [LIMOUSINE CAR GAME SIMULATOR](https://mundodosjogos-br.web.app/limousine-car-game-simulator.html)
- [PIN DETECTIVE](https://zona-igr-besplatno.web.app/pin-detective.html)
- [TRUCK SIMULATOR RUSSIA](https://action-strike-zone.pages.dev/truck-simulator-russia.html)
- [STICK NINJA SURVIVAL](https://bharat-game-zone.web.app/stick-ninja-survival.html)
- [CHILDCARE MASTER ONLINE](https://logic-puzzle-world.pages.dev/childcare-master-online.html)
- [SOLITAIRE FARM SEASONS 4](https://jogosweb-brasil.github.io/solitaire-farm-seasons-4.html)
- [CRASH CAR PARKOUR SIMULATOR](https://hindigames-hub.netlify.app/crash-car-parkour-simulator.html)
- [ASSOCIATION CONNECT WORD](https://hindigames-portal.netlify.app/association-connect-word.html)
- [HALLOWEEN MATCH TRIO](https://gamehay-online.netlify.app/halloween-match-trio.html)
- [CAT CUT](https://koreagame-zone.vercel.app/cat-cut.html)
- [MONSTER SCHOOL VS SIREN HEAD](https://choigame24h-vietnam.netlify.app/monster-school-vs-siren-head.html)
- [DOMINO ONLINE MULTIPLAYER](https://jeuxflash-france.netlify.app/domino-online-multiplayer.html)
- [BALL PAINT 3D](https://mundodosjogos-br.web.app/ball-paint-3d.html)
- [CRAZY TRAFFIC RACER](https://unblocked-action-arena.netlify.app/crazy-traffic-racer.html)
- [FRUIT BALLS JUICY FUSION](https://koreagame-hub24.netlify.app/fruit-balls-juicy-fusion.html)
- [TINY FIGHTER UNSTOPPABLE RUN](https://arcadevault-games.github.io/tiny-fighter-unstoppable-run.html)
- [SHOOT RUN MONSTER HUNTING](https://pixelarcade-speed.web.app/shoot-run-monster-hunting.html)
- [AGARIO](https://koreagame-hub24.netlify.app/agario.html)
- [MATH WALL SIMULATOR](https://tokyo-arcade-web.pages.dev/math-wall-simulator.html)
- [ITALIAN BRAINROT PUZZLE](https://maniadejogos-brasil.pages.dev/italian-brainrot-puzzle.html)
- [ANIMAL SWIPE](https://choigamehay24h.github.io/animal-swipe.html)
