"""Sub-systems only the UMG 508 serves, beyond the shared measurement block.

No UMG 508 Modbus address list was at hand. These addresses were found on a
real UMG 508 (firmware 5.030) by reading every address and matching what it
returned against values known to be on that meter: its energy counters from
the 19000 block, its CT ratio of 35 A / 1 A, VT 400 V / 400 V, serial number
and firmware release. The layout of each block follows Janitza's address
lists for its other analysers (UMG 509-PRO, UMG 604), at different addresses.

A UMG 508 answers a read that starts in the middle of a variable with
meaningless data rather than an error, so every block here starts exactly
where a variable starts.
"""

from __future__ import annotations

from modbus_connection.model import integer, raw_register, uint32

from .model import JanitzaComponent, measured


class TariffEnergy(JanitzaComponent):
    """Active energy over every tariff, 9929-9944.

    The "frequently required readings" carry consumed energy for tariff 1
    only (19068). These counters add up all tariffs, so they keep counting
    when the meter switches to tariff 2. Each array runs L1, L2, L3, L4,
    L1..L3, L1..L4 (consumed from 9921, delivered from 9933); only the
    L1..L3 sums are read, as one request from 9929, an address the real
    meter answered correctly on its own.
    """

    register_ranges = ((9929, 9944),)

    active_energy_consumed_all_tariffs = measured(9929, unit="Wh")
    """Consumed active energy L1..L3, every tariff (_WH_V[4])."""
    active_energy_delivered_all_tariffs = measured(9941, unit="Wh")
    """Delivered active energy L1..L3, every tariff (_WH_Z[4])."""


class Umg508Transformers(JanitzaComponent):
    """Primary and secondary ratings of each phase's CT and VT, 10131-10162.

    The same names as the UMG 96RM's ``Transformers``, laid out by kind
    rather than by phase: all CT primaries, then all CT secondaries, and so
    on, each for L1 to L4. L4 is not read by name.
    """

    register_ranges = ((10131, 10162),)

    ct_primary_l1 = measured(10131, unit="A")
    ct_primary_l2 = measured(10133, unit="A")
    ct_primary_l3 = measured(10135, unit="A")
    ct_secondary_l1 = measured(10139, unit="A")
    ct_secondary_l2 = measured(10141, unit="A")
    ct_secondary_l3 = measured(10143, unit="A")
    vt_primary_l1 = measured(10147, unit="V")
    vt_primary_l2 = measured(10149, unit="V")
    vt_primary_l3 = measured(10151, unit="V")
    vt_secondary_l1 = measured(10155, unit="V")
    vt_secondary_l2 = measured(10157, unit="V")
    vt_secondary_l3 = measured(10159, unit="V")


# Addresses of the serial number, for a dump that will be shared.
UMG508_SERIAL_NUMBER_REGISTERS = (19916, 19917)


class Umg508Identity(JanitzaComponent):
    """Firmware release and serial number, in the block from 19900.

    Read from 19900, where a read was seen to start cleanly, through the
    serial number at 19916.
    """

    register_ranges = ((19900, 19917),)

    block_start = raw_register(19900)
    """Not a value: anchors the read at 19900, where it was seen to start.

    A read is planned from the first field, and 19908 was never tried as a
    start; without this the read would begin there.
    """
    software_release = integer(19908, signed=False)
    """The release as an integer: 5030 for release 5.030."""
    serial_number = uint32(19916)
