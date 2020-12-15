.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================
Stock Tier Validation
=====================

This module extends the functionality of pickings to support a tier
validation process.

Installation
============

This module depends on ``base_tier_validation``. You can find it at
`OCA/server-ux <https://github.com/OCA/server-ux>`_

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Technical > Tier Validations > Tier Definition*.
#. Create as many tiers as you want for Stock Picking model.

Usage
=====

To use this module, you need to:

#. Create a Picking triggering at least one "Tier Definition".
#. Click on *Request Validation* button.
#. Under the tab *Reviews* have a look to pending reviews and their statuses.
#. Once all reviews are validated click on *Confirm*.

Additional features:

* You can filter the pikcings requesting your review through the filter *Needs my
  Review*.
* User with rights to confirm the picking (validate all tiers that would
  be generated) can directly do the operation, this is, there is no need for
  her/him to request a validation.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/142/12.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/BADEP/addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Khalid Hazam <k.hazam@badep.ma>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://badep.ma/logo.png
   :alt: BADEP
   :target: https://badep.ma

This module is maintained by BADEP.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://github.com/BADEP/addons.
