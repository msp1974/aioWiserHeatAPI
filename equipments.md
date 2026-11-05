# Equipment records

Generation 2 hubs include an `Equipment` array in the domain response. These
records complement physical devices with power, scheduling, load-control, and
native notification data.

`devices.equipments` exposes every valid equipment record and supports lookup
by equipment ID or linked device application-instance ID. Hubs that omit the
array expose an empty collection.

Equipment records provide the following optional fields without inventing
defaults for missing values:

- available control states and overview schedule ID;
- stated power for smart plugs;
- cable stated power for EVSE devices;
- under-power and over-power notification settings.

Native power notifications can be created, updated, enabled, disabled, and
deleted. Create and update operations patch the complete notification object.
Deletion uses the notification subresource exposed by the hub.

EVSE devices use the validated control states from their linked equipment
record.
