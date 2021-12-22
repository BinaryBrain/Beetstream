# Beets-SubSonic-API

Beets.io plugin that expose SubSonic API endpoints.

## Motivation

_TODO_

## Install & Run

Requires Python 3.8 or newer.

Install with:

```
$ pip install -r requirements.txt
```

Run with:

```
$ beet subsonic
```

## Clients Configuration

### Authentication

There is currently no security whatsoever. You can put whatever user and password you want in your favorite app.

### Server and Port

Currently runs on port `8080`. i.e: `https://192.168.1.10:8080`

## Supported Clients

All clients below are working with this server. By "working", it means one can use most of the features, browse library and most importantly play music!

### Android

- [Subsonic](https://play.google.com/store/apps/details?id=net.sourceforge.subsonic.androidapp) (official app)
- [Audinaut](https://play.google.com/store/apps/details?id=net.nullsum.audinaut)
- [Ultrasonic](https://play.google.com/store/apps/details?id=org.moire.ultrasonic)
- [Subtracks](https://play.google.com/store/apps/details?id=com.subtracks) (currently very slow)
- [Music Stash](https://play.google.com/store/apps/details?id=com.ghenry22.mymusicstash) (currently very slow)
- [substreamer](https://play.google.com/store/apps/details?id=com.ghenry22.substream2) (currently very slow and seems to play random songs)

Some apps are slow because pagination is not properly handled yet.

### Web

- [Jamstash](http://jamstash.com) ([Chrome App](https://chrome.google.com/webstore/detail/jamstash/jccdpflnecheidefpofmlblgebobbloc))
- [SubFire](http://subfireplayer.net)

_Currently supports a subset of API v1.16.1, avaiable as Json, Jsonp and XML._
