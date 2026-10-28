#!/usr/bin/env bash
# Alternative locations are accepted only after the recipe's SHA-256 matches.
termux_source_mirrors() {
	local url="$1" checksum="$2" filename path
	[[ "$checksum" =~ ^[[:xdigit:]]{64}$ ]] || return 0
	[[ "$url" == https://* && "$url" != *\?* && "$url" != *\#* ]] || return 0
	filename="${url##*/}"
	[[ -n "$filename" ]] || return 0
	case "$url" in
		https://ftp.gnu.org/gnu/*|https://ftpmirror.gnu.org/*|https://mirrors.kernel.org/gnu/*)
			path="${url#https://*/}"; path="${path#gnu/}"
			printf '%s\n' "https://mirrors.kernel.org/gnu/$path" \
				"https://ftp.osuosl.org/pub/gnu/$path" "https://ftp.fau.de/gnu/$path"
			;;
		https://www.kernel.org/pub/*|https://cdn.kernel.org/pub/*|https://mirrors.edge.kernel.org/pub/*)
			path="${url#https://*/}"
			printf '%s\n' "https://cdn.kernel.org/$path" "https://mirrors.kernel.org/$path"
			;;
		https://pkgconfig.freedesktop.org/releases/*)
			printf '%s\n' "https://distfiles.macports.org/pkgconfig/$filename"
			;;
		https://archive.docbook.org/*|https://docbook.org/*|https://www.docbook.org/*)
			printf '%s\n' "https://distfiles.macports.org/docbook-xml/$filename"
			;;
		https://downloads.sourceforge.net/project/tcl/*)
			printf '%s\n' "https://distfiles.macports.org/tcl/$filename"
			;;
	esac
	printf '%s\n' "https://cdn.NetBSD.org/pub/pkgsrc/distfiles/$filename"
}
