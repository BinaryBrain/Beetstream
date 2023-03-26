# Beetstream

Beetstream is a [Beets.io](https://beets.io) plugin that exposes [SubSonic API endpoints](http://www.subsonic.org/pages/api.jsp), allowing you to stream your music everywhere.

## Motivation

I personally use Beets to manage my music library on a Raspberry Pi but when I was looking for a way to stream it to my phone I couldn't find any comfortable, suitable and free options.  
I tried [AirSonic](https://airsonic.github.io) and [SubSonic](http://www.subsonic.org), [Plex](https://www.plex.tv) and some other tools but a lot of these solutions want to manage the library as they need (but I prefer Beets) and AirSonic/SubSonic were quite slow and CPU intensive and seemed to have a lot of overhead just to browse albums and send music files. Thus said, SubSonic APIs are good and implemented by a lot of different [clients](#supported-clients), so I decided to re-implement the server side but based on Beets database (and some piece of code).

## Install & Run

Requires Python 3.8 or newer.

1) First of all, you need to [install Beets](https://beets.readthedocs.io/en/stable/guides/main.html):

2) Install the dependancies with:

```
$ pip install beetstream
```

3) Enable the plugin for Beets in your config file `~/.config/beets/config.yaml`:
```yaml
plugins: beetstream
```

4) **Optional** You can change the host and port in your config file `~/.config/beets/config.yaml`.  
You can also chose to never re-encode files even if the clients asks for it with the option `never_transcode: True`. This can be useful if you have a weak CPU or a lot of clients.

Here are the default values:
```yaml
beetstream:
  host: 0.0.0.0
  port: 8080
  never_transcode: False
```

5) Run with:
```
$ beet beetstream
```

## Clients Configuration

### Authentication

There is currently no security whatsoever. You can put whatever user and password you want in your favorite app.

### Server and Port

Currently runs on port `8080`. i.e: `https://192.168.1.10:8080`. You can configure it in `~/.config/beets/config.yaml`. Defaults are:
```yaml
beetstream:
  host: 0.0.0.0
  port: 8080
```

## Supported Clients

All clients below are working with this server. By "working", it means one can use most of the features, browse library and most importantly play music!

### Android

- [Subsonic](https://play.google.com/store/apps/details?id=net.sourceforge.subsonic.androidapp) (official app)
- [DSub](https://play.google.com/store/apps/details?id=github.daneren2005.dsub)
- [Audinaut](https://play.google.com/store/apps/details?id=net.nullsum.audinaut)
- [Ultrasonic](https://play.google.com/store/apps/details?id=org.moire.ultrasonic)
- [GoSONIC](https://play.google.com/store/apps/details?id=com.readysteadygosoftware.gosonic)
- [Subtracks](https://play.google.com/store/apps/details?id=com.subtracks)
- [Music Stash](https://play.google.com/store/apps/details?id=com.ghenry22.mymusicstash)
- [substreamer](https://play.google.com/store/apps/details?id=com.ghenry22.substream2)

### Desktop

- [Clementine](https://www.clementine-player.org)

### Web

- [Jamstash](http://jamstash.com) ([Chrome App](https://chrome.google.com/webstore/detail/jamstash/jccdpflnecheidefpofmlblgebobbloc))
- [SubFire](http://subfireplayer.net)

_Currently supports a subset of API v1.16.1, avaiable as Json, Jsonp and XML._

## Contributing

There is still some [missing endpoints](missing-endpoints.md) and `TODO` in the code.
Feel free to create some PR!
