# Reproducible build standard

Release builds use a fixed `SOURCE_DATE_EPOCH`, sorted inventories, normalised archive timestamps and SHA-256 manifests. The release builder validates data contracts and the conductor before copying approved inputs. Stable release versions are blocked unless their required gate has an accepted decision.

A clean-build evidence pack must record the source revision, Python version, dependency lock or resolved package inventory, command line, source date epoch, generated file inventory, archive checksum and comparison with an independently repeated build. The v1.0 acceptance target is byte-identical archives from two clean environments or a documented, independently reviewed explanation for any platform-specific divergence.
