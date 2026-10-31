Summary
Rewrite the new implementation of equipments:
Add some attribute to equipments.    

Problem

Changes
add "available_control_state", "overview_schedule_id" to equipment for smartplugs and EVSE 
add "stated_power" to equipment for smartplugs  (stated power gives the power of the device)
add "cable_stated_power" to equipment for EVSE  (cable stated power gives the power max of charging)
it affects the files
    helpers/equipment.py
    equipments.py
    evse.py

Testing
Works fine on my HA.
Fixes https://github.com/asantaga/wiserHomeAssistantPlatform/issues/