# getpocket2notion

[![CodeFactor](https://www.codefactor.io/repository/github/davethe/getpocket2notion/badge)](https://www.codefactor.io/repository/github/davethe/getpocket2notion)


# What is getpocket2notion?

getpocket2notion helps you organize your links from getpocket.com to notion.so.

getpocket2notion code is entirely open source.

![logo](https://backdropcms.org/files/inline-images/logo.png)

# How to use this image
- [create a getpocket app](https://getpocket.com/developer/docs/authentication)

The basic pattern for starting a `getpocket2notion` instance is:

```console
$ docker run --name getpocket2notion getpocket2notion:latest
```

The following environment variables are also honored for configuring your getpocket2notion instance:

- `-e TOKEN_V2=...` (Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so)
- `-e NOTION_LINK=...` (the notion page link with a collection view)
- `-e API_KEY=...` (apikey of getpocket app)
- `-e USR=...` (getpocket username)
- `-e PSW=...` (getpocket password)
- `-e LOG_TYPE=...` (defaults to "prod", if you run on GCP use "gcp")


# Library

- [Notion-py](https://github.com/jamalex/notion-py)
- [Selenium](https://github.com/SeleniumHQ/selenium)
- [add rows logic into notion](https://github.com/bkiac/wickie/blob/master/wickie/notionutils/add.py)

# License

View [license information](https://www.drupal.org/licensing/faq) for the software contained in this image.

# Supported Docker versions

This image is officially supported on Docker version 1.10.3.

Support for older versions (down to 1.6) is provided on a best-effort basis.

Please see [the Docker installation documentation](https://docs.docker.com/installation/) for details on how to upgrade your Docker daemon.

# User Feedback

## Documentation

 > @todo: link to github?

## Issues

 > @todo: link to github?

## Contributing

 >  @todo: link to github?
