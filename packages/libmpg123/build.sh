TERMUX_PKG_HOMEPAGE=https://mpg123.org/
TERMUX_PKG_DESCRIPTION="Fast console MPEG Audio Player and decoder library"
TERMUX_PKG_LICENSE="LGPL-2.1"
TERMUX_PKG_MAINTAINER="@termux"
TERMUX_PKG_VERSION="1.33.7"
# Flaky https://mpg123.org/download/mpg123-${TERMUX_PKG_VERSION}.tar.bz2
TERMUX_PKG_SRCURL=https://downloads.sourceforge.net/sourceforge/mpg123/mpg123-${TERMUX_PKG_VERSION}.tar.bz2
TERMUX_PKG_SHA256=31d0e35a4ca567ec9b5ebda6c3062bb4435d6d3eacd6ef0d95cadd7854dc03ee
TERMUX_PKG_AUTO_UPDATE=true
TERMUX_PKG_REVISION=1
# No PulseAudio output module. It would make libmpg123 depend on pulseaudio, which depends
# on libsndfile, which depends on libmpg123: a cycle that cannot be bootstrapped from source
# (upstream sidesteps it by downloading prebuilt dependencies, which a renamed prefix cannot).
TERMUX_PKG_EXTRA_CONFIGURE_ARGS="--with-audio=dummy --with-default-audio=dummy"
TERMUX_PKG_BREAKS="mpg123 (<< 1.33.1-1)"
TERMUX_PKG_REPLACES="mpg123 (<< 1.33.1-1)"
