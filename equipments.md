Summary
Rewrite the new implementation of equipments:
Add some attributes to equipment records.

Problem

Changes
add "available_control_states" and "overview_schedule_id" to equipment for smart plugs and EVSE
add "stated_power" to equipment for smart plugs (stated power gives the power of the device)
add "cable_stated_power" to equipment for EVSE (cable stated power gives the maximum charging power)
it affects the files:
    helpers/equipment.py
    equipments.py
    evse.py

Testing
Works fine on my HA.
Fixes https://github.com/asantaga/wiserHomeAssistantPlatform/issues/786
