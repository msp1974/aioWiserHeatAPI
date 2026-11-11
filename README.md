# Drayton Wiser Hub API Async v1.7.8

An asynchronous Python API for the Drayton Wiser heating system used in the UK.
It supports one-, two-, and three-channel HeatHubs, Smart Plugs, shutters, lights,
and other Wiser devices.

## Requirements

Python 3.12 or later.

## Installation

```sh
python -m pip install aioWiserHeatAPI
```

## Hub setup

### 1. Find your HeatHub secret key

1. Press the setup button on your HeatHub. The light will start flashing.
2. Connect your computer or phone to the Wi-Fi network named `WiserHeatXXXXXX`,
   where `XXXXXX` is the last six digits of the hub's MAC address.
3. Open `http://192.168.8.1/secret` in a browser. Save the returned string as your
   hub's secret key.
4. Press the setup button again to return the HeatHub to normal operation.

See the [HeatHub connection guide](https://it.knightnet.org.uk/kb/nr-qa/drayton-wiser-heating-control/#controlling-the-system)
for more information.

### 2. Find your HeatHub IP address

Use your router's connected-device list to find the HeatHub's IP address. The hub
usually identifies itself as `WiserHeatXXXXXX`.

Hub discovery is also available through the API; see
[discovery.py](aioWiserHeatAPI/discovery.py).

## Documentation

- [API documentation](docs/info.md)
- [API implementation](aioWiserHeatAPI/wiserhub.py)
- [Release history](CHANGELOG.md)
